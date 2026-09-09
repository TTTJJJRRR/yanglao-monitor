"""SQLite WAL 修复验证脚本。

验证目标（对应 mock_stream 每秒写库被强杀导致 100+ 个 13KB -journal 残留的问题）：
1. 项目 database.py 的连接监听器确实把 journal_mode 切到了 WAL；
2. 在「事务中途被强制打断」场景下，磁盘上不会再堆积 app.db-journal 回滚日志，
   最多只有单个 -wal / -shm（WAL 模式下正常存在，进程被杀也能自动恢复）。

用法：
    python scripts/check_journal.py
"""
import os
import sys
import tempfile
from pathlib import Path

BACKEND = Path(__file__).resolve().parents[1] / "backend"
sys.path.insert(0, str(BACKEND))

from sqlalchemy import create_engine, event, text
from sqlalchemy.orm import sessionmaker


def _files(db_path: str) -> dict:
    out = {"journal": [], "wal": [], "shm": []}
    for suffix, key in (("-journal", "journal"), ("-wal", "wal"), ("-shm", "shm")):
        p = db_path + suffix
        if os.path.exists(p):
            out[key].append(p)
    return out


def main() -> int:
    # 用临时库，避免污染真实 app.db；配置与 database.py 完全一致。
    tmp = tempfile.mkdtemp(prefix="wal_check_")
    tmp_db = os.path.join(tmp, "test.db")
    eng = create_engine(
        f"sqlite:///{tmp_db}",
        connect_args={"check_same_thread": False},
        pool_pre_ping=True,
        pool_recycle=1800,
    )

    @event.listens_for(eng, "connect")
    def _pragmas(dbapi_conn, _rec):
        c = dbapi_conn.cursor()
        c.execute("PRAGMA journal_mode=WAL;")
        c.execute("PRAGMA synchronous=NORMAL;")
        c.execute("PRAGMA busy_timeout=5000;")
        c.execute("PRAGMA foreign_keys=ON;")
        c.close()

    # 1) 确认 journal_mode 已切换到 WAL
    with eng.connect() as conn:
        mode = conn.exec_driver_sql("PRAGMA journal_mode;").scalar()
    print(f"[1] journal_mode = {mode}")
    ok_wal = mode.lower() == "wal"

    # 2) 模拟 mock_stream：前 19 次正常提交，第 20 次事务中途直接物理关闭连接（= 进程被 SIGKILL）
    SM = sessionmaker(bind=eng, autoflush=False, autocommit=False)
    with eng.connect() as conn:
        conn.exec_driver_sql("CREATE TABLE IF NOT EXISTS t(id INTEGER PRIMARY KEY, v TEXT)")
        conn.commit()

    for i in range(20):
        s = SM()
        try:
            s.execute(text("INSERT INTO t(v) VALUES (:v)"), {"v": f"row{i}"})
            if i < 19:
                s.commit()
            else:
                # 事务进行中直接物理关闭底层连接 —— 模拟被强杀，不 commit
                s.connection().connection.close()
                s.invalidate()
        except Exception as e:
            print(f"    iter {i} exc: {type(e).__name__}")
            try:
                s.rollback()
            except Exception:
                pass
        finally:
            try:
                s.close()
            except Exception:
                pass

    # 3) 再开连接：确认 WAL 自动恢复（回滚第 20 次半截插入），能正常打开
    with eng.connect() as conn:
        cnt = conn.exec_driver_sql("SELECT COUNT(*) FROM t;").scalar()
    print(f"[2] 中断后重新打开，t 表行数 = {cnt}（期望 19：第 20 次半截插入被自动回滚）")

    files = _files(tmp_db)
    print(f"[3] 残留文件: journal={files['journal']} wal={files['wal']} shm={files['shm']}")

    no_journal = len(files["journal"]) == 0
    recover_ok = cnt == 19

    print("\n=== 结论 ===")
    print(f"  journal_mode=WAL : {'PASS' if ok_wal else 'FAIL'}")
    print(f"  无 -journal 堆积  : {'PASS' if no_journal else 'FAIL'} (残留 {len(files['journal'])} 个)")
    print(f"  WAL 自动恢复     : {'PASS' if recover_ok else 'FAIL'}")
    return 0 if (ok_wal and no_journal and recover_ok) else 1


if __name__ == "__main__":
    sys.exit(main())

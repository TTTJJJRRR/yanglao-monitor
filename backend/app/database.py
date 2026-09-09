from sqlalchemy import create_engine, event
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from .config import get_settings

settings = get_settings()
engine = create_engine(
    settings.database_url,
    connect_args={"check_same_thread": False},
    # 连接池健康检查：自动回收失效连接，避免 mock_stream 后台线程长期持有时
    # 遇到数据库被外部工具打开/重建后拿到坏连接。
    pool_pre_ping=True,
    pool_recycle=1800,
)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


@event.listens_for(engine, "connect")
def _set_sqlite_pragmas(dbapi_conn, conn_record) -> None:
    """每个新连接都施加 SQLite 性能/安全 PRAGMA。

    关键：journal_mode=WAL 彻底消除 DELETE 模式下「每事务一个 -journal 回滚日志」
    的堆积问题。WAL 改为单一 -wal 追加文件，进程被 SIGKILL/Ctrl+C 强杀后，
    下次打开数据库会自动从 -wal 做恢复（回滚未完成事务），不会留下 100+ 个残留 journal。
    - synchronous=NORMAL：WAL 模式下已足够安全，且大幅降低 fsync 次数（写吞吐更高）。
    - busy_timeout=5000：多写者（uvicorn + 后台 mock_stream）并发时等待而非立即报错 SQLITE_BUSY。
    - foreign_keys=ON：启用外键约束（SQLite 默认关闭）。
    """
    cursor = dbapi_conn.cursor()
    cursor.execute("PRAGMA journal_mode=WAL;")
    cursor.execute("PRAGMA synchronous=NORMAL;")
    cursor.execute("PRAGMA busy_timeout=5000;")
    cursor.execute("PRAGMA foreign_keys=ON;")
    cursor.close()


class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

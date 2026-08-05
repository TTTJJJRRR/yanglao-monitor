# M0 收尾 + MMFi 验证包接入（交给 Cursor 执行）

> 使用方式：打开 Cursor → 打开项目根目录 `C:\Users\tttt\WorkBuddy\大创-真正版本` → 按 `Ctrl+L` → 把本文件全文粘贴进对话框 → 让 Cursor 执行。
> 委托方：滕家瑞（指挥）+ 黄敬城（副手/前端/测试）｜阶段：M0 收尾（2026-08）
> 验收方：滕家瑞 / 黄敬城（生成后必须人工验收，不要直接信任 AI 产出）

---

## 0. 背景与前置事实（给 Cursor 的上下文）

这是一个**智能康养监测系统**（江南大学大创项目）：毫米波雷达 **IWR6843AOP**（60GHz AoP 3T4R）+ 摄像头融合，非接触监测老人呼吸/心率/跌倒/行为/情绪，秒级预警，**雷达不录视频、不拍画面**。

**M0 脚手架已经搭好**（不要从零重建）：
- 后端：`backend/app/` 下已有 `main.py`（FastAPI app）、`auth.py`（JWT 三角色）、`mock.py`（模拟数据发生器）、`schemas.py`（pydantic 模型）、`ws.py`（WebSocket `/ws/stream`）、`routers/`（auth/alerts/behaviors/vitals）、`config.py`、`database.py`、`models.py`。演示账号 `admin/admin123` 可登录。
- 前端：`frontend/src/` 下已有 `App.tsx`、`api/client.ts`、`api/ws.ts`、`types.ts`、`styles.css`、`main.tsx`，Vite 启动正常，大屏能显示 WebSocket 模拟帧。

**本次目标不是重写，而是两件事**：
1. **接入朋友给的 MMFi 验证包**，把"读取真实样例数据 → 推送前端"这条管道跑通（作为可切换数据源，默认仍走 mock）。
2. **完成 M0 收尾**：契约对齐校验、README 启动说明、验收清单逐项核对、分支提交。

---

## 1. 朋友的 MMFi 验证包（数据源）

原始位置（微信目录，路径含中文，不要硬编码进代码）：
`C:\Users\tttt\Documents\WeChat Files\wxid_9abiwmjxfa1t22\FileStorage\File\2026-08\A01\A01\`

包含关键文件：
- `radar_sample.jsonl` —— 雷达样例，每行一个 JSON，**字段与本项目 §4 数据契约一致**（timestamp_ms / device_id / vital{breath_rate,heart_rate,chest_displacement_mm,motion_flag} / behavior{action,action_confidence} / alert{level,type,message,suggested_action}）。注意：心率/呼吸率当前为 `null`（MMFi 无生命体征真值），解析时要容错 null。
- `meta_project.json` —— 7 模态各 297 帧、fps=20、合成时间戳；`privacy_status: do not upload raw RGB to cloud`（隐私红线，严格遵守）。
- `labels_project.json` —— 动作标签占位，`project_action` 当前为 `null`（尚未映射到本项目 6 类动作）。
- `collection_parameters.md` —— 空白采集参数模板（真实值待周震宇填）。
- `mmwave/`（297 帧原始雷达）、`skeleton/`、`ground_truth.npy`（297,17,3 人体骨骼）、`rgb/`（占位，无真实画面）。

---

## 2. 你必须执行的任务（增量，不破坏现有结构）

### 2.1 把验证包纳入项目统一管理
- 在 `data/` 下新建 `data/mmfi-sample/`，将 `radar_sample.jsonl`、`meta_project.json`、`labels_project.json`、`collection_parameters.md`、`README_project_delivery.md` 复制进去（`mmwave/`、`skeleton/`、`ground_truth.npy`、`rgb/` 暂不复制，避免体积膨胀；如需可后续补）。
- 写一个简短 `data/mmfi-sample/README.md`，说明来源、字段含义、`null` 字段含义、以及"非最终数据集，仅流程验证"的定位。

### 2.2 后端：新增「数据源切换」能力（核心任务）
- 在 `backend/app/` 下新增 `data_source.py`（或扩展 `mock.py`）：实现一个可切换的数据源。
  - 默认模式 `mock`：复用现有 `mock.py` 的 `generate_frame()`。
  - 新增模式 `mmfi`：读取 `data/mmfi-sample/radar_sample.jsonl`，逐行解析为符合 §4 契约的帧，**循环推送**（文件 297 行播完循环）。
  - 解析必须**容错**：`breath_rate`/`heart_rate` 为 `null` 时不报错（前端显示"—"而非崩溃）；`action` 缺失时回退 `normal_activity`。
- WebSocket 端点 `/ws/stream` 增加一个可选 query 参数 `?source=mock|mmfi`（默认 mock），切换推送源。**不要改动现有 mock 默认行为**，确保现有演示不受影响。
- 提供一个只读接口 `GET /api/data-source` 返回当前数据源与可用选项，方便前端/调试。

### 2.3 前端：确认大屏能渲染 MMFi 结构（最小改动）
- 检查 `frontend/src/types.ts` 与 `api/ws.ts`，确认能正确接收 §4 契约字段。若 `vital.breath_rate`/`heart_rate` 为 `null` 时大屏不崩（显示"—"或占位）。
- 确认 `behavior.action` 六个取值（walking/falling/sitting_still/standing_up/lying/normal_activity）的展示逻辑完好，跌倒（falling）红色高亮正常。
- 若现有大屏已能渲染 mock 帧，基本无需改；**只在确有类型不一致时最小化修正**，不要重写组件。

### 2.4 契约对齐校验（红线）
- 读取 `docs/大创项目统筹需求文档.md` §6 数据契约，与 `backend/app/schemas.py` 字段逐一比对。
- 若发现偏差（如字段名、取值集合不一致），**最小化修正** `schemas.py` 使其与契约完全一致；前端 `types.ts` 同步。不要改契约核心字段（`timestamp_ms`/`device_id`/`vital`/`behavior`/`alert`）。

### 2.5 M0 收尾文档
- 若 `backend/README.md` / `frontend/README.md` 缺失或不完整，补全启动步骤：
  - 后端：用 venv 路径 `C:/Users/tttt/.workbuddy/binaries/python/envs/backend313/Scripts/python.exe -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload`（若 venv 不存在，先 `python -m venv` + `pip install -r requirements.txt`，清华源）。
  - 前端：`npm install`（若沙箱 npm 报 shim 错误，用 `NODE_OPTIONS="" npm install` 绕过），然后 `npm run dev`，默认后端 `http://localhost:8000`。
- 在 README 注明三个演示账号（family/admin/elder，密码统一 `demo1234` 或现有 `admin/admin123`，以代码实际为准，写清楚）。

---

## 3. 验收标准（滕/黄 逐项核对）

- [ ] `data/mmfi-sample/` 已建立，`radar_sample.jsonl` 等已复制，README 说明到位。
- [ ] 后端起服务：`GET /api/health` 返回 ok；`GET /api/data-source` 返回 `{source:"mock"}`。
- [ ] WebSocket 默认（mock）行为不变：大屏实时滚动、手动 `POST /api/simulate/fall` 出红色跌倒预警。
- [ ] WebSocket `?source=mmfi` 时：大屏能渲染 radar_sample.jsonl 的帧；`null` 心率/呼吸显示"—"不崩；循环播放 297 帧无异常。
- [ ] `backend/app/schemas.py` 与 docs §6 契约字段一致；前端 `types.ts` 对齐。
- [ ] `backend/README.md` + `frontend/README.md` 启动步骤可复现（队友按文档能起）。
- [ ] 代码提交到分支 `dev-huang`，提 PR 给滕 review，**不直接推 main**。

---

## 4. 约束与红线（务必遵守）

- **不写真实算法**：雷达信号处理、跌倒检测模型、融合逻辑一律不碰。本次只做"数据源切换 + 管道跑通 + 收尾"。
- **不破坏现有结构**：M0 脚手架已存在，所有改动是**增量**。不确定现有代码意图时，先问滕，不要大删大改。
- **隐私红线**：任何地方不得出现"保存视频/图片/上传 rgb"的逻辑。`meta_project.json` 已声明 `do not upload raw RGB to cloud`，严格遵守。
- **不要硬编码微信目录路径**：数据源路径用项目内 `data/mmfi-sample/`，便于队友复现。
- **代码可读性**：关键函数写注释，复杂处加说明，方便队友（尤其标注/数据同学）接手。
- 生成完成后**输出一份改动清单**（新增/修改了哪些文件、怎么启动、怎么切换数据源），方便验收。

---

> 完成后请明确告知：mock 与 mmfi 两种数据源是否都能在前端大屏正常展示、null 字段是否容错、验收清单逐项结果。验收不过打回。

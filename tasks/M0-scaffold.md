# M0 脚手架委托任务（交给 Cursor 执行）

> 使用方式：打开 Cursor → 打开项目根目录 `C:\Users\tttt\WorkBuddy\大创-真正版本` → 按 `Ctrl+L` → 把本文件全文粘贴进对话框 → 让 Cursor 生成代码。
> 委托方：滕家瑞（指挥）+ 黄敬城（副手/前端/测试）｜阶段：M0（2026-08，2–3 周）
> 验收方：滕家瑞 / 黄敬城（生成后必须人工验收，不要直接信任 AI 产出）
>
> ⚠️ **状态更新（2026-08-05）**：M0 脚手架已由既有代码完成（见 `backend/app/*`、`frontend/src/*`，之前已修通过登录与启动）。本文件作为原始委托存档保留。**下一步任务见 `tasks/M0-cursor-mmfi-integrate.md`**（接入朋友给的 MMFi 验证包 + 完成 M0 收尾验收）。

---

## 0. 项目背景（给 Cursor 的上下文）

这是一个**智能康养监测系统**（江南大学大创项目）：
- 硬件：毫米波雷达 **IWR6843AOP**（60GHz AoP 3T4R）+ 摄像头。
- 目标：非接触监测老人呼吸/心率/跌倒/行为/情绪，秒级预警，**雷达不录视频、不拍画面**。
- 当前阶段 M0：只搭**脚手架空壳 + 前端大屏 + 冻结数据契约**，所有感知数据用**模拟（mock）**驱动，真实雷达未到货。
- 已有仓库结构：`backend/`（Python/FastAPI 方向）、`frontend/`（React 方向）、`docs/`（需求文档）、`data/`。

## 1. 本次目标（M0 必须产出）

1. **后端空壳**（FastAPI）：能启动、能登录（JWT 三角色）、能通过 WebSocket 实时推送模拟数据。
2. **前端大屏**（React）：实时显示体征曲线、行为标签、预警卡片，数据来自后端模拟流。
3. **数据契约 v1 冻结**：前后端共用一套 JSON 结构（见 §4），写进 `backend/` 的 schema 文件和 `docs/` 说明。
4. **模拟数据发生器** `mock.py`：周期性产生符合契约的体征/行为/预警数据，让大屏"活"起来。

> ⚠️ **范围限制（Non-goals）**：M0 **不写任何真实算法**（不写雷达信号处理、不写跌倒检测模型、不写融合）。只做空壳 + 模拟 + 大屏骨架。真实算法留到 M1/M2。

## 2. 后端任务（FastAPI 空壳）

技术栈：Python 3.11+、FastAPI、uvicorn、python-jose（JWT）、passlib（密码哈希）、websockets / FastAPI WebSocket、pydantic。

必须实现：
- `main.py`：FastAPI app，挂载路由。
- `auth.py`：JWT 登录，三角色 `family`（家属）/ `admin`（管理员/护理员）/ `elder`（老人）。提供 `/api/login` 接口，返回 token。预置 3 个演示账号（各角色一个，密码统一 `demo1234`，明文注释提醒"仅演示"）。
- `schemas.py`：pydantic 模型，**按 §4 契约定义** `VitalSign`、`Behavior`、`Alert`、`SimFrame` 等。
- `mock.py`：模拟数据发生器。提供函数 `generate_frame()` 返回符合 §4 的 `SimFrame`（随机但合理的呼吸/心率、随机行为、偶发跌倒预警）。可用 `asyncio` 定时推送。
- `ws.py` 或 `routers/ws.py`：WebSocket 端点 `/ws/stream`，连接后每 ~1s 推一帧模拟数据（用 mock.py）。需简单校验 token（query 参数或 header）。
- `routers/simulate.py`：`POST /api/simulate/fall` 手动触发一次"跌倒预警"帧（方便演示），`GET /api/health` 健康检查。
- `requirements.txt`：列出依赖。
- 根目录 `README` 或 `backend/README.md`：写清楚 `pip install -r requirements.txt` → `uvicorn main:app --reload --port 8000` 启动步骤。

数据流向：mock.py 生成 → 既可通过 REST 拉取，也可经 WebSocket 实时推 → 前端订阅。

## 3. 前端任务（React 大屏）

技术栈：React 18+、Vite、TypeScript（或 JS 若现有脚手架是 JS）、axios、WebSocket 原生、图表用 recharts 或 echarts（二选一，写明选择）。

必须实现（页面 `frontscreen` / `Dashboard`）：
- 登录页：输入账号密码 → 调 `/api/login` → 存 token。
- 大屏页（登录后）：
  - **体征卡片**：实时呼吸率、心率数字 + 折线图（随时间滚动，数据来自 WebSocket）。
  - **行为标签**：当前行为（walking/falling/...）大字显示，跌倒时红色高亮。
  - **预警列表**：收到预警帧时插入列表（时间、类型、建议动作），跌倒预警置顶红色。
  - **连接状态**：显示 WebSocket 已连/断线。
- 用 WebSocket 订阅 `/ws/stream`，token 通过 query 传递；断线自动重连（简单指数退避即可）。
- 整体 UI 走"监护大屏"风格：深色背景、大字号、高对比，适老/适值守场景。
- `frontend/README.md`：写清楚 `npm install` → `npm run dev` 启动步骤、默认后端地址（http://localhost:8000，可用 .env 配置）。

## 4. 数据契约 v1（前后端共用，必须严格遵守）

后端 `schemas.py` 与前端类型定义都按此实现：

```json
{
  "timestamp_ms": 1690000000000,
  "device_id": "RADAR_01",
  "vital": {
    "breath_rate": 16.5,
    "heart_rate": 72.0,
    "chest_displacement_mm": 3.2,
    "motion_flag": false
  },
  "behavior": {
    "action": "walking",
    "action_confidence": 0.91
  },
  "alert": {
    "level": "none",
    "type": null,
    "message": "",
    "suggested_action": ""
  }
}
```

- `action` 取值固定：`walking, falling, sitting_still, standing_up, lying, normal_activity`
- `alert.level` 取值：`none / info / warning / critical`；`alert.type` 如 `fall / abnormal_vital / none`
- 表情字段暂不接入（M0 不含情绪），契约预留 `emotion` 字段位置但可为 null。
- 把这份契约写进 `docs/大创项目统筹需求文档.md` §6 已有定义，保持完全一致；后端 schema 文件名建议 `backend/schemas.py`。

## 5. 验收标准（滕/黄 生成后逐项核对）

- [ ] 后端 `uvicorn main:app --reload` 能起，无报错；`GET /api/health` 返回 ok。
- [ ] 三个演示账号能登录拿到 JWT；错误密码被拒。
- [ ] 前端 `npm run dev` 能起，登录后能进大屏。
- [ ] 大屏体征曲线实时滚动、行为标签随模拟变化、**手动调 `POST /api/simulate/fall` 后大屏出现红色跌倒预警**。
- [ ] WebSocket 断线后能重连。
- [ ] `backend/schemas.py` 与 §4 契约一致；前端类型与之后端对齐。
- [ ] `requirements.txt` / `package.json` 依赖完整，队友按 README 能复现启动。
- [ ] 代码提交到分支 `dev-teng`（滕）或 `dev-huang`（黄），提 PR 给滕 review，**不直接推 main**。

## 6. 约束与红线

- **不写真实算法**：信号处理、模型推理、融合逻辑一律不碰，M0 只用 mock。
- **雷达隐私**：任何地方都不出现"保存视频/图片"的逻辑；M0 连摄像头都没接，纯模拟。
- **不要重构已有文件结构**：若 `backend/`、`frontend/` 已有文件，在其基础上补全，不要大删大改；不确定先问滕。
- **代码可读性**：关键函数写中文或英文注释，复杂处加说明，方便队友接手。
- 生成完成后**输出一份改动清单**（新增/修改了哪些文件、怎么启动），方便验收。

---

> 完成后请明确告知：能否本地起服务、大屏能否看到实时模拟数据、跌倒预警能否触发。验收不过打回。

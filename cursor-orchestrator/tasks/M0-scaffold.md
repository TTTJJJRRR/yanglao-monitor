# M0 任务 — 系统脚手架（后端空壳 + 前端大屏 + 数据契约）

> 来自 WorkBuddy 指挥家的委托任务（项目阶段：M0 脚手架，对应统筹文档 §5）。
> 请 Cursor AI 代理完成后，将结果写入本项目对应目录，并在末尾按"完成后"要求标记。
>
> ⚠️ 你是这个项目的技术实现者，请用**最强编码模型**认真完成。这是真实大创项目的第一步，
> 后续所有模块都建立在这个骨架上，请保证代码可运行、结构清晰、易于扩展。

---

## 0. 项目背景（必读，理解你在做什么）

这是一个**基于毫米波雷达 + 视频图像融合的智能康养监测系统**（江南大学大创重点项目）。
当前阶段（M0）目标是搭好**可运行的系统骨架**：后端能收数据、前端能看大屏、两端用统一的"数据契约"对接。
**关键约束**：雷达硬件（TI IWR6843ISK）目前未到货，所以 M0/M1 全部用**模拟数据**跑通流程，
真实数据到位后无缝替换（只需替换"数据来源"，不动上层逻辑）。

---

## 1. 技术栈（固定，不要擅自更换）

**后端**
- Python 3.11+ / FastAPI + Uvicorn
- SQLAlchemy 2.0（ORM）+ SQLite（开发库，文件 `backend/app.db`，加入 .gitignore）
- 实时通道：WebSocket（内置 `fastapi.WebSocket`）
- 鉴权：JWT（PyJWT），三角色：`family`（家属）/ `admin`（管理员）/ `elder`（老人）
- 数据处理：Pydantic v2（数据契约校验）

**前端**
- React 18 + Vite + TypeScript
- Tailwind CSS（暗色科技风）
- 图表：Recharts（折线/柱状） + 自绘 Canvas（雷达图/环形图）
- 实时：原生 WebSocket 客户端

**工程**
- 后端根目录：`backend/`
- 前端根目录：`frontend/`
- 根目录 `README.md` 已有，请**追加** M0 的运行说明（不要覆盖已有内容，用追加或在对应小节补充）

---

## 2. 目录结构（请按此创建，不要随意改名）

```
backend/
├── app/
│   ├── main.py              # FastAPI 入口，挂载路由 + WebSocket
│   ├── config.py            # 配置（JWT 密钥、CORS、数据库路径）
│   ├── database.py          # SQLAlchemy engine / SessionLocal / Base
│   ├── models.py            # ORM 表：User(三角色) / VitalRecord / BehaviorEvent / Alert
│   ├── schemas.py           # Pydantic：数据契约（§4）+ 请求/响应模型
│   ├── auth.py              # JWT 生成/校验、当前用户依赖
│   ├── routers/
│   │   ├── auth.py          # 登录(返回JWT) / 当前用户
│   │   ├── vitals.py        # 接收雷达体征（§4.1 JSON）/ 查询历史
│   │   ├── behaviors.py     # 接收行为/情绪事件（§4.2 JSON）/ 查询历史
│   │   └── alerts.py        # 预警查询 / 手动触发测试预警
│   ├── ws.py                # WebSocket 端点：实时推送体征+行为+预警
│   └── mock.py              # 模拟数据生成器（见 §5，雷达未到货用）
├── requirements.txt
└── run.sh                  # 启动脚本：uvicorn app.main:app --reload --port 8000

frontend/
├── index.html
├── package.json
├── vite.config.ts
├── tailwind.config.js
├── postcss.config.js
├── tsconfig.json
└── src/
    ├── main.tsx
    ├── App.tsx              # 布局：顶部标题 + 三栏（体征/行为/预警）
    ├── api/
    │   ├── client.ts        # axios/fetch 封装 + JWT 注入
    │   └── ws.ts            # WebSocket 客户端（连 ws://localhost:8000/ws）
    ├── components/
    │   ├── StatCard.tsx     # 统计卡片
    │   ├── VitalChart.tsx   # 呼吸/心率实时折线（Recharts）
    │   ├── BehaviorList.tsx # 行为/情绪状态列表
    │   ├── AlertPanel.tsx   # 预警列表（红/黄分级）
    │   └── RadarCanvas.tsx  # 用 Canvas 画一个"生命体征雷达图"（示意）
    └── types.ts             # 与后端 §4 契约对应的 TS 类型
```

---

## 3. 数据模型（ORM，`models.py`）

| 表 | 关键字段 | 说明 |
|----|---------|------|
| `User` | id, username, hashed_pwd, role(enum: family/admin/elder), elder_id(可为空) | 三角色鉴权 |
| `VitalRecord` | id, device_id, timestamp_ms, breath_rate, heart_rate, chest_displacement_mm, motion_flag, ahi_index(可空), source(enum: mock/real) | 雷达体征，字段**严格对齐 §4.1** |
| `BehaviorEvent` | id, timestamp_ms, action(enum), emotion(enum), confidence, source | 行为/情绪，字段**严格对齐 §4.2** |
| `Alert` | id, timestamp_ms, level(enum: red/yellow), type, message, is_handled | 预警记录 |

> 所有时间戳用毫秒整数（timestamp_ms），与数据契约一致。

---

## 4. 数据契约（Pydantic `schemas.py`，这是对接的命门，必须严格一致）

### 4.1 雷达体征（接收 POST `/api/vitals`，字段与统筹文档 §6.1 一致）
```json
{
  "timestamp_ms": 1690000000000,
  "device_id": "RADAR_01",
  "breath_rate": 16.5,
  "heart_rate": 72.0,
  "chest_displacement_mm": 3.2,
  "motion_flag": false,
  "ahi_index": null
}
```

### 4.2 行为/情绪事件（接收 POST `/api/behaviors`）
```json
{
  "timestamp_ms": 1690000000000,
  "action": "falling",           // 枚举见下
  "emotion": "calm",             // 枚举见下
  "confidence": 0.93
}
```
- `action` 枚举：`walking, falling, sitting_still, standing_up, lying, normal_activity`（严格等于统筹文档 §6.1）
- `emotion` 枚举：`happy, sad, angry, anxious, calm, surprised`（严格等于人员分工规范 §动作/表情标签集）

### 4.3 WebSocket 实时推送消息（前端 `ws.ts` 按此解析）
推送三种 type：
```json
{"type":"vital",  "data":{...§4.1 字段..., "id":1}}
{"type":"behavior","data":{...§4.2 字段..., "id":1}}
{"type":"alert",  "data":{"id":1,"timestamp_ms":...,"level":"red","type":"fall","message":"检测到跌倒，请立即查看"}}
```

---

## 5. 模拟数据（`backend/app/mock.py` + 后端启动时的后台任务）

雷达未到货，M0 必须有可见数据流动：
- `mock.py` 提供 `generate_vital()`：在合理范围随机（呼吸 12-20、心率 60-100、位移 1-8mm、motion 随机）
- `generate_behavior()`：从 §4.2 枚举随机选，emotion 随机
- `generate_alert()`：偶发（如 action=falling 时必发 red 预警）
- 后端 `main.py` 用 `asyncio` 后台任务**每 1 秒**生成一条 vital + 偶发 behavior/alert，
  经 WebSocket 推给前端（模拟真实设备流）。代码里用 `source="mock"` 标记。
- 提供一个 `POST /api/simulate/fall` 调试接口：手动触发一次跌倒预警，方便演示。

---

## 6. 鉴权（`auth.py`）

- `POST /api/auth/login`：接收 `{username, password}`，校验后返回 `{access_token, token_type:"bearer", role}`
- 内置一个 seed 用户（启动时在库里建好）：`admin / admin123`（role=admin），方便登录演示
- WebSocket 连接时从 query 参数 `?token=xxx` 取 JWT 校验，无效则拒连
- 受保护路由用 `Depends(get_current_user)`

---

## 7. 前端大屏（`App.tsx` + 组件）

要求（暗色科技风，蓝/青配色，卡片带阴影，响应式）：
- **顶部**：系统标题「智能康养监测系统 · 实时大屏」+ 连接状态指示灯（WebSocket 连上变绿）
- **左栏 体征**：呼吸率/心率两个 StatCard（实时数值）+ VitalChart 实时折线（最近 30 点）
- **中栏 行为/情绪**：BehaviorList 显示最新行为 + 情绪（带 emoji 或色块）+ RadarCanvas 生命体征雷达图（用 Canvas 画呼吸/心率/位移三维示意）
- **右栏 预警**：AlertPanel 实时列表，red 红色高亮、yellow 黄色，显示时间+类型+消息
- 启动后自动连 `ws://localhost:8000/ws?token=<登录拿到的JWT>`；断线自动重连（3秒）
- 提供简单登录弹窗（输入 admin/admin123 拿 token）

> 注意：前端**不硬编码 token**，从登录接口获取；先登录再连 WS。
> 图表数据来自 WebSocket 推送，不要前端自己造假数据（后端 mock 已提供数据源）。

---

## 8. 验收标准（Cursor 完成后自测，我方会复核）

1. `cd backend && pip install -r requirements.txt && ./run.sh` 能启动，访问 `http://localhost:8000/docs` 看到 Swagger
2. 用 Swagger 或 curl 调 `/api/auth/login` 拿到 token；用 token 调 `/api/vitals` POST 一条 §4.1 数据能 200
3. `cd frontend && npm install && npm run dev` 能起；浏览器打开后登录 → 大屏实时刷新（体征曲线动、行为/情绪更新、预警偶发弹出）
4. 调 `POST /api/simulate/fall` 后，前端右栏立刻出现 red 跌倒预警
5. 用 `pytest` 或至少 `python -c` 验证 Pydantic 契约能正确校验 §4.1/§4.2 的非法字段（如 action 不在枚举）会报错
6. 代码无明显语法错误，结构清晰，关键函数有简短注释

---

## 9. 完成后

1. 在 `backend/requirements.txt` 和 `frontend/package.json` 写清依赖
2. 在根目录 `README.md` **追加**「M0 运行说明」小节（启动后端、启动前端、登录账号、演示跌倒预警的步骤）
3. 在 `cursor-orchestrator/results/` 下写一个 `M0-scaffold-report.md`，包含：
   - 实际创建的文件清单
   - 如何运行（命令）
   - 已知限制（如 mock 数据、未接真实硬件）
   - 给滕家瑞的下一步建议（M1 接真实雷达时需改哪几个文件）
4. 在 `M0-scaffold-report.md` 末尾加一行：`<!-- M0 脚手架任务完成，由 Cursor AI 执行 -->`

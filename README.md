# 智能康养监测系统（yanglao-monitor）

> 基于**毫米波雷达 + 视频图像融合**的智能康养监测系统研发
> 江南大学 · 人工智能与计算机学院（大创重点项目）
> 周期：2026.03 – 2027.03

## 项目简介

一套面向智慧养老的**多模态健康主动预警系统**：毫米波雷达（**TI IWR6843AOP**，60GHz AoP 3T4R）非接触式
监测呼吸 / 心率 / 睡眠呼吸暂停，视频图像（MediaPipe 端侧骨骼化）识别跌倒 / 行为 / 情绪，二者在边缘端融合后做主动预警，
关键预警**始终送达、不可静音/关闭**（家属端无「免打扰」入口）。数据上云做长期趋势分析与模型迭代。

## 团队与分工

| 成员 | 角色 | 负责 |
|------|------|------|
| 陈意豪 | 队长 | 文档 / 论文 / 专利 / 对外 |
| 滕家瑞（teng-jiarui_TJR） | 技术总负责 | 架构 / 前后端 / 融合算法 / 代码闸门 |
| 黄敬城 | 副手 | 前后端编码 / 测试验证 |
| 周震宇 | 数据采集 | 雷达 + 视频 硬件与原始数据 |
| 万砚佶 | 标注 + 文档协助 | 数据标注 / 论文专利初稿 |

分工与数据交付格式见 [`docs/人员分工与数据交付规范.md`](docs/人员分工与数据交付规范.md)；
架构与流程总览见 [`docs/大创项目统筹需求文档.md`](docs/大创项目统筹需求文档.md)。

## 仓库结构

```
yanglao-monitor/
├── docs/                 # 需求/分工/采集规程/前沿调研
├── backend/              # FastAPI 后端（JWT 三角色 + WS + 数据源切换）
├── frontend/             # React 机构管理端（正式前端，暖苔绿 8 屏）
├── edge/                 # 边缘端（雷达 OOB 采集 / MediaPipe 视觉节点）
├── fusion/               # 融合算法（特征级+决策级，核心创新）
├── data/                 # 数据（大文件走 LFS/网盘，仅留说明与示例）
│   ├── radar/            # 周震宇：原始雷达点云 .bin（待采）
│   ├── mmfi-sample/      # MMFi 公开验证样例
│   └── replay/           # 同学采集的坐/走回放数据（jsonl，仅演示）
├── tests/                # 测试（黄敬城主导）
├── scripts/              # 工具脚本（数据转换/解析）
└── cursor-orchestrator/  # WorkBuddy→Cursor 文件接力工具（非交付源码）
```

## 分支策略

- `main`：稳定版，仅滕家瑞可合并
- `feature/*`：功能分支，PR → 滕 review 合并
- `data/radar`：周震宇  `data/label`：万砚佶  `docs`：陈/万

## 技术栈

- 后端：FastAPI + SQLAlchemy + SQLite + JWT（三角色 family/admin/elder）
- 前端：React + Vite + TypeScript + Tailwind + Recharts
- 实时：WebSocket（`/ws/stream`）
- 感知：TI IWR6843AOP OOB 点云 + 生命体征（DFT 周期图 + EEMD 双估计器投票）
- 视觉：MediaPipe Pose（端侧骨骼化，画面不上云）
- 边缘AI：mmWave 行为 CNN（自训，见进度说明）

## 开发阶段

| 阶段 | 时间 | 目标 | 状态 |
|------|------|------|------|
| M0 脚手架 | 8月 | 后端空壳 + 前端 + 数据契约 | ✅ 完成 |
| M1 感知打通 | 9月 | 雷达(模拟)→体征显示；视频→跌倒 | 🔄 进行中（生命体征/视觉几何已真集成，雷达待采原始点云） |
| M2 边缘AI | 9-10月 | 行为/情绪识别、雷达信号分离 | ⏳ 待原始数据 |
| M3 融合原型 | 10-11月 | **最小融合原型（核心创新）** | ⏳ 待定 |
| M4 数据集 | 10-12月 | 真实采集+标注，建成数据集 | ⏳ 待采集 |
| M5 集成部署 | 12-1月 | 边缘+云端联调、Docker、试点 | 🔄 代码已就位，未部署 |
| M6 成果 | 2-3月 | 论文/专利/研究报告/答辩PPT | ⏳ 待定 |

---

## 当前进度（进行到哪一步）

> 诚实基线：下方明确区分「已真集成」vs「演示/占位」，不把 mock 当成果。

### ✅ 已真集成（真实算法 / 真实管道）

1. **生命体征双估计器投票（Wave 0）**
   - DFT 周期图 + EEMD（集合经验模态分解）两个独立估计器对同一相位信号交叉验证；
   - 一致 → 提可信取均值；分歧/缺检/低质量 → 降可信 + `needs_review` 转盯防（宁误报不漏报）；
   - 已做**窗口长度感知**（≤12s 短窗只比对心率，呼吸以 DFT 为准，避免 5s 雷达窗误报）。
   - 状态：**算法真实、合成信号验证通过**；真数据对照待原始雷达帧。

2. **视觉跌倒几何检测**
   - MediaPipe Pose 33 关键点 → 躯干夹角 + 质心高度比 → `fall_score`；
   - `FallDetector` 3 帧滑窗：连续 ≥3 帧高分才报红，单帧尖峰仅黄色盯防；
   - 状态：**纯几何真实、无训练**；坐/走负样本验证不误报（站 0.0 / 走 0.027 / 坐 0.0，跌倒正对照 0.85）。

3. **8 类安全动作枚举（锁定）**
   - `walking / standing / sitting_still / standing_up / crouching / lying / lying_floor / falling` + `normal_activity`（未知兜底）；
   - 老人安全视角：易混淆动作（弯腰/蹲下）单独成类，融合层对低置信/未知**升级盯防**。

4. **融合安全翻转**：低置信/易混淆姿态/未知 → `needs_review` + `watch_reason`，绝不静默当安全。

5. **设备离线监测**：`device_offline` → `critical` 红色常驻横幅，文案「关键预警始终送达，不可静音/关闭」，仅服务端 `device_online` 恢复时清除（**零关闭入口**）。

6. **正式前端（机构管理端）**
   - 暖苔绿 8 屏：登录 / 总览 / 床位看板 / 床位详情 / 预警中心 / 健康趋势 / 设备管理 / 老人档案；
   - 真实管道：登录 `/api/auth/login`、预警 `/api/alerts`、WS 实时体征/行为/预警/设备离线；
   - 入口：`frontend/src/InstitutionApp.tsx`（旧「实时大屏」已删除）。

### ⚠️ 演示 / 占位（诚实标注，勿当成果）

- **床位 / 老人 / 设备 / 趋势** 4 类实体后端 API 尚未建，前端用 `frontend/src/data/demo.ts` 静态填充（排期 M3–M5）。
- **预警「标记已处理」** 后端无写接口，前端仅本地生效（刷新还原）。
- **雷达行为 CNN**：已训练出 `weights.pt`（真实 torch 权重），但**仅单类 A01 样本，实际不能区分多类**，`accuracy remains pending`，未编造准确率。
- **数据源 `mock`（默认）**：后端生成合成生命体征/预警，用于联调演示。

### 📦 数据现状

- 雷达 **IWR6843AOP 已到手（2026-08-07）**，可物理采数据；**尚未采原始点云**。
- 同学已给「坐 / 走」两动作的**回放数据**（`data/replay/`：`.jsonl` 成品体征 + 同步 `.mp4`）——非原始雷达帧，仅能演示前端管道，跑不了真实生命体征/行为识别。
- MMFi 公开集（`data/mmfi-sample/`）降为校验/补充集。

---

## 接下来怎么做（路线图）

### 短期（当前主线）
1. **采原始雷达点云**（周震宇）：用 `edge/capture_oob.py` 从 IWR6843AOP 的 DATA UART 采 OOB 点云 `.bin`，
   覆盖 **8 类动作含跌倒**，按 `data/radar/E<环境>/S<受试者>/A<class>/mmwave/frame*.bin` 归档。
   执行清单见 [`docs/M1-周震宇原始雷达采集清单.md`](docs/M1-周震宇原始雷达采集清单.md)。
2. **接通真实雷达帧**：`RadarPhaseProvider` 读原始点云 → 相位 → DFT/EEMD 双估计器，把线上系统从 `mock` 切到真实生命体征。

### 中期（数据到位后）
3. **重训行为 CNN**：用多类（含跌倒）真实点云重训，替换单类 `weights.pt`，让模型真正区分 8 类。
4. **补 4 类实体 API**：床位 / 老人 / 设备 / 趋势 的后端接口，替换前端 `demo.ts`。
5. **补预警「标记已处理」写接口**。
6. **M3 融合原型**：雷达行为 + 生命体征 + 视觉跌倒 在边缘端决策级融合（核心创新，评审命门）。

### 后期
7. **M4 数据集**：建成自有多类数据集（含跌倒），评估指标留测试集。
8. **M5 集成部署**：边缘+云端联调、Docker、试点。
9. **M6 成果**：论文 / 专利 / 研究报告 / 答辩 PPT。

---

## 快速开始

### 端口约定（防踩坑）
- **后端 FastAPI = 8000**（`backend/run.sh`：`uvicorn --port 8000`）
- **前端 Vite dev = 5173**，通过 `frontend/vite.config.ts` 把 `/api` 与 `/ws` 代理到 `localhost:8000`
- 前端代码用相对 `/api`、WS 用 `location.host`+代理，**不直接写后端端口**；改端口只需动 `run.sh` 与 `vite.config.ts` 两处。

### 1. 启动后端
```bash
cd backend
pip install -r requirements.txt
bash run.sh          # 监听 8000
# Swagger: http://localhost:8000/docs
```

### 2. 启动前端
```bash
cd frontend
npm install
npm run dev          # http://localhost:5173
```

### 3. 登录（机构管理端）
- 用户名 `admin` / 密码 `admin123`（后端 seed 的默认管理员）

### 4. 切换数据源（四态）
正式前端不暴露切换入口，用 API 切换：
```bash
# mock（默认，合成体征/预警）/ mmfi（验证样例）/ real（真实雷达占位）/ replay（同学坐走回放）
curl -X POST http://localhost:8000/api/data-source -H "Content-Type: application/json" -d '{"source":"replay"}'
```
- `mock`：合成生命体征 + 随机预警（联调演示）
- `mmfi`：MMFi 样例（仅验证管道，生命体征为 null）
- `real`：真实雷达（M1 接原始点云后生效）
- `replay`：同学坐/走回放（**演示，非实时检测**）

### 5. 演示跌倒预警
登录后可等待后端 `mock` 流；或 `POST /api/simulate/fall` 手动触发跌倒红警（现场演示用）。

## 许可证

项目源码内部研发使用，未开源。引用开源组件均已标注来源（见 `deliverables/product-strategy/opensource-survey-yanglao-2026-08-05.md`）。

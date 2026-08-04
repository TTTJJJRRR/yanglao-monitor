# 智能康养监测系统（yanglao-monitor）

> 基于毫米波雷达与视频图像融合的智能康养监测系统研发
> 江南大学 · 人工智能与计算机学院（大创重点项目）
> 周期：2026.03 – 2027.03

## 项目简介

一套面向智慧养老的**多模态健康主动预警系统**：毫米波雷达（TI IWR6843ISK）非接触式
监测呼吸/心率/睡眠呼吸暂停，视频图像识别跌倒/行为/情绪，二者在边缘端融合后做主动预警，
数据上云做长期趋势分析与模型迭代。

## 团队与分工

| 成员 | 角色 | 负责 |
|------|------|------|
| 陈意豪 | 队长 | 文档 / 论文 / 专利 / 对外 |
| 滕家瑞（teng-jiarui_TJR） | 技术总负责 | 架构 / 前后端 / 融合算法 / 代码闸门 |
| 黄敬城 | 副手 | 前后端编码 / 测试验证 |
| 周震宇 | 数据采集 | 雷达 + 视频 硬件与原始数据 |
| 万砚佶 | 标注 + 文档协助 | 数据标注 / 论文专利初稿 |

详细分工与数据交付格式见 [`docs/人员分工与数据交付规范.md`](docs/人员分工与数据交付规范.md)。
架构与流程总览见 [`docs/大创项目统筹需求文档.md`](docs/大创项目统筹需求文档.md)。

## 仓库结构

```
yanglao-monitor/
├── docs/                 # 需求/分工/规范文档
├── backend/              # FastAPI 后端（feat/backend）
├── frontend/             # React 前端大屏（feat/frontend）
├── edge/                 # 边缘端部署（网关/模型轻量化）
├── fusion/               # 融合算法（特征级+决策级，核心创新）
├── data/                 # 数据（大文件走 LFS/网盘，仅留说明与示例）
│   ├── radar/            # 周震宇：雷达 JSON + 视频 + meta
│   └── label/            # 万砚佶：标注 COCO JSON
├── tests/                # 测试（黄敬城主导）
├── scripts/              # 工具脚本（数据转换/解析）
└── cursor-orchestrator/  # WorkBuddy→Cursor 文件接力工具（非交付源码）
```

## 分支策略

- `main`：稳定版，仅滕家瑞可合并
- `dev`：日常开发主分支
- `feat/backend` `feat/frontend`：滕/黄
- `data/radar`：周震宇  `data/label`：万砚佶  `docs`：陈/万
- 流程：feature 分支 → PR → 滕 review 合并

## 技术栈（参考 smart-greenhouse-iot-dashboard 架构）

- 后端：FastAPI + SQLAlchemy + SQLite/PostgreSQL + JWT
- 前端：React + Vite + TypeScript + Tailwind + Recharts
- 实时：WebSocket
- 部署：Docker Compose
- 感知：mmVital-Signs（TI IWR6843 Python API）
- 边缘AI：YOLOv8 + MediaPipe（改造自 Multi-modal-Fall-Detection）

## 开发阶段

| 阶段 | 时间 | 目标 |
|------|------|------|
| M0 脚手架 | 8月 | 后端空壳+前端大屏+数据契约 |
| M1 感知打通 | 9月 | 雷达(模拟)→体征显示；视频→跌倒demo |
| M2 边缘AI | 9-10月 | 行为/情绪识别、雷达信号分离 |
| M3 融合原型 | 10-11月 | **最小融合原型（核心创新）** |
| M4 数据集 | 10-12月 | 真实采集+标注，建成数据集 |
| M5 集成部署 | 12-1月 | 边缘+云端联调、Docker、试点 |
| M6 成果 | 2-3月 | 论文/专利/研究报告/答辩PPT |

## 快速开始

> 待 M0 由 Cursor 生成脚手架后补充。

## 许可证

项目源码内部研发使用，未开源。引用开源组件均已标注来源（见 docs）。

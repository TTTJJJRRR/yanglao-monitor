# 开源技术生态调研报告 — 智能康养监测系统（IWR6843AOP + 摄像头融合）

**日期**：2026-08-05
**类型**：竞品 / 开源生态分析
**参与成员**：竞析（竞品分析师）

---

## 📌 TL;DR（执行摘要）
- **核心目标**：找出能直接复用逻辑/代码、避免从零搭建的开源项目与官方例程，覆盖毫米波雷达（IWR6843AOP）+ 视频融合的康养监测全链路。
- **关键决策**：**分模块复用**——TI 官方例程打底（AOP 兼容）+ 精选开源补算法/视觉/后端骨架；不要自研雷达驱动和生命体征底层算法。
- **下一步**：雷达到货后用 TI Out-of-Box + Vital Signs 验证；生命体征抄 mmVital-Signs；行为抄 patient_monitoring；视觉用 MediaPipe（边缘不上云）；后端骨架参考 32iterations 的 FastAPI+WS。

---

## 🎯 核心结论卡片

| 项目 | 内容 |
|------|------|
| 推荐方案 | TI 官方例程 + 5 个精选开源分模块复用，不自研底层 |
| 优先级 | P0（M1 感知阶段必须） |
| 预期影响 | 省掉雷达接入层、生命体征相位提取、行为识别 CNN、视觉骨骼化、后端 WS 骨架的大部分从零工作 |
| 资源需求 | 一台能跑 ROS2 的机器（或走纯 Python 路线避开 ROS）；Python 3.12+ |
| 风险等级 | 中（官方无现成跌倒检测 lab，需基于开源改；ROS 栈有学习成本；部分仓库 Star/活跃度待核实） |

---

## 1. 调研全景（按可复用维度分类）

### 1.1 TI 官方例程 / SDK（必抄，AOP 兼容）
- **MMWave SDK + Industrial Toolbox 4.12.0**（dev.ti.com/tirex）
  - 含 `68xx_vital_signs`（呼吸/心率）、`68xx_gesture_recognition`、`Out_Of_Box_Demo`（含 `xwr64xxAOP_mmw_demo.bin` 即 AOP 专用固件）、People Tracking
  - AOP 兼容：✅（AOP 是同芯片 AoP 封装，OOB 与 Vital Signs 均可跑）
  - 复用点：算法参考 + `.cfg` 配置 + TLV 解析格式
  - 成本：中
  - ⚠️ 官方工具箱**没有现成"跌倒检测"lab**，需自研或基于开源改

### 1.2 开源生命体征估计
- **mmVital-Signs**（Python，TI xWR14/16/68xx 标准 API，0.1–8.6m 非接触呼吸/心率）
  - AOP 兼容：✅（同 68xx 系列）
  - 复用点：Python 解析 + 生命体征算法（相位提取/FFT）
  - 成本：【低，最省事】
- **Z-H-XU/DCT-Vital-Signs**（MATLAB，DCT 稀疏优化，MAPE 2.96%/5.92%）
  - 复用点：算法思路，需转 Python；成本：中

### 1.3 开源跌倒检测
- **radar-lab/mmfall**（⭐135，Python/Jupyter，4D mmWave 点云 + 变分 RNN 自编码器，半监督，98%）
  - 复用点：异常检测范式；成本：中
- **iwantlatiao/mmFall**（Python/PyTorch，RD+RA 双流 + 多任务）
  - 复用点：雷达图特征工程 + 训练流水线；成本：中

### 1.4 视频骨骼化 / 行为识别（隐私合规：只取关键点，不上云）
- **MediaPipe Pose**（Google，Python，33 关键点边缘实时）
  - 复用点：骨骼化 + 躯干倾角判跌倒；成本：【低】
- **sayksii/dual-model-fall-detection**（Python/PyTorch/MediaPipe，MIT，TCN+ST-GCN 老人跌倒，GUI/CLI/训练齐全）
  - 复用点：整套视觉跌倒管线；成本：中低
- **pat2echo/AI-Posture-Monitor**（Python/MediaPipe/模糊逻辑 + 有限状态机，pip 即用）
  - 复用点：姿态状态机（站立/坐/躺/跌倒）；成本：【低】

### 1.5 雷达接入驱动（AOP 专用）
- **radar-lab/ti_mmwave_rospkg**（⭐300，C++/ROS，含 AOP 配置、多雷达、相机叠加）
  - AOP 兼容：✅；复用点：串口驱动 + 点云发布；成本：中（需 ROS）
- **lightinfection/TI_IWR6843AOP**（ROS2/C++/Python，专为 AOP，滤波/DBSCAN/3D tracking + 实时热力图，docker 一键起）
  - AOP 兼容：✅✅ 最贴合；复用点：开箱即用的点云与 tracking；成本：中低

### 1.6 多床位行为识别（与需求 1:1）
- **radar-lab/patient_monitoring**（⭐60，C++/ROS/CNN，多床位、6 类行为实时识别——行走/坐/躺/弯腰/跌倒/静止）
  - 复用点：多目标 Doppler 特征 + 3 层 CNN 范式（与本项目 6 类行为需求几乎一致）；成本：中

### 1.7 融合 / 系统级
- **32iterations/mmwave-fall-omniverse-demo**（FastAPI + WebSocket + PyTorch 跌倒 demo）
  - 与本项目技术栈（FastAPI + WS）**同构**；复用点：后端/前端骨架；成本：【低】
- **radar-lab/autolabelling_radar**（MATLAB，雷达-相机自动标注）、**sensors-ros1 / Radar_Camera_MOT**（雷达+相机 MOT、在线标定）

### 1.8 数据集处理代码（团队已有 mmFi 样例）
- **ybhbingo/MMFi_dataset**（NeurIPS2023 主流，Python/PyTorch，mmWave(.bin)+RGB+深度+LiDAR+WiFi 统一 dataloader，含隐私脱敏关键点）
  - 复用点：mmFi 解析逻辑直接抄；成本：中低
- **phish-tech/awesome-mmwave-sensing**（精选索引，含 RadHAR、HuPR 等）

---

## 2. 可复用项目矩阵

| 项目 | 链接/来源 | Star | 技术栈 | 借鉴点 | 复用成本 | AOP |
|------|-----------|------|--------|--------|----------|-----|
| TI Industrial Toolbox | dev.ti.com/tirex | - | C/Lua/cfg | 生命体征+OTA 固件+TLV 格式 | 中 | ✅ |
| lightinfection/TI_IWR6843AOP | GitHub | 未知 | ROS2/C++/Py | AOP 驱动+点云+tracking | 中低 | ✅✅ |
| ti_mmwave_rospkg | GitHub | 300 | C++/ROS | 串口驱动+点云 | 中 | ✅ |
| mmVital-Signs | gitcode 镜像 | 未知 | Python | 生命体征解析+算法 | 低 | ✅ |
| radar-lab/patient_monitoring | GitHub | 60 | C++/ROS/CNN | 6 类行为 CNN 范式 | 中 | 可 |
| radar-lab/mmfall | GitHub | 135 | Py/Jupyter | 跌倒异常检测 | 中 | 可 |
| MediaPipe Pose | Google | - | Python | 骨骼化+倾角判跌倒 | 低 | n/a |
| sayksii/dual-model-fall-detection | GitHub | 未知 | Py/PyTorch | 视觉跌倒管线 | 中低 | n/a |
| 32iterations/mmwave-fall-omniverse-demo | GitHub | 未知 | FastAPI+WS+PyTorch | 后端/前端骨架 | 低 | n/a |
| ybhbingo/MMFi_dataset | GitHub | 未知 | Py/PyTorch | mmFi 解析+dataloader | 中低 | n/a |

---

## 3. Top 推荐（按省事程度排序）

1. **mmVital-Signs（Python）** → 直接拿 TI 雷达生命体征解析+算法，省掉从零写串口/TLV/相位提取。
2. **lightinfection/TI_IWR6843AOP（ROS2）** → AOP 专用驱动+点云+tracking 开箱即用，省掉雷达接入层。
3. **radar-lab/patient_monitoring（CNN 多床位 6 类）** → 行为识别范式与需求几乎 1:1，省掉自设计特征/模型。
4. **ybhbingo/MMFi_dataset** → mmFi 解析与 dataloader，省掉样例数据解析代码。
5. **sayksii/dual-model-fall-detection + MediaPipe** → 视觉跌倒/姿态完整管线，边缘只出骨骼关键点满足隐私红线，省掉视觉侧从零造。

> 纯雷达跌倒可再叠加 radar-lab/mmfall 或 iwantlatiao/mmFall 做融合冗余；后端直接参考 32iterations 的 FastAPI+WS 结构。

---

## 4. 与本项目技术栈的契合度 & 复用路线

现有栈：FastAPI + WebSocket + React + SQLAlchemy + JWT三角色；雷达未到货，现用 mock/mmFi。

| 模块 | 现有状态 | 建议复用 | 接入方式 |
|------|----------|----------|----------|
| 雷达接入层 | 无 | lightinfection AOP 驱动 / TI OOB 固件 | 雷达到货后接串口，点云经 WS 广播（复用现有 mock_stream 通道） |
| 生命体征 | mock 生成 | mmVital-Signs 解析+算法 | 替换 data_source 的 mock 为真实解析 |
| 行为6类 | 无 | patient_monitoring CNN 范式 | 后端加推理服务 |
| 跌倒 | 无 | mmfall + MediaPipe 视觉 | 雷达+视觉双路，融合告警 |
| 视觉 | 无 | MediaPipe（边缘骨骼化，不上云） | 边缘节点只吐关键点 JSON |
| 后端骨架 | 已有 FastAPI+WS | 32iterations 同构 demo | 参考其结构增强告警/多床 |
| 数据集解析 | mmFi 样例 | ybhbingo/MMFi_dataset | 直接抄 dataloader |

---

## 5. ✅ 行动清单

| # | 行动 | 负责方 | 时间窗 |
|---|------|--------|--------|
| 1 | 雷达到货后用 TI Out-of-Box + Vital Signs 例程验证 AOP 点云/生命体征 | 滕家瑞 | M1（9月） |
| 2 | 接入 lightinfection AOP 驱动（或 mmVital Python 直连）拿点云 | 滕家瑞 | M1 |
| 3 | 生命体征算法抄 mmVital-Signs（相位提取/FFT） | 滕家瑞 | M1 |
| 4 | 行为6类参考 patient_monitoring CNN 范式做原型 | 滕家瑞/后续 | M2 |
| 5 | 视觉侧 MediaPipe 骨骼化 + sayksii 跌倒管线（边缘，不上云） | 黄敬城/视觉 | M2-M3 |
| 6 | 后端骨架参考 32iterations FastAPI+WS 做告警/多床增强 | 滕家瑞 | M0-M1 |
| 7 | mmFi 解析抄 ybhbingo/MMFi_dataset dataloader | 周震宇/滕 | 当前 |

---

## 6. ⚠️ 待确认 / 假设 / Non-goals

- **假设**：竞析检索的部分仓库 Star/链接需落地前二次核实（尤其 gitcode 镜像与部分未知 Star 项）。
- **Non-goals**：
  - 不自研雷达底层驱动（直接用 TI/开源）
  - 不自研生命体征 DCT/相位算法（直接抄 mmVital）
  - 不把视频上云（视觉只边缘出骨骼关键点）
  - 不引入完整 ROS 生态（除非 AOP 驱动必需；可走纯 Python 路线避开 ROS 学习成本）
- **风险**：官方无现成跌倒检测 lab；ROS2 环境搭建有学习成本；部分开源项目许可（license）需逐一确认（MIT 优先）。

---

## 7. 📚 数据来源 & 成员产出索引
- 竞析（竞品分析师）：全网开源生态调研（TI 官方例程、生命体征/跌倒/行为/视觉/融合/数据集共 10+ 项目，含 AOP 兼容性与复用成本评估）

---

---

## 8. 🔍 2026-08-09 GitHub 前沿补充检索（连接器实搜）

> 方法：用 GitHub 连接器 `search_repositories` 实搜 "mmwave fall detection / HAR transformer / radar vision multimodal / mmwave vital signs / elderly monitoring radar / multimodal fall detection" 等 13 组关键词。下列为**高信噪比 + 可借鉴**项，按可升级我们现有代码的程度分档。

### 8.1 雷达行为识别新架构（可升级 `mmwave_cnn` 朴素 CNN）
- **`AksharThakor/RadarPose-HybridNet`** — Point Transformer(3D 姿态) + CTR-GCN(时序) 混合，23 类 **95.79%**。**借鉴：点云→Point Transformer 替代我们 voxel-grid CNN，提点云 HAR 精度。**
- **`Alan-cs1/MmWave-Motion-Waveform-HAR`** — ICMEW 2025，Motion Waveform 预处理喂 Transformer 分类。**借鉴：给 `preprocess.py` 加 waveform 表征分支（我们当前只有 voxel grid）。**
- **`yizzfz/MiliPoint` (⭐125)** — 开源 mmWave 点云 HAR 数据集，可预训练/数据增强。
- **`1YifanGuo/mmLM`** — 点云 + 语言模型对抗域偏移（跨受试者泛化）。**借鉴：解决"采够样本/跨人泛化"痛点。**

### 8.2 多模态 / 雷达-视觉融合新范式（我们主线）
- **`jpnm561/HAR-UP` (⭐53)** — 成熟多模态跌倒检测系统。
- **`DHUspeech/fall-mamba`** — **Fall-Mamba：Masked Mamba(状态空间模型) 多模态融合**，2024-2026 最新架构趋势，比 Transformer 更省算力做长时序。**借鉴：融合层从 `fall_fusion.py` 的 if/else 规则升级为 Mamba/Transformer 时序融合（远期）。**
- **`faresaljbour/A-Dual-Transformer-Fusion-Framework`** — 视频 + 2D 骨骼双分支 Transformer 融合。**借鉴：视觉侧（MediaPipe 骨骼）升级为 Transformer 融合。**
- **`01Elaine/fall-detection-multimodal`** — 视频(RTMPose+ST-GCN) + 音频(PANNs) **决策级融合** + 深度。**与我们 `fall_fusion.py` 决策级融合同构，可参考其融合权重设计。**
- **`MODAL-UNINA/Federated-Learning-based-Fall-Detection-with-Multimodal-Data-Fusion`** — 联邦学习多模态融合（隐私）。**远期：多家庭部署参考。**

### 8.3 生命体征（直接对标 `mmvital_estimator`）
- **`phish-tech/mmWave-Heartbeat-Dataset-Preprocessing-Toolbox-` (⭐60, 更新 2026-08)** — **开源 77GHz 单人 .bin 原始数据 + MATLAB EEMD 呼吸/心跳分离基线。★最可借鉴：用其真实数据验证我们的 DFT 周期图估计；EEMD 作对照方法。**

### 8.4 隐私优先产品哲学（印证我们方向）
- **`marminguez/theguardian` / `Yeeejj/guardian-priv-monitor`** — 被动毫米波 → **8 项老人可读日常信号**，全本地、无云、无相机、无音频。**几乎就是我们的产品愿景（8 类行为=8 信号），印证"不上云/不拍照"是前沿正确方向。**
- **`SiDOlu/aetherics`** — Edge-AI + 毫米波 + 热阵 + MEMS，无相机环境智能。
- **`Sameer856/EchoCare` / `AsadIdreesEE/LexaCare_Project`** — 雷达(+热成像/麦克风) 老人日常活动 + 告警。

### 8.5 雷达跌倒（与 `radar-lab/mmfall` 互补）
- **`DarkSZChao/MMWave-radar-human-tracking-and-fall-detection` (⭐77, 更新 2026-08)** — 多人跟踪 + 跌倒，最新。**比 mmfall 多 tracking，补我们多目标场景。**
- **`sareebali/mmwave-radar-fall-detection`** — 点云 CNN 跌倒（PyTorch），轻量可抄。

### 8.6 ⚠️ 诚实 caution（与第 6 节一致）
- 多数"多模态融合" repo 是 **视频 + 音频，不是雷达 + 视觉**；雷达+视觉融合代码稀缺，我们属较先锋 → 宜借*融合策略*(决策级/双 Transformer/Mamba) 而非照搬模态。
- 2026 新 repo 多 **0–9⭐（未经验证）**，作"方向参考"；高信噪比：`radar-lab/mmfall`(152) / `yizzfz/MiliPoint`(125) / `phish-tech`(60) / `DarkSZChao`(77) / `HAR-UP`(53)。
- **License 必须逐仓核实（MIT 优先）**；学术 paper repo 常无显式 license，商用前需确认。
- `Fall-Mamba` / `RadarPose-HybridNet` 需 torch + 较大数据，等周震宇真实多类数据到位后再升级（现 8 类单类 CNN 先跑通）。

---

> 本报告由产品战略团队 AI 协作生成，重要决策请由产品负责人审定。

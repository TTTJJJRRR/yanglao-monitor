# 开源项目移植与借鉴技术指南 — 智能康养监测系统（IWR6843AOP + 摄像头）

> 作者：Senior Developer（高级全栈开发工程视角）
> 日期：2026-08-05
> 配套：调研报告 `deliverables/product-strategy/opensource-survey-yanglao-2026-08-05.md`
> 目标：把"可借鉴开源项目"逐个拆成**能搬进现有 FastAPI+WS+React 栈**的工程步骤，避免从零造轮子。

---

## 0. 现状基线 & 移植接入点

**现有架构（已读源码确认）**
- 后端：`backend/app/`（`main.py` 的 `mock_stream()` 后台任务 + `broadcast()` 统一出口；`data_source.py` 管理 `mock`/`mmfi` 切换；`mock.py` 生成器；`models.py` 含 `VitalRecord`/`BehaviorEvent`/`Alert`；`routers/` 四个；`ws.py`）
- 前端：`frontend/src/`（`types.ts` 平坦契约 `VitalData`/`BehaviorData`/`AlertData`；`App.tsx` WS 订阅 + 数据源切换按钮现成）
- 数据契约：平坦 `vital` = `timestamp_ms / device_id / breath_rate / heart_rate / chest_displacement_mm / motion_flag / ahi_index`（对齐需求文档 §6.1）

**两个必须先修的移植坑（后面每节呼应）**
- **坑 A — 行为枚举不统一**：现有 `BehaviorAction = {walking, falling, sitting_still, standing_up, lying, normal_activity}`，但需求文档 6 类 =「行走/坐下/躺下/弯腰/跌倒/静止」，`patient_monitoring` 也是这 6 类。**现有缺"弯腰"、多"站立/常态"**，移植行为识别前必须统一。
- **坑 B — VitalRecord NOT NULL vs 雷达偶发 null**：`VitalRecord.breath_rate/heart_rate/chest_displacement_mm/motion_flag` 全是 `nullable=False`。真实雷达偶尔丢值出 `null` 会落库崩。real 模式必须做插值/兜底，或仿 mmfi **只广播不落库**。

**核心接入点（最小改动路径）**
> 新增任意真实数据源 = 在 `data_source.AVAILABLE` 加名字 → `mock_stream()` 加对应分支 → 调用解析器映射成平坦 `vital`/`behavior`/`alert` → 复用 `broadcast()`。前端 `types.ts` 已预留 `source: 'real'`，几乎不用改。

---

## 1. 雷达接入层（硬件串口 → 点云/生命体征 TLV）

### 1.1 TI Industrial Toolbox 官方例程（必用，不是"抄"是"必须"）
- **是什么**：`dev.ti.com/tirex` 的 MMWave SDK + Industrial Toolbox 4.12，含 `Out_of_Box_Demo`（含 `xwr64xxAOP_mmw_demo.bin` **AOP 专用固件**）、`68xx_vital_signs`、`people_tracking`。
- **借鉴/复用**：烧录 AOP 固件；用 OOB 例程经串口输出 TLV 点云；用 `vital_signs` 例程输出生命体征 TLV。
- **移植步骤**：
  1. Uniflash 烧录 `xwr64xxAOP_mmw_demo.bin` 到 AOP（一次性）。
  2. 配 `.cfg`（OOB 的 `profile_2D.cfg` 或 vital_signs 的 config），串口 921600 波特。
  3. PC 侧自写/抄 TLV 解析（`pyserial` 读帧 → 按 TI TLV 格式解包 → 点云/生命体征）。可参考 mmVital（§2.1）或 TI 官方 mmw demo 解析脚本。
- **依赖**：TI mmWave SDK（C 固件板端跑）；PC 侧 `pyserial`。
- **雷达未到**：❌ 这是硬件层，必须等货。
- **风险**：cfg 的 range/resolution 参数调优影响精度；AOP 天线布局固定不可改。

### 1.2 lightinfection/TI_IWR6843AOP（ROS2 驱动，AOP 专用）
- **是什么**：ROS2 包，串口读 AOP + 滤波/DBSCAN/3D tracking + 实时热力图，docker 一键起。
- **借鉴**：开箱即用的点云 + tracking，省掉自写驱动和跟踪。
- **移植步骤（ROS 路线）**：装 ROS2 + docker → 跑其 launch → 订阅 `/ti_mmwave/pointcloud` 话题 → 写 ROS2→FastAPI 桥接节点把点云转 WS 推后端。
- **依赖**：ROS2 Humble + docker + 一台算力机。
- **风险**：中。引入整个 ROS2 生态，学习曲线陡，与现有纯 FastAPI 架构割裂。
- **💡 Senior Developer 建议**：**M1 先用纯 Python 直连串口（§1.1 + §2.1），把 ROS2 驱动留到 M2 若需多目标 tracking 再上**。团队是新手，ROS2 成本不划算。

### 1.3 ti_mmwave_rospkg（ROS 驱动备选）
- 类似 1.2，C++/ROS1，⭐300 更流行但 ROS1 已老旧。除非已在用 ROS1，否则不优先。作 ROS 路线备选。

---

## 2. 生命体征估计（呼吸/心率）

### 2.1 mmVital-Signs（Python，最省事，**重点抄**）
- **是什么**：TI xWR14/16/68xx 标准 Python API，0.1–8.6m 非接触呼吸/心率，解析+算法一体。
- **借鉴**：串口配置、TLV/相位数据解析、相位提取→FFT→呼吸/心率估计算法。
- **移植步骤（精确到文件）**：
  1. 依赖装进 `backend313` venv：`pyserial numpy scipy`；或将其 core 模块 vendoring 到 `backend/app/sources/mmvital_core/`。
  2. 新建 `backend/app/sources/mmvital_source.py`：
     ```python
     class MmVitalSource:
         def __init__(self, port="COMx", baud=921600):
             self.ser = serial.Serial(port, baud)
             self._last = None
         def next_vital(self) -> dict:
             raw = parse_tlv(self.ser.read())        # 抄 mmVital 解析
             br, hr = estimate_vitals(raw)            # 抄其相位/FFT 算法
             # 坑B 对策：偶发 None 时线性插值或保持上一帧
             br = br if br is not None else self._last["breath_rate"]
             return {"timestamp_ms": now_ms(), "device_id": "RADAR_01",
                     "breath_rate": br, "heart_rate": hr,
                     "chest_displacement_mm": ..., "motion_flag": ..., "ahi_index": None,
                     "source": "real"}
     ```
  3. `data_source.py`：`AVAILABLE` 加 `"real"`；新增 `_mmvital = MmVitalSource()`；`next_real_messages()` 复用 broadcast 格式。
  4. `main.py` `mock_stream()` 加 `elif get_source()=="real": for msg in next_real_messages(): await broadcast(msg)`。
  5. `models.VitalSource` 已有 `real` ✓；前端 `types.ts` `source` 已有 `'real'` ✓；`App.tsx` 切换按钮加 `'real'` 选项即可。
- **依赖**：`pyserial numpy scipy`。
- **雷达未到**：若仓库带回放/样例 `.bin`，用其跑通管道；否则用现有 `mock` 占位，等货接真串口。
- **风险**：低-中。需确认其 TLV 格式与 AOP（同 68xx 系列）一致，基本兼容。
- **工作量**：2–3 天。

### 2.2 Z-H-XU/DCT-Vital-Signs（MATLAB，备选）
- **是什么**：DCT 稀疏优化，MAPE 2.96%/5.92%（比 FFT 更鲁棒）。
- **借鉴**：算法思路。
- **移植**：MATLAB 不适用后端，需重写为 Python（`scipy` 做 DCT）。**优先级低**，M2 要提精度再考虑，不作为 M1 必做。
- **风险**：中（重写成本）。

---

## 3. 行为识别（6 类）

### 3.1 radar-lab/patient_monitoring（CNN，与需求 1:1）
- **是什么**：C++/ROS，多床位，6 类行为（行走/坐/躺/弯腰/跌倒/静止）实时识别，3 层 CNN on Doppler 特征。
- **借鉴**：多目标 Doppler 特征提取 + 3 层 CNN 范式 + 6 类定义。
- **⚠️ 先修坑 A（统一行为枚举）**：
  - `models.py`：`BehaviorAction` 改为 `walking / sitting / lying / crouching / falling / still`（对齐需求文档 6 类）。
  - `types.ts`：`BehaviorData.action` 联合类型同步。
  - `mock.py`：`generate_behavior()` 的 `choice` 列表同步；`emotion` 字段 M1/M2 暂置 `calm`（情绪是 P2）。
- **移植步骤**：
  1. 抽取其特征工程（Doppler FFT→特征图）和 CNN 推理，封装为 `backend/app/inference/behavior_cnn.py`（**纯 Python/PyTorch，脱离 ROS**）。
  2. 输入：real 雷达的 Range-Doppler 图；输出：6 类 softmax + confidence。
  3. `mock_stream()` 的 real 分支周期性调 `behavior_cnn`，映射成 `BehaviorEvent` 落库 + broadcast。
- **依赖**：`torch numpy`；训练数据来自周震宇采集（M4）。
- **雷达未到**：用其发布预训练权重 + 公开 Doppler 样本先跑通推理管线；行为数据用 mock 生成（对齐新枚举）。
- **风险**：中。ROS/C++ 转 Python 有工作量；预训练权重是否开源需确认。
- **工作量**：3–5 天（含枚举统一）。

---

## 4. 跌倒检测（雷达 + 视觉融合；官方无现成 → 组合）

### 4.1 radar-lab/mmfall（Python，雷达点云异常检测）
- **是什么**：4D mmWave 点云 + 变分 RNN 自编码器，半监督，98%。
- **借鉴**：雷达点云异常检测范式（无标签也能训）。
- **移植**：`backend/app/inference/fall_radar.py`，输入 real 点云，输出 `fall_probability`。
- **雷达未到**：用其公开样本/合成点云跑通。
- **风险**：中（需训练）。

### 4.2 iwantlatiao/mmFall（PyTorch，RD+RA 双流）
- **是什么**：Range-Doppler + Range-Azimuth 双流 + 多任务（跌倒+关键点）。
- **借鉴**：特征工程 + 训练流水线。
- **移植**：与 4.1 二选一或融合，作雷达跌倒更强备选。
- **风险**：中。

### 4.3 融合策略（💡 M3 评审命门）
- 官方无跌倒 lab，故 **雷达(mmfall) + 视觉(MediaPipe 倾角) 双路投票**：
  - `雷达 fall_prob > 阈值` **OR** `视觉躯干倾角 > 阈值` → 触发 `red` alert（≤3s）。
- 在 `backend/app/inference/fall_fusion.py` 做融合决策，输出 `Alert`。**建议 M1 起就搭融合框架（先用 mock 双路）**，M3 才填真模型。

---

## 5. 视觉骨骼化（边缘节点，绝不上云）

### 5.1 MediaPipe Pose（Google，必用）
- **是什么**：33 关键点，边缘实时。
- **借鉴**：骨骼化 + 躯干倾角判跌倒。
- **移植（架构关键）**：
  1. **新建独立边缘节点** `edge/vision_node.py`（跑在摄像头旁主机/本地进程，**不进 FastAPI 后端**）。
  2. 读摄像头 → MediaPipe → 提取 33 关键点（或仅躯干倾角）→ 经 WS/HTTP POST 给后端新接口 `/api/edge/pose`。
  3. **绝不发送视频帧**，只发 JSON 关键点（隐私红线 R-P0-03）。
  4. 后端新增 `routers/edge.py` 接收姿态 JSON，转成 behavior/fall 输入。
- **依赖**：`mediapipe opencv-python`（仅本地读帧）。
- **雷达未到**：✅ edge 节点可单独开发测试（任意摄像头）；后端接收逻辑先用 mock 姿态 JSON。
- **风险**：低（MediaPipe 成熟）。
- **工作量**：2 天。

### 5.2 sayksii/dual-model-fall-detection（视觉跌倒管线）
- **是什么**：TCN+ST-GCN 老人跌倒，MIT，GUI/CLI/训练齐全。
- **借鉴**：整套视觉跌倒训练+推理管线（吃骨骼序列而非单帧倾角）。
- **移植**：替换/增强 5.1 的倾角法，用 ST-GCN 吃 MediaPipe 关键点序列。
- **风险**：中（ST-GCN 训练）。

### 5.3 pat2echo/AI-Posture-Monitor（姿态状态机）
- **是什么**：站立/坐/躺/跌倒，模糊逻辑+FSM，pip 即用。
- **借鉴**：姿态状态机（视觉侧行为识别的轻量实现，对标 patient_monitoring 的视觉版）。
- **移植**：edge 节点用其 FSM 直接输出姿态类别，省掉训练。
- **风险**：低。

---

## 6. 后端骨架 & 增强

### 6.1 32iterations/mmwave-fall-omniverse-demo（FastAPI+WS）
- **是什么**：FastAPI+WS+PyTorch 跌倒 demo，与你栈**同构**。
- **借鉴**：后端结构、告警广播模式、前端组件。
- **移植**：现有后端已同构，**重点抄其告警规则引擎 + 多床管理思路**补强 `routers/alerts.py` 和新增多床位（M1 需求 P1）。
- **风险**：低（参考性质）。

---

## 7. 数据集解析

### 7.1 ybhbingo/MMFi_dataset（mmFi dataloader）
- **是什么**：NeurIPS2023，统一 dataloader（mmWave+RGB+深度+LiDAR+WiFi），含脱敏关键点。
- **借鉴**：mmFi `.bin` 解析 + dataloader，用于周震宇采集数据的离线处理。
- **移植**：`backend/app/data/mmfi_loader.py` 抄其解析，替换 `data_source.MMFiSource` 的 jsonl 读取为真实 `.bin` 解析（M4 用）。
- **雷达未到**：现在 `MMFiSource` 读 jsonl 已够演示；真 `.bin` 解析等采集后。
- **风险**：低-中。

### 7.2 phish-tech/awesome-mmwave-sensing（索引）
- **是什么**：mmWave 精选索引（含 RadHAR、HuPR 等）。
- **借鉴**：后续查资料入口，不移植代码。

---

## 8. 移植优先级 & 路线图（结合 M0–M3）

| 阶段 | 无雷达能否做 | 动作 |
|------|------|------|
| **M0（现在）** | ✅ | 统一行为枚举(坑A)；搭 edge 视觉节点骨架(§5.1)；后端告警/多床增强(§6.1)；mmVital 管道回放模式跑通(§2.1)；fall_fusion 框架(§4.3) |
| **M1（雷达到）** | ❌→✅ | TI 固件烧录(§1.1) + mmVital 直连串口(real 源)(§2.1) + 统一数据通道 |
| **M2** | — | behavior_cnn 移植(§3.1) + fall_radar 移植(§4.1) + MediaPipe 倾角接入(§5.1) |
| **M3（评审命门）** | — | fall_fusion 双路融合(§4.3) 填真模型 |

---

## 9. 关键风险汇总
1. **坑 A**：行为枚举不统一（必须修，否则 patient_monitoring 移植后数据对不上）。
2. **坑 B**：`VitalRecord` NOT NULL vs 雷达偶发 null（real 模式需插值/兜底或仿 mmfi 只广播不落库）。
3. ROS2 生态重 → 建议纯 Python 路线优先。
4. 官方无跌倒 lab → 自研融合（M3 命门）。
5. license 需逐一确认（MIT 优先）。
6. 部分仓库 Star/API 落地前二次确认（尤其 gitcode 镜像与未知 Star 项）。

---

> 本报告由 Senior Developer 基于现有代码审阅 + 开源调研产出，重要工程决策请由滕家瑞/导师审定。

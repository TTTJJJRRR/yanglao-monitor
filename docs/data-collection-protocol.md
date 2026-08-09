# 真实毫米波数据采集团队规程（M1 + M4 合并执行，雷达已到货）

> 触发：IWR6843AOP 已于 **2026-08-07 到货**。P0 数据获取从"借 MMFi"转为"采集自有硬件数据"——更贴合大创、且能补齐 MMFi 缺失的跌倒类。
> 执行人：**周震宇**（唯一原始数据采集，见团队 RACI）；规程与工具由 WorkBuddy 编写，肆月转发群。
> 关联：`tasks/M4-data-retrain-cursor.md`（重训）、`edge/capture_oob.py`（采集脚本）。

## 0. 为什么改路线
- MMFi 公开集 27 类日常/康复动作里**没有 `falling`**，而跌倒是项目 P0 关键类。
- 用自己硬件采的数据 = 我们的部署场景（房间布局、天线朝向、人体特征），模型泛化更可信，评审也更站得住。
- 结论：**自有 IWR6843AOP 数据为主，MMFi 降为校验/补充集。**

## 1. 硬件清单
- IWR6843AOP EVM（天线封装，无需外接天线）
- 5V / ≥2.5A 电源（或 EVM 配套供电）
- micro-USB 数据线 ×1（连 PC，承载 CLI + DATA 双 UART）
- 上位机：Windows 或 Linux PC（Python 3.11+，装 `pyserial` + `numpy`）
- 雷达支架：高度 1.0–1.5 m，朝向人体胸腹（模拟实际安装）
- 安全垫：采集 `falling` 类时使用

## 2. 固件与连接
1. 装 TI **mmWave SDK（3.6.x）**。取 AOP 专用 demo 固件：
   `packages/ti/runtime/xwr68xx/mmw/xwr68xx_aop_mmw_demo.bin`
   （路径随 SDK 版本略有差异，以你本地 SDK 为准。）
2. 用 **UniFlash** 烧录上述 bin 到 IWR6843AOP。
3. 上电，micro-USB 连 PC。设备管理器出现两个 CDC UART 口：
   - **CLI UART**（115200）：发配置用（默认 demo 可免配置直接出点云）
   - **DATA UART**（921600）：点云帧输出口 —— 采集脚本连这个
4. 跑 `edge/capture_oob.py` 连 DATA UART，解析 OOB TLV，每帧点云存成 `(N,3) float64` 的 `frame*.bin`（格式与 MMFi 完全一致，`train.py` 零改动）。

## 3. 采集脚本用法
```bash
cd 项目根
pip install pyserial numpy          # 采集机只需这俩
python edge/capture_oob.py \
    --port COM5 \                   # 你的 DATA UART 口
    --baud 921600 \
    --out data/radar/E01/S01/A01/mmwave \
    --seconds 30
```
- 跑完生成 `frame0000.bin ... frame00NN.bin`。
- 离线自检（无需硬件）：
  ```bash
  python -c "from backend.app.inference.mmwave_cnn.preprocess import load_mmwave_frames; \
  f=load_mmwave_frames('data/radar/E01/S01/A01/mmwave'); print('帧数',len(f),'首帧',f[0].shape if f else None)"
  ```
  应看到 `帧数 > 0`、形状 `(N, 3)`。

## 4. 活动清单（与 BehaviorAction 对齐，肆月 2026-08-09 锁定 8 类安全集）

> 设计原则（老人安全视角）：凡是长得像跌倒的"安全动作"必须单独成类，逼模型学边界；
> 融合层对"低置信/未知"从"当安全"翻转为"升级视觉确认/持续盯防"，宁误报不漏报。

| A 类 | 动作 | 映射 BehaviorAction | 安全属性 |
|---|---|---|---|
| A01 | 走动 walking | `walking` | 正常 |
| A02 | 站立 standing | `standing` | 正常（从 normal_activity 拆出） |
| A03 | 静坐 sitting | `sitting_still` | 正常 |
| A04 | 躺床休息 lying | `lying` | 正常（需与倒地区分） |
| A05 | 起身 standing_up | `standing_up` | 正常 |
| A06 | 弯腰/蹲下/拾物 crouching | `crouching` | ⚠️ 易误判为跌倒→必须单类（M3 曾误删，已恢复） |
| A07 | 倒地不起 lying_floor | `lying_floor` | 🔴 跌倒后状态=急救（从 lying 拆出） |
| A08 | **跌倒 falling** | `falling` | 🔴 P0 红色警报（MMFi 无，必须自有采集） |

> `normal_activity` 仅作"未知/其他"低置信兜底，不表示安全。

## 5. 采集协议（达标线）
- 每位受试者（subject）每类 **≥10 次重复**，每次 10–30 秒。
- 受试者 **≥3 人**，尽量覆盖不同年龄/体型（贴近老人特征更佳）。
- 环境固定：同一房间布局、雷达高度 1.0–1.5 m、朝向一致（匹配部署场景）。
- 文件夹结构（mirror MMFi，让 `train.py` 零改动）：
  `data/radar/E<环境>/S<subject>/A<class>/mmwave/frame*.bin`
- **标签即文件夹**：不需要单独标注文件，A 序号即标签。

## 6. 跌倒类安全规范（重要）
- `falling` 是 P0 关键类，但**必须安全**：用慢动作"坐/滑/跪/倒"排练 + 地面垫 + 旁人保护，**严禁真实自由落体**。
- 受试者签简易知情同意（校内大创项目，记录年龄/体型区间即可，脱敏）。
- 也可用"模拟跌倒"动作集（快速下蹲 + 侧倒 + 扶墙下滑）替代高风险动作。

## 7. 交付与下一步
- 采集完打包 `data/radar/` 经网盘 / Git LFS 发给 WorkBuddy → 触发 M4 重训（Cursor 跑 `train.py`，验证不同类落到不同行为 + 留出测试集准确率 > 1/N）。
- `weights.pt` 受 `.gitignore` 保护，不进 GitHub，重训后另行分发队友。
- 同时 `RadarPhaseProvider` 接通 OOB 流，让线上系统从 mock 切到真实雷达帧。

## 8. 诚实提醒
- 这是**物理/后勤任务**，不是纯代码：需要实验室空间、受试者、时间、同意。
- 首次烧录 + 首帧解析会有摩擦（波特率/配置/TLV 版本差异），预算 1–2 天调通。
- 标注虽由文件夹隐式完成，但**采集质量（遮挡、距离、重复数）直接决定模型上限**，别凑数。

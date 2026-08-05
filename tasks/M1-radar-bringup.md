# M1 雷达硬件点亮与首帧采集（委托卡）

> 适用阶段：M1（9 月雷达感知）。本卡发给**拿到 IWR6843AOP 硬件的同学**（建议：周震宇，原始数据采集负责人；？？？协助软件联调）。
> 目标：**只把雷达点亮 + 采到能映射数据契约的原始帧 + 跑通 real 通道**。**本阶段不写任何算法**（生命体征/跌倒算法留 M1 后期 / M2）。

---

## 0. 前置清单
- [ ] 硬件：TI IWR6843AOP 评估套件（MMWAVEICBOOST + AOP 天线板，Antenna-on-Package，板载天线免射频调试）
- [ ] 一台 Windows / Linux 电脑 + USB 线
- [ ] TI 账号（用于下载 Industrial Toolbox）；串口工具（Tera Term / Putty / Python pyserial）

## 1. 硬件连线
- MMWAVEICBOOST 接 AOP 天线板，USB 接电脑。
- 设备管理器确认出现 **XDS110 的两个 COM 口**：`User UART`（数据输出）与 `Aux/UART`（烧录/CLI）。
- 常见坑：只看到一个 COM → 没装 XDS110 驱动（下 TI Emulation Software）；供电不足 → 用带源 USB  hubs 或独立供电。

## 2. 烧录 AOP 固件（关键：型号已定 AOP）
- 下载 **TI Industrial Toolbox 4.12**（mmWave SDK 同版本）。
- 取 AOP 专用 out-of-box 固件：`xwr64xxAOP_mmw_demo.bin`（路径在 toolbox 的 `out_of_box` / `mmw` demo 下，**必须 AOP 版**，别用 ISK 的 `xwr68xx` bin）。
- 用 **Uniflash** 烧录到 AOP（选 AOP 设备，波特率默认，烧录后复位）。
- 验收：串口能收到启动日志，无 `error` / `assert`。

## 3. 采集 OOB TLV 数据
- 用 **mmWave Demo Visualizer**（TI 官方，网页/桌面）连 User UART，或直接用 Python 读串口（默认 **波特率 921600**）的 TLV 流。
- 导出几十条帧作**小样本**（不需要多，够联调即可；别导出整夜大文件）。
- TLV 里关注：呼吸/心跳估值、微动（chest displacement）、点云/轨迹 → 这些对应我们契约的 `breath_rate / heart_rate / chest_displacement_mm / motion_flag`。

## 4. 对齐数据契约（§6.1）
把 TLV 字段映射到我们平坦契约（参照 `data/mmfi-sample/collection_parameters.md`）：
```
timestamp_ms          # 帧时间戳(ms)
device_id             # 设备编号，如 RADAR_01
breath_rate           # 呼吸率(次/分)，偶发 null 要兜底(坑B)
heart_rate            # 心率(次/分)
chest_displacement_mm # 胸腔位移(mm)
motion_flag           # 是否有微动(bool)
ahi_index             # 呼吸暂停指数，暂可 null
```

## 5. 软件联调（？？？协助）
- 把样本帧喂进 `backend/app/sources/mmvital_source.py`：**先替换占位 `next_vital()` 为真实 TLV 解析**（M1 后期正式做；本卡只需验证通道能通）。
- 前端切到「真实雷达(占位)」→ 验证后端**写库 + 广播**有效帧。
- 打 `POST /api/edge/behavior`（`{"action":"walking","confidence":0.8}`）验证行为事件落库。
- 验收：大屏实时出数、DB 有 `source=real` 记录。

## 6. 交付物
- [ ] 样本帧放 `data/radar/raw/<日期>/`（已被 `.gitignore` 忽略，**不上 GitHub**）
- [ ] 一份采集参数 + 烧录/采集步骤文档（给陈意豪整理论文「方法」章节）
- [ ] 在群里回报：固件版本、COM 口、波特率、采样时长

---

## 红线（务必遵守）
- 🚫 **不录视频、人脸/画面不上云**（隐私红线 R-P0-03）。只传雷达帧/骨骼 JSON。
- 🚫 样本**不含真实老人隐私数据**：用空房间 / 志愿者标定即可。
- 🚫 本阶段**只点亮 + 采样 + 跑通通道**，生命体征/跌倒算法（mmVital、patient_monitoring CNN）等 M1 后期 / M2 再做，别现在写。

## 验收清单
- [ ] ① 固件烧录成功（AOP 版 bin）
- [ ] ② 串口稳定输出 TLV 帧（921600）
- [ ] ③ 样本帧字段能映射到 §6.1 契约
- [ ] ④ real 通道在本地跑通（写库 + 广播）
- [ ] ⑤ 交付样本 + 文档

## FAQ
- **COM 口冲突 / 打不开**：关掉占用串口的其它软件（Visualizer 只开一个）；确认烧录用 Aux、数据用 User。
- **Uniflash 烧录失败**：板子先进烧录模式（SOP0/1/2 跳线或按复位），再点烧录；检查 bin 是 AOP 不是 ISK。
- **TLV 字段对不上**：以 `data/mmfi-sample` 的 `collection_parameters.md` 为模板，缺的字段先填空并标注，同步给滕家瑞。
- **联调卡住**：把后端报错贴群，黄敬城 / 滕家瑞 跟进。

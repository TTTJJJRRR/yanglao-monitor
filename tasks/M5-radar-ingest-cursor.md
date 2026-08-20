# M5 — 数据前可做的全部代码工作（真实数据接入 + 安全逻辑 + 训练脚手架）

> 给 Cursor 的提示词（Ctrl+L 粘贴）。本任务是**数据未到齐前**就能真刀真枪干、且能用 fixture（标注测试样本）验证的一整段活。
> 关联：M3（已产出单类 `weights.pt`，2 commit 未推送）、M4（周震宇采真实多类数据）、`docs/周震宇-数据采集手把手教程.md`、`docs/雷达数据采集SOP.xlsx`、`edge/capture_oob.py`。
> **目标**：让系统在真实数据到位前，完成「接入就绪 + 保命安全逻辑 + 训练/评估脚手架」三件大事，全部 fixture 可测、零造假。

---

## 0. 你是谁 / 当前状态
你是本项目（江南大学大创「智能康养监测系统」）的远程协作 AI。
- 本地 `main` 上有 **2 个未推送 commit**：`7a60308`（训练并接入 MMFi 雷达行为 CNN）、`82bbcb3`（对齐融合测试）。远程 `origin/main` 落后 2 个。
- 雷达 IWR6843AOP 已到货；队友周震宇正按 SOP 采真实多类点云（目录 `data/radar/E<环境>/S<受试者>/A<动作>/mmwave/frame*.bin`）。**数据尚未到位。**
- 现有真实算法：生命体征 = DFT 周期图（`mmvital_estimator.py`）；视觉跌倒 = BlazePose 几何（`edge/vision_node.py`）；融合 = 双模态规则（`fall_fusion.py`）。行为 CNN 已接入但**仅在单类 A01 上训过，等于不能区分多类**；`RadarPhaseProvider` 读 OOB TLV 仍是 TODO。

## 1. 硬规则（红线，违反即作废）
1. **不编造任何训练数据 / 权重**。测试只能用**明确标注为 fixture** 的合成数据；fixture 一律放 `tests/fixtures/`，**不得进入 `data/radar/`**（那是真实数据目录）。
2. **`BehaviorAction` 枚举已于 2026-08-09 由肆月锁定为 8 类安全集**（`walking` / `standing` / `sitting_still` / `standing_up` / `crouching` / `lying` / `lying_floor` / `falling`，外加 `normal_activity` 作未知兜底）。**直接引用、不要增删成员**；生产模型规范类数 = **8**（MMFi 的 27 类仅作外部校验，不进生产模型）。
3. 准确率/性能指标未实测就写「待评估」，**严禁编造 95%+**。
4. **关键预警产品红线（肆月定）**：跌倒 / 生命体征异常 / 设备离线 这类**关键预警，家属端不可静音、不可关闭**，必须始终送达。相关告警实现必须遵守此约束（不要提供任何「关闭推送」开关）。
5. **Git 工作流（本次重点，务必遵守）：**
   - 所有新工作在 **单一 feature 分支** `feature/radar-predata-safety` 上做。
   - **每个模块一次提交**（commit 粒度 = 一个独立功能/文件组），提交信息格式 `feat(scope): 中文简述`。
   - **不要直接 push `main`**，也不要自行 merge 到 main。
   - 本地 main 上那 2 个未推送 commit 从当前 HEAD 拉分支即自然包含，不要单独再 push main；完成后只 `git push -u origin feature/radar-predata-safety` 等 肆月 review。
   - 提交前 `git status` 确认只暂存本模块相关文件，不混进无关改动。

## 2. 七个模块（各一次提交）

### 模块 1：RadarPhaseProvider —— 真实 OOB TLV 接入
- **文件**：`backend/app/sources/mmvital_source.py`（复用现有文件，不新建）。
- 实现 `RadarPhaseProvider`：
  - 配置开关启用：环境变量 `RADAR_PORT` / `RADAR_BAUD`（默认不启用 → 不连硬件）。
  - **复用 `edge/capture_oob.py` 已验证的 OOB TLV 解析**（MAGIC = `bytes([2,1,4,3,6,5,8,7])`、`HDR_SIZE = 40`、TLV type 1 = 检测点）。把每帧检测点参考距离门相位变化作为 `phase_signal` 喂给 `MmVitalEstimator.estimate()`。
  - 解析失败 / 无配置时**优雅回退** `SyntheticPhaseProvider`，绝不抛未捕获异常导致服务崩。
  - 暴露 `next_vital()`（生命体征）与 `next_frame()`（点云帧）两种取数接口，供生命体征估计与行为 CNN 共用。
- **提交**：`feat(source): 接入 IWR6843AOP 真实 OOB TLV 的 RadarPhaseProvider（无配置回退合成）`
- **验证**：生成 `tests/fixtures/oob_sample.bin`（代码拼一段合法 OOB TLV 字节流，旁附 README 标「TEST FIXTURE, NOT REAL DATA」）。`tests/test_radar_phase.py` 断言能解析出 `>0` 帧且 `estimate_vitals` 跑通。测试支持 `python tests/test_radar_phase.py` 直跑与 pytest。

### 模块 2：多类训练数据加载器 + 训练前达标自检
- **文件**：新建 `backend/app/inference/mmwave_cnn/dataset.py`；按需微调 `train.py`。
- 实现 `RadarDataset`：扫描 `data/radar/E<env>/S<subj>/A<class>/mmwave/frame*.bin` 目录树，按 A 编号（A01–A08）自动映射标签到锁定的 8 类 `BehaviorAction`，返回 `(frames, label)`。**标签即文件夹，无需外部标注文件。**
- `--num-classes` 锁死 **8**（对齐生产模型）；MMFi 27 类仅离线校验，不混生产训练。
- **训练前自检**：`data/radar/` 为空、或类数 `< 5`、或每类帧数 `< 50` 时，`train.py` **直接报错退出**并提示「去采数据」，绝不拿单类硬训。
- 用**合成多类 fixture**（清晰标注，放 `tests/fixtures/mmwave/`，不进 `data/radar/`）跑通 `train.py --dry-run` 或最小 epoch，证明多类路径打通。
- **提交**：`feat(cnn): 多类雷达数据集加载器 + 训练前数据达标自检（<5类/每类<50帧即拒训）`
- **验证**：`tests/test_dataset.py` 断言 fixture 多类被正确加载、标签与文件夹 A 编号一致。

### 模块 3：融合安全翻转（宁误报不漏报）
- **文件**：`backend/app/inference/fall_fusion.py`（改 `fuse()`）。
- 背景：原逻辑雷达低置信时回落 `normal_activity`（视为安全），对跌倒危险——真摔被判成「低置信弯腰/躺」会被静音。
- 改造 `fuse()`：
  - 定义 `FALL_AMBIGUOUS = {crouching, lying, lying_floor}`（与跌倒易混淆的安全动作）。
  - `radar_action ∈ FALL_AMBIGUOUS` 或 `normal_activity`（未知）且 `radar_conf < 0.5` → **不视为安全**，置 `needs_review=True`、`alert_level='yellow'`（持续盯防/视觉复核），记 `watch_reason`。
  - 仅当 `radar_action` 为明确非易混淆正常动作（`walking`/`standing`/`sitting_still`/`standing_up`）且 `radar_conf >= 0.5` 才判安全正常。
  - 跌倒判定（双/单模态）逻辑不变（红/黄警）。返回新增 `needs_review: bool` 与 `watch_reason: str | None`。
- **提交**：`feat(fusion): 低置信易混淆姿态/未知→升级盯防(宁误报不漏报)`
- **验证**：更新 `tests/test_fusion.py` —— 低置信 `crouching`/`normal_activity` → `needs_review=True` 而非安全；明确 `walking` 高置信 → 安全。红/黄警用例不变。

### 模块 4：设备离线告警（失明=致命，必须报）
- **文件**：`backend/app/routers/edge.py`（或新建 `backend/app/monitoring.py` 管连接状态）。
- 实现：按数据源（来源标识）记录最后一次收到帧的时间戳；若某源连续 **N=5 秒**无帧 → 广播 `device_offline` 事件，`alert_level='critical'`。
  - **遵守产品红线**：关键预警家属端不可静音/关闭，必须始终送达（不要在告警 payload 里提供任何可关闭字段）。
  - 恢复收到帧后广播 `device_online` 解除。
- **提交**：`feat(alert): 雷达 N 秒无帧→device_offline 关键告警（家属端不可关闭）`
- **验证**：`tests/test_device_offline.py` —— 用 mock 时钟注入「帧间隔 > 5s」断言广播离线；恢复帧断言解除。测试支持直跑与 pytest。

### 模块 5：视觉跌倒多帧确认（降误报不漏报）
- **文件**：`backend/app/inference/fall_fusion.py` 或新建 `backend/app/inference/fall_confirm.py`。
- 实现轻量时间窗确认：维护最近 K=3 帧的 `fall_score`（来自视觉 / 雷达 falling 概率）；仅当**连续 K 帧** `fall_score > 0.6`（或雷达 falling 高置信）才发红色跌倒告警，否则只记 `watch`（黄）。
  - 单帧尖峰（抖动/弯腰误触发）被滤掉；真跌倒的连续下坠尖峰照常触发。
- **提交**：`feat(vision): 跌倒多帧确认(连续K帧超阈才报,降误报)`
- **验证**：`tests/test_fall_confirm.py` —— 单帧尖峰 → 不报红；连续 3 帧超阈 → 报红；交替分数 → 仅 watch。

### 模块 6：异常输入鲁棒性（空帧/噪声/遮挡不崩）
- **文件**：`backend/app/sources/mmvital_estimator.py`、`backend/app/inference/behavior_classifier.py`、`backend/app/inference/fall_fusion.py` 按需。
- 实现：
  - 空点云 / 空 phase 信号 → `estimate_vitals` 返回 `VitalEstimate(None, None, motion_flag=True, quality=0.0)` 而非崩；`next_frame()` 返回空列表而非异常。
  - 全噪声信号（quality≈0）→ 标记 `motion_flag=True` 交给融合降级处理。
  - 遮挡（点数极少）→ 行为 CNN 走 Stub 路径 / 标记低置信，不抛错。
  - 融合层对 `None` 输入做防御，绝不 `AttributeError`。
- **提交**：`fix(inference): 空帧/噪声/遮挡等异常输入的鲁棒降级(不崩)`
- **验证**：`tests/test_robustness.py` —— 空列表 / 全 0 / 全随机噪声 / 单点 四种输入均不抛异常且返回合理降级值。

### 模块 7：训练 / 评估脚手架（数据一到即用）
- **文件**：`backend/app/inference/mmwave_cnn/preprocess.py`（加 `augment()`）、`backend/app/inference/mmwave_cnn/train.py`（加 k-fold/early-stop/均衡采样）、新建 `backend/app/inference/mmwave_cnn/eval.py`。
- 实现：
  - `augment(frames)`：点云 jitter、绕竖轴随机旋转、时间扭曲；**标签不变**。单测断言形状保持、标签一致（用 fixture）。
  - `train.py` 加：`--folds`（按受试者 k-fold 切分）、`--early-stop`（patience 监控 val loss）、`WeightedRandomSampler` 类别均衡。
  - `eval.py`：加载 `weights.pt`，在留出集上输出 **per-class 准确率 + 混淆矩阵**（用 numpy；无 sklearn 依赖）。现即可用现有单类 `weights.pt` / fixture 验证「能跑通」。
- **提交**：`feat(cnn): 训练增强(增强/k-fold/早停/均衡)+评估脚本(每类准确率+混淆矩阵)`
- **验证**：`tests/test_augment.py` 断言增强后形状/标签正确；`eval.py` 在单类权重上能输出混淆矩阵（本机有 torch/numpy 时运行）。

## 3. 收尾（给 肆月 汇报用）
- 七个模块各一次提交后：`git push -u origin feature/radar-predata-safety`。
- 群里向 肆月 汇报：做了什么、新增测试是否全绿、真实数据到位后重训命令是什么。**不 push main、不自行 merge。**
- 若顺手更新了 `tasks/M4-data-retrain-cursor.md` 顶部状态，改动一并提交到本分支。

## 4. 验收标准（肆月 review 用）
- [ ] 全程单一 feature 分支 `feature/radar-predata-safety`，**7 次提交各对应一个模块**（commit 粒度正确）
- [ ] `RadarPhaseProvider` 能从 OOB 夹具解析出帧；无配置时回退合成、不崩
- [ ] `RadarDataset` 能从目录树按 A 编号加载多类；训练前自检拒绝不达标数据
- [ ] `fuse()` 安全翻转生效：低置信易混淆姿态/未知 → `needs_review=True` 升级盯防，而非静音为安全
- [ ] `device_offline` 关键告警生效且不可关闭；恢复帧解除
- [ ] 跌倒多帧确认生效：连续 K 帧超阈才报红，单帧尖峰不报
- [ ] 空帧/噪声/遮挡输入均不崩、走降级
- [ ] 训练增强 + `eval.py` 能跑通（本机有 torch/numpy）
- [ ] 新增测试 `python tests/test_*.py` 直跑全绿（沙箱无 torch 时，fixture 解析 / 数据集 / 融合 / 离线 / 确认 / 鲁棒性测试必须绿；CNN 训练与 eval 测试需你本机有 torch/numpy）
- [ ] 未增删 `BehaviorAction` 成员、未编造准确率、未 push main

## 5. 诚实提醒
- 真实数据还没采回来，本任务**只打通代码链路 + 用 fixture 验证逻辑**，不碰真实训练。数据到位后由 M4 流程触发真多类重训。
- OOB TLV 偏移按 `capture_oob.py` 标准布局；若本机 SDK 版本不同导致解析异常，汇报里写明，不要改魔数硬凑。
- fixture 再像真数据也只是测试用，绝不允许把 fixture 当训练集交给 `train.py` 产出 `weights.pt`。
- 前端监控大屏打磨（实时波形 / 置信度条 / `device_offline` 横幅 / 关键预警不可关闭 UI）属独立前端任务，另行出卡（M7），本次不涉及。

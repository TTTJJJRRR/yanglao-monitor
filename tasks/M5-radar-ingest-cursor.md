# M5 — 雷达真实数据接入（RadarPhaseProvider）+ 多类训练就绪

> 给 Cursor 的提示词（Ctrl+L 粘贴）。关联：M3（已产出单类 `weights.pt`，2 commit 未推送）、M4（周震宇采真实多类数据）、`docs/周震宇-数据采集手把手教程.md`、`edge/capture_oob.py`。
> 本任务目标：**让系统准备好接收真实 IWR6843AOP 数据**，不依赖训练数据也能把代码链路打通、用明确标注的测试夹具验证。

---

## 0. 你是谁 / 当前状态
你是本项目（江南大学大创「智能康养监测系统」）的远程协作 AI。
- 本地 `main` 上有 **2 个未推送 commit**：`7a60308`（训练并接入 MMFi 雷达行为 CNN）、`82bbcb3`（对齐融合测试）。远程 `origin/main` 落后 2 个。
- 雷达 IWR6843AOP 已到货；队友周震宇正按手把手教程采真实多类点云（目录 `data/radar/E<环境>/S<受试者>/A<动作>/mmwave/frame*.bin`）。
- 现有代码：生命体征用 `SyntheticPhaseProvider`（合成输入→真实 DFT 估计）；行为 CNN 已接入但**仅在单类 A01 上训过，等于不能区分多类**；`RadarPhaseProvider` 读 OOB TLV 仍是 TODO。

## 1. 硬规则（红线，违反即作废）
1. **不编造任何训练数据 / 权重**。测试只能用**明确标注为 fixture** 的合成数据；fixture 一律放 `tests/fixtures/`，**不得进入 `data/radar/`**（那是真实数据目录）。
2. **`BehaviorAction` 枚举已于 2026-08-09 由肆月锁定为 8 类安全集**（`walking` / `standing` / `sitting_still` / `standing_up` / `crouching` / `lying` / `lying_floor` / `falling`，外加 `normal_activity` 作未知兜底）。**直接引用、不要增删成员**；本系统训练/推理的规范类数 = **8**（MMFi 的 27 类仅作外部校验，不进入生产模型）。
3. 准确率/性能指标未实测就写「待评估」，**严禁编造 95%+**。
4. **Git 工作流（本次重点，务必遵守）：**
   - 所有新工作必须在 **feature 分支** 上做，命名 `feature/<模块名>`。
   - **每个模块一次提交**（commit 粒度 = 一个独立功能/文件组），提交信息格式 `feat(scope): 中文简述`。
   - **不要直接 push `main`**，也不要自行 merge 到 main。
   - 当前本地 main 上那 2 个未推送 commit：从当前 HEAD 拉 feature 分支即自然包含它们，**不要单独再 push main**；完成后只 push 该 feature 分支等 肆月 review。
   - 提交前 `git status` 确认只暂存本模块相关文件，不混进无关改动。

## 2. 本次三个模块（各一次提交）

### 模块 1：RadarPhaseProvider —— 真实 OOB TLV 接入
- **文件**：`backend/app/sources/mmvital_source.py`（建议复用现有文件，不新建）。
- **实现 `RadarPhaseProvider`**：
  - 通过配置开关启用：环境变量 `RADAR_PORT` / `RADAR_BAUD`（默认不启用 → 不连硬件）。
  - **复用 `edge/capture_oob.py` 里已验证的 OOB TLV 解析逻辑**（MAGIC = `bytes([2,1,4,3,6,5,8,7])`、`HDR_SIZE = 40`、TLV type 1 = 检测点）。把每帧检测点的参考距离门相位变化作为 `phase_signal`，喂给 `MmVitalEstimator.estimate()`。
  - 解析失败 / 无配置时**优雅回退**到现有 `SyntheticPhaseProvider`，绝不抛未捕获异常导致服务崩。
  - 暴露 `next_vital()`（生命体征）与 `next_frame()`（点云帧）两种取数接口，供生命体征估计与行为 CNN 共用。
- **提交信息**：`feat(source): 接入 IWR6843AOP 真实 OOB TLV 的 RadarPhaseProvider（无配置时回退合成）`
- **验证**：生成**测试夹具** `tests/fixtures/oob_sample.bin`（用代码拼一段合法 OOB TLV 字节流，文件旁 README 标注「TEST FIXTURE, NOT REAL DATA」）。在 `tests/test_radar_phase.py` 中断言 `RadarPhaseProvider` 能从该夹具解析出 `>0` 帧、且 `estimate_vitals` 能跑通。测试同时支持 `python tests/test_radar_phase.py` 直跑与 pytest。

### 模块 2：多类训练数据加载器 + 训练前达标自检
- **文件**：新建 `backend/app/inference/mmwave_cnn/dataset.py`；按需微调 `train.py`。
- **实现 `RadarDataset`**：扫描 `data/radar/E<env>/S<subj>/A<class>/mmwave/frame*.bin` 目录树，按 A 编号（A01–A08）自动映射动作标签到锁定的 8 类 `BehaviorAction`，返回 `(frames, label)`。**标签即文件夹，无需外部标注文件。**
- `--num-classes` 锁死为 **8**（对齐 `BehaviorAction` 8 类生产模型）；MMFi 27 类仅作离线校验，不混入生产训练。
- **训练前自检**：当 `data/radar/` 为空，或类数 `< 5`、或每类帧数 `< 50` 时，`train.py` **直接报错退出**并提示「去采数据」，绝不拿单类硬训。
- 用**合成多类 fixture**（清晰标注，放 `tests/fixtures/mmwave/` 下，**不进 `data/radar/`**）跑通 `train.py --dry-run` 或最小 epoch，证明多类路径打通。
- **提交信息**：`feat(cnn): 多类雷达数据集加载器 + 训练前数据达标自检（<5类/每类<50帧即拒训）`
- **验证**：`tests/test_dataset.py` 断言 fixture 多类能被正确加载、标签与文件夹 A 编号一致。

### 模块 3：融合安全翻转（宁误报不漏报）
- **文件**：`backend/app/inference/fall_fusion.py`（修改 `fuse()`）。
- **背景**：原逻辑在雷达低置信时回落 `normal_activity`（视为安全），对跌倒是危险的——真摔若被判成"低置信弯腰/躺"会被静音，不报警。
- **改造 `fuse()`**：
  - 定义 `FALL_AMBIGUOUS = {crouching, lying, lying_floor}`（与跌倒易混淆的安全动作）。
  - 当 `radar_action` 属于 `FALL_AMBIGUOUS` 或 `normal_activity`（未知）且 `radar_conf < 0.5` 时：**不视为安全**，置 `needs_review=True`、`alert_level='yellow'`（持续盯防/视觉复核），记录 `watch_reason`。
  - 仅当 `radar_action` 为明确非易混淆正常动作（`walking`/`standing`/`sitting_still`/`standing_up`）且 `radar_conf >= 0.5` 时，才判为安全正常。
  - 跌倒判定（双模态/单模态）逻辑保持不变（红/黄警）。
  - 返回字段新增 `needs_review: bool` 与 `watch_reason: str | None`。
- **提交信息**：`feat(fusion): 低置信易混淆姿态/未知→升级盯防(宁误报不漏报)`
- **验证**：更新 `tests/test_fusion.py` —— 新增用例：雷达低置信 `crouching` → `needs_review=True` 而非安全；雷达低置信 `normal_activity` → 升级盯防；明确 `walking` 高置信 → 安全。保持红/黄警用例不变。

## 3. 收尾（给 肆月 汇报用）
- 两个模块各一次提交后：`git push -u origin feature/radar-live-ingest`（分支名按实际模块命名，可合并为 `feature/radar-realdata-ready`）。
- 在群里向 肆月 汇报：做了什么、新增测试是否全绿、真实数据到位后重训命令是什么。**不 push main、不自行 merge。**
- 若顺手更新了 `tasks/M4-data-retrain-cursor.md` 顶部状态，改动一并提交到本分支。

## 4. 验收标准（肆月 review 用）
- [ ] 全程在单一 feature 分支，2 次提交各对应一个模块（commit 粒度正确）
- [ ] `RadarPhaseProvider` 能从 OOB 夹具解析出帧；无配置时回退合成、不崩
- [ ] `RadarDataset` 能从目录树按 A 编号加载多类；训练前自检拒绝不达标数据
- [ ] `fuse()` 安全翻转生效：低置信易混淆姿态/未知→`needs_review=True` 升级盯防，而非静音为安全
- [ ] 新增测试 `python tests/test_radar_phase.py`、`python tests/test_dataset.py`、`python tests/test_fusion.py` 直跑全绿（沙箱无 torch 时，fixture 解析 / 数据集 / 融合测试必须绿；CNN 训练测试需你本机有 torch）
- [ ] 未增删 `BehaviorAction` 成员、未编造准确率、未 push main

## 5. 诚实提醒
- 真实数据还没采回来，所以本任务**只打通代码链路 + 用 fixture 验证逻辑**，不碰真实训练。
- OOB TLV 偏移按 `capture_oob.py` 标准布局；若你本机 SDK 版本不同导致解析异常，在汇报里写明，不要改魔数硬凑。
- fixture 再像真数据也只是测试用，绝不允许把 fixture 当训练集交给 `train.py` 产出 `weights.pt`。

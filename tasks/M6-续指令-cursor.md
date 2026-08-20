# M6 续 · Cursor 执行指令（验收后补齐阻塞项）

> 前置：你之前的进展汇报已由 WorkBuddy 主理人（方向明）扎实验收。本卡基于验收结论，列出**必须补齐的阻塞项**。
> 转发方式：复制全文粘贴进 Cursor（Ctrl+L）。执行人：Cursor（本机，有 torch/numpy）。
> 当前分支：`feature/radar-predata-safety`（已切，勿动）。

## 0. 验收已确认你真做了什么（无需重做）
- `test_fusion` 去重：旧 `backend/tests/test_fusion.py` 已删，根 `tests/test_fusion.py` 保留 ✓
- 后端健壮性修复文件确有改动（`fall_fusion` / `classifier` / `main` / `models` / `mmvital_source` / `sources/__init__`）✓
- M5 模块文件齐全新增（`oob_tlv` / `dataset` / `eval` / `monitoring` / `eemd_vitals` / `capture_oob` + 7 个 test）✓
- 未 push ✓

## 1. 你必须补齐的三件事（按此顺序，前一件不完成不进下一件）

### 阻塞项 A · 提交拆分（最高优先，先固化代码）
当前 **32 个文件**游离 working tree，一个 commit 都没做，违反红线「每模块一次提交」。工作区大量未提交改动是风险源，必须先固化。

- 按模块语义拆成多次提交（建议 ≤10 次，宁可多不可杂），message 格式 `feat(scope): 中文简述` / `fix(scope): 中文简述`。
- 必须把以下全部文件分配进提交，无遗漏、无「大杂烩」单提交：

  **后端 sources / 感知**
  - `backend/app/sources/oob_tlv.py`（新）
  - `backend/app/sources/eemd_vitals.py`（新）
  - `backend/app/sources/__init__.py`（M）
  - `backend/app/sources/mmvital_source.py`（M）
  - `tests/test_radar_phase.py`（新）+ `tests/fixtures/oob/`（新）

  **CNN 数据集 / 训练 / 评估**
  - `backend/app/inference/mmwave_cnn/dataset.py`（新）+ `tests/test_dataset.py`（新）+ `tests/fixtures/mmwave/`（新）
  - `backend/app/inference/mmwave_cnn/{preprocess,train,eval}.py`（新）+ `tests/test_augment.py`（新）
  - `backend/app/inference/mmwave_cnn/classifier.py`（M）+ `tests/test_robustness.py`（新）

  **融合 / 模型 / 监控**
  - `backend/app/inference/fall_fusion.py`（M）+ `backend/app/models.py`（M，critical）+ `tests/test_fusion.py`（新，根目录版）
  - `backend/app/monitoring.py`（新）+ `tests/test_device_offline.py`（新）

  **视觉 / 多帧确认（见阻塞项 B，改完再提交）**
  - `edge/vision_node.py`（待改）+ `tests/test_fall_confirm.py`（待重写）

  **数据采集工具链 / 接入**
  - `edge/capture_oob.py`（新）
  - `backend/app/main.py`（M，接 OOB 流）
  - `docs/_gen_sop.py`（新）+ `docs/卧床老人-数据采集活动清单-*.md`（新）+ `docs/雷达数据采集SOP.xlsx`（新）
  - `backend/tests/test_fusion.py`（D，删除旧版）

  **前端（M6 UI 尚未做，先提交已存在的壳/数据）**
  - `frontend/src/components/`（新）+ `frontend/src/data/`（新）
  - `frontend/src/api/client.ts`（M）+ `frontend/src/styles.css`（M）+ `frontend/src/types.ts`（M）+ `frontend/tailwind.config.js`（M）
  - ⚠️ `App.tsx` 预警渲染待阻塞项 C 完成后**单独提交**

  **文档 / 任务卡**
  - `tasks/M3-cnn-train-cursor.md` / `tasks/M4-data-retrain-cursor.md` / `tasks/M5-radar-ingest-cursor.md` / `tasks/M6-frontend-retrain-cursor.md`（新）
  - `deliverables/product-strategy/opensource-survey-yanglao-2026-08-05.md`（M）

- 每次提交前跑对应测试确认绿；提交后 `git status` 应干净（仅余尚未完成的 M6 UI 文件）。

### 阻塞项 B · 真多帧跌倒确认（P0 安全命门，不可只「梳理方向」）
**验收硬伤**：`fall_fusion.fuse` 仍是**单帧无状态**函数（只看当前帧 `vision_fall_score>=0.6`）；`edge/vision_node.py` 完全没改；`tests/test_fall_confirm.py` 名「confirm」实则测单帧、断言过弱——「34 passed」含水分。

- 真正实现：**连续 ≥3 帧 `fall_score>=0.6` 才报 red 跌倒确认；单帧尖峰只进 watch，不误报**。
- 落点二选一（实现其一即可，但要真接生产代码，不是停留在测试）：
  - (a) 在 `edge/vision_node.py` 的 `VisionNode` 维护滑动窗口，连续 ≥3 帧 high 才输出 `falling` 红警；
  - (b) 在 fusion 调用处外包一个**状态ful** 的 `FallDetector`（维护窗口），聚合雷达 + 视觉时序后判红。
- **重写 `tests/test_fall_confirm.py`**，使其真正覆盖多帧语义（不再测单帧 `fuse`）：
  - `test_single_spike_no_red`：序列 `[0.1, 0.8, 0.1]` 整体**不产生 red 跌倒确认**
  - `test_three_consistent_high`：连续 3 帧 `0.8` → 第 3 帧后 `is_fall=True` 且 `alert_level="red"`
  - `test_alternating_no_red`：交替 `0.2/0.8` 永不累积到 3 帧 → 始终 watch 不 red
- 成功标准：上述测试针对**真实多帧逻辑**全绿；旧的单帧「假绿」测试已被替换。

### 阻塞项 C · 前端 M6 关键预警 UI（纯前端，数据前可做）
后端已能发 `device_offline` / `device_online` / `needs_review` / `watch_reason` / `radar_status` / `pose`。
⚠️ **先确认前端现状**：机构管理端前端框架可能已由 肆月 本机实现（含 WS 预警横幅、`App.tsx` 已重写）。动手前先 `git status` / 读 `frontend/src/App.tsx` 与 `components/`，在现有代码上**补充** `device_offline` / `device_online` / `needs_review` / `watch_reason` 的消费与渲染，**不要重写覆盖**已有框架。把它们变成用户可见的保命界面：

- **模块4 设备离线横幅**：`App.tsx` 消费 WS `device_offline` / `device_online`，顶部红色 **critical 横幅**（「雷达设备离线，监测中断！」），**不可关闭、不可静音**；收到 `device_online` 自动消失。
- **模块5 融合盯防指示**：活动识别面板消费 `needs_review` / `watch_reason`，`needs_review=true` 显示黄色「持续盯防中」徽标 + 原因文案（如「低置信·易混淆姿态」），**不静音、不自动消解**，直到下一帧恢复正常。
- **模块6 生命体征波形 + 模型状态**：接 `MmVitalSource` 真实估计（呼吸/心率），画轻量趋势小图；展示 `model_loaded` 状态与雷达置信度条；标注「生命体征为趋势预警，非医疗级」。
- 成功标准：`tsc --noEmit` + `vite build` 通过；横幅 / 徽标可见；**代码审查确认无关闭/免打扰入口**。

## 2. 红线（沿用，不可破）
- 每模块一次提交，message 合规，无大杂烩。
- **不 push main**：仅 `git push origin feature/radar-predata-safety`，等 肆月 review。
- 不编数据 / 权重 / 准确率：没测写「待评估」，严禁编 95%+。
- 不动 `BehaviorAction` 枚举（9 成员锁死）。
- **关键预警前端零关闭能力**：跌倒 / 生命体征异常 / 设备离线 三类 critical 预警，UI 不得出现任何「关闭 / 免打扰 / 不再提醒」按钮或开关。

## 3. 明确不做（本次）
- 第三部分数据重训（模块7/8）：等周震宇采回真实雷达帧（M4/SOP），门禁（≥5 类 / 每类 ≥50 帧 / ≥3 受试者）通过后另开任务。

## 4. 验收清单（给 肆月 review）
- [ ] `git log` 显示按模块拆分的多次独立提交，无大杂烩；`git status` 干净（除 review 中）
- [ ] `fall_fusion` 或 `vision_node` 含真实多帧窗口逻辑；`test_fall_confirm` 真覆盖多帧语义，全绿
- [ ] 前端 `tsc --noEmit` + `vite build` 通过；设备离线横幅 / 盯防徽标可见；代码审查确认无关闭 / 免打扰入口
- [ ] 未 push main；仅 `feature/radar-predata-safety` 待 review
- [ ] 未动 `BehaviorAction`、未编准确率

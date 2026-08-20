# M6 · M5 收尾 + 前端关键预警 UI + 数据到位重训

> 关联：`M5`（feature/radar-predata-safety，7 模块代码已完成但未提交）、`M4`（数据获取）、`docs/data-collection-protocol.md`、`docs/雷达数据采集SOP.xlsx`
> 执行人：Cursor（本机，有 torch/numpy）
> 转发方式：复制本文粘贴进 Cursor（Ctrl+L）

## 0. 背景与当前状态（先读，避免重复踩坑）

`feature/radar-predata-safety` 分支上 M5 的 7 个模块**代码已写完且 34 测通过**，但 肆月 亲自核对后发现三处必须收尾的隐患，本卡第一部分就是修这些。

已核实的真实现状（肆月 2026-08-09 在沙箱实测）：
- `oob_tlv.py` 真实存在（`parse_frame`/`iter_frames`/`build_oob_frame`），且 `mmvital_source.py` 已 `from .oob_tlv import iter_frames` 并在 `RadarPhaseProvider.next_frame` 中使用 → **模块1真实可用**，非脚手架。
- `fall_fusion.py` 确有 `needs_review`/`watch_reason`；`monitoring.py` 确有 `device_offline`/`device_online`（level=critical）。
- `BehaviorAction` 仍是锁定 9 成员（8 类 + normal_activity），未动。
- `models.py` 仅新增 `AlertLevel.critical`；`classifier.py` 仅加了 torch 张量直传的健壮性判断。

**三处隐患（必须修）：**
1. 25 个文件全在 working tree，**一个 commit 都没做** → 违反 M5「每模块一次提交」。
2. 存在两份 `test_fusion.py`：`backend/tests/test_fusion.py`（8-06 旧版，与新 fuse 契约冲突 FAIL 1）与 `tests/test_fusion.py`（Cursor 新版，通过）→ 必须去重。
3. `vision_node.py` **从未被改**，模块5「跌倒多帧确认」只停留在孤立测试，没接进生产视觉管线。

## 红线（沿用 M5，不可破）
- **每模块一次提交**，message 格式 `feat(scope): 中文简述`。
- **不 push main**：只 `git push origin feature/radar-predata-safety` 等 肆月 review。
- **不编数据/权重/准确率**：没测就写「待评估」，严禁编 95%+。
- **不动 `BehaviorAction` 枚举**（9 成员锁死）。
- **关键预警前端零关闭能力**：跌倒 / 生命体征异常 / 设备离线 三类 critical 预警，UI 不得出现任何「关闭 / 免打扰 / 不再提醒」按钮或开关（产品硬红线，之前已定）。

---

## 第一部分 · M5 收尾（先做，阻塞合并）

### 模块 1 · 按模块提交 M5
把当前分支 25 个未提交文件，按 M5 的 7 个模块拆成 **7 次提交**（建议顺序与对应文件）：
1. `feat(sources)`: `backend/app/sources/oob_tlv.py` + `tests/test_radar_phase.py` + `tests/fixtures/oob/`
2. `feat(cnn)`: `backend/app/inference/mmwave_cnn/dataset.py` + `tests/test_dataset.py` + `tests/fixtures/mmwave/`
3. `feat(fusion)`: `backend/app/inference/fall_fusion.py` + `tests/test_fusion.py`（用根目录新版）+ `backend/app/models.py`(critical)
4. `feat(alert)`: `backend/app/monitoring.py` + `tests/test_device_offline.py`
5. `feat(vision)`: `edge/vision_node.py`（见模块3）+ `tests/test_fall_confirm.py`
6. `fix(inference)`: `tests/test_robustness.py` + `backend/app/inference/mmwave_cnn/classifier.py`(detach 健壮性)
7. `feat(cnn)`: `backend/app/inference/mmwave_cnn/{preprocess,train,eval}.py` + `tests/test_augment.py`

每次提交前跑对应测试确认绿。提交后 `git status` 应干净（除 M6 新文件）。

### 模块 2 · 去重 test_fusion
删除过时的 `backend/tests/test_fusion.py`（8-06 版，已与新契约冲突），保留 `tests/test_fusion.py`（与新 `needs_review` 契约一致）。
**统一测试目录**：全部测试收口到 `backend/tests/`（与既有 4 个测试一致），或保留根 `tests/` 但确保无重复文件名。选一种并跑全量确认绿。

### 模块 3 · 接通多帧跌倒确认（补齐模块5）
`tests/test_fall_confirm.py` 测试的是「连续 N 帧 fall_score 超阈才报红」的**期望行为**，但 `vision_node.py` 没改 → 把该逻辑真正写进 `vision_node.py`（或 fusion 调用处），让测试覆盖的是生产代码。落点：`VisionNode` 维护一个滑动窗口，连续 ≥3 帧 `fall_score>0.6` 才输出 `falling` 红警；单帧尖峰只进 `watch`，不误报。

---

## 第二部分 · 前端关键预警 UI（数据前可做，纯前端）

> 后端已能发 `device_offline`/`device_online`/`needs_review`/`watch_reason`/`radar_status`/`pose`，但前端 `App.tsx` 目前**没渲染**这些。本部分把它们变成用户可见的保命界面。

### 模块 4 · 设备离线横幅
`App.tsx` 消费 WS 消息 `device_offline`/`device_online`：顶部红色 **critical 横幅**（「雷达设备离线，监测中断！」），**不可关闭、不可静音**；收到 `device_online` 自动消失。

### 模块 5 · 融合盯防指示
活动识别面板消费 `needs_review`/`watch_reason`：当 `needs_review=true` 显示黄色「持续盯防中」徽标 + 原因文案（如「低置信·易混淆姿态」），**不静音、不自动消解**，直到下一帧恢复正常。

### 模块 6 · 生命体征波形 + 模型状态
接 `MmVitalSource` 真实估计（呼吸/心率），画轻量趋势小图；展示 `model_loaded` 状态与雷达置信度条。标注「生命体征为趋势预警，非医疗级」。

---

## 第三部分 · 数据到位后（周震宇采回真实帧，见 M4/SOP）

### 模块 7 · 真多类重训
`RadarDataset` 门禁通过（≥5 类 / 每类 ≥50 帧 / ≥3 受试者）→ 跑 `train.py` 产出**真能区分**的 `weights.pt`（直接覆盖旧单类权重，反正被 `.gitignore` 拦着）→ `eval.py` 出每类准确率 + 混淆矩阵，结果写进 commit message（**严禁编 95%+，没测写「待评估」**）。

### 模块 8 · RadarPhaseProvider 吃真帧 + 端到端
设 `RADAR_PORT` 指向真实雷达，后端从 mock 切真实流；联调后做一次**诚实实时演示**：明确标注哪些是真的（生命体征/视觉几何/融合规则/设备离线）、CNN 多类是否真区分，不糊弄。

---

## 验收清单（给 肆月 review 用）
- [ ] `python tests/test_*.py` 全绿（沙箱无 numpy/torch 时 fixture 类必须绿；CNN 训练测试需本机 torch）
- [ ] 7 次模块提交各自独立、message 合规；无「大杂烩」提交
- [ ] 无重复 `test_fusion`；测试目录统一
- [ ] `vision_node.py` 已含多帧确认；`test_fall_confirm` 覆盖生产代码
- [ ] 前端 `tsc --noEmit` + `vite build` 通过；设备离线横幅/盯防徽标可见
- [ ] 前端关键预警**无关闭/免打扰入口**（代码审查确认）
- [ ] 未 push main；仅 push `feature/radar-predata-safety`
- [ ] 未动 `BehaviorAction`、未编准确率

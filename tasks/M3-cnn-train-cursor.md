# M3 指挥：把毫米波行为 CNN 真正训练出来（补全 M2 未完成项）

> 委托对象：本机 Cursor（粘贴到 Cursor 对话框 Ctrl+L 执行）
> 指挥：滕家瑞（肆月） / 由 WorkBuddy 代拟
> 关联：上一份 `tasks/M2-mmwave-cnn-cursor.md`（已部分完成，但**核心交付缺失**）

---

## 0. 现状复盘（为什么要这份新指挥）

上次 M2 委托卡要求你做的事，核对实际产物后结论如下：

| 要求 | 状态 | 证据 |
|---|---|---|
| 重构/增强 `preprocess.py` 数据管线 | ✅ 已做（质量尚可） | `load_mmwave_frames` 加了帧号排序、float32/64 兼容、NaN 过滤；`voxelize_frame` 加了形状校验 + `np.add.at` 向量化；`preprocess_sequence` 加了 `t_frames<=0` 校验与零填充 |
| 重构 `BehaviorAction` 枚举契约 | ✅ 已做（但**未 commit、未同步文档**） | `still`→`normal_activity`、删 `crouching`、加 `sitting_still/standing_up`；`VitalSource` 加 `mmfi`；生命体征字段改 nullable；`bus.py`/`main.py` 新增 `/ws/stream?source=` 分流 |
| **训练 CNN 产出 `weights.pt`** | ❌ **没做** | 全仓库无任何 `.pt`；`train.py`/`classifier.py`/`model.py` 未被修改；`git log` 无新提交 |
| **commit + 收尾** | ❌ 没做 | `git status` 显示 10 个文件未提交改动 |

**结论：你改了"水管"（数据管道、枚举、WS 分流、前端映射），但没接"水龙头"（训练出能推理的权重）。**

诚实边界（肆月硬性要求）：**宁可交付"显式空挡 Stub"，也不能把占位/随机伪造成"训练好的模型"。** 当前后端 `main.py` 启动时会 try `register_classifier(MmWaveBehaviorCNN())`，`weights.pt` 缺失就自动保持 Stub（503 诚实拒绝）——这是对的，保持。

---

## 1. 本次目标（唯一硬交付）

**产出 `backend/app/inference/mmwave_cnn/weights.pt`，并验证 `MmWaveBehaviorCNN.classify()` 返回真实 softmax 推理结果（非随机、非占位）。**

---

## 2. 前置条件（先自查，不满足就停并回报）

1. 本机 Python 环境已装 `torch` + `numpy`（`preprocess.py` 已 import numpy，应已具备；torch 按 `requirements-ml.txt` 装）。
2. 有真实 mmwave 点云数据，二选一：
   - **朋友本机**：`D:\S01\S01\A01\mmwave\`（297 帧/模态，每帧 `frame*.bin`）；或
   - **公开 MMFi 全量**：从官方取 `E*/S*/A*/mmwave/frame*.bin`（注意：MMFi 的 A 类 = 27 种康复/日常动作，**不含 falling**）。
3. 若两者都拿不到 → **停止并回报**，不要伪造数据或权重。

---

## 3. 执行步骤（自包含）

### 3.1 数据校验
```bash
cd 项目根
python - <<'PY'
from backend.app.inference.mmwave_cnn.preprocess import load_mmwave_frames
frames = load_mmwave_frames(r"你的/mmwave/帧目录")
print("帧数:", len(frames), "首帧形状:", frames[0].shape if frames else None)
PY
```
- 必须能看到 `帧数 > 0` 且每帧是 `(N, 3)` 浮点。否则先修 `preprocess.py` 的数据读取（不要瞎猜 dtype/点数）。

### 3.2 对齐枚举契约（重要，别再悄悄改）
当前 `BehaviorAction` 已是 6 类：`walking / falling / sitting_still / standing_up / lying / normal_activity`。
- `model.py` 的 `MmWaveCNN` 输出头 **n_classes 必须与数据标签数对齐**（MMFi 27 类则 27；若只训 6 类则 6）。
- `classifier.py` 的 MMFi→`BehaviorAction` 映射**只可映射到现有 6 类**，不得引入新枚举值。
- `falling` 类 MMFi **没有**，留待 M1 硬件数据；训练时 falling 行可为 0 样本或单独标注集，不要编造 falling 样本。

### 3.3 训练（先小步跑通，再正式训）
- 修改/运行 `train.py`：枚举数据集 → `preprocess_sequence` → `MmWaveCNN` → 存 `weights.pt`。
- 若 `train.py` 当前实现与新枚举/数据不匹配，**先改 `train.py` 让它跑通**，不要绕过去。
- 小数据集上先 `epoch=2` 验证 loss 下降、能 `save`；再正式训。
- 保存路径固定为 `backend/app/inference/mmwave_cnn/weights.pt`（已被 `.gitignore` 忽略，勿强行入库）。

### 3.4 验证 classify 真实可用（红线：必须做）
```bash
python - <<'PY'
from backend.app.inference.behavior_classifier import register_classifier, get_classifier
from backend.app.inference.mmwave_cnn.classifier import MmWaveBehaviorCNN
from backend.app.inference.mmwave_cnn.preprocess import load_mmwave_frames, preprocess_sequence
register_classifier(MmWaveBehaviorCNN())
clf = get_classifier()
frames = load_mmwave_frames(r"你的/mmwave/帧目录")
seq = preprocess_sequence(frames)
pred = clf.classify(__import__("backend.app.inference.behavior_classifier", fromlist=["RadarFrame"]).RadarFrame("RADAR_01", 0, seq))
print("action:", pred.action, "conf:", round(pred.confidence, 3))
assert pred.confidence > 0 and pred.confidence <= 1
print("OK: 真实推理输出（非随机）")
PY
```
- 必须看到 `OK: 真实推理输出`。
- 同一样本多次推理结果应**稳定一致**（确定性权重，非随机）。

### 3.5 收尾 commit（把 M2 的枚举重构 + 本次训练成果一起收口）
- `git status` 当前有 10 个未提交改动（你上次 M2 留下的）；**不要只 commit 训练相关**，把枚举契约重构一并提交，并在 message 里写清：
  - 枚举已从 `still` 重构为 `normal_activity`、删 `crouching`、加 `sitting_still/standing_up`；
  - 前端/WS/数据源已同步；
  - **`weights.pt` 已产出并验证 classify 真实可用**（或若仍缺，必须诚实写明"仍待 weights.pt"）。
- **push 前先停**：等肆月确认后再 `git push origin main`。不要把半成品/未验证产物直接推上去。
- 顺手把我之前挂在 `test_fusion.py` 的 1 个失败用例（`test_low_conf_radar_falls_back_to_still` 断言 `still`）对齐新枚举（`normal_activity`），保证测试全绿再交付。

---

## 4. 验收标准（肆月会逐条核对）

- [ ] `weights.pt` 存在且能被 `MmWaveBehaviorCNN` 加载
- [ ] `classify()` 返回真实 softmax 结果，同输入稳定一致，confidence∈(0,1]
- [ ] `n_classes` 与数据标签数对齐；枚举零新增
- [ ] 后端 `main.py` 启动日志显示"雷达行为 CNN 已接入"，不再 503
- [ ] 前端"活动识别"面板 `model_loaded=true`，行为标签用新枚举
- [ ] 所有测试（pytest / 各 `__main__`）全绿
- [ ] commit message 诚实写明训练数据与准确率（**不编造准确率**，没测就写"待评估"）
- [ ] **未 push**（等肆月确认）

---

## 5. 红线（违反即视为失败交付）

1. **绝不伪造准确率**：没有在真实/公开数据上评估出的数字，一律写"待评估"，不得凭空写 95%+。
2. **绝不把占位/随机输出当训练成果**：`weights.pt` 必须来自真实反向传播，不是手写常量。
3. **不破坏 `BehaviorAction` 契约**：不得再新增/删除枚举值，除非先回这份指挥确认。
4. **`falling` 留待 M1**：MMFi 无跌倒样本，训练集不得编造 falling。
5. **未 push**：push 权限归肆月，擅自 push 视为越界。

---

## 6. 交付后回报格式（粘贴回群里给肆月）

```
M3 CNN 训练完成：
- 数据来源：朋友D盘 / 公开MMFi（二选一，写明）
- 训练类数：N 类（映射到的 BehaviorAction 子集）
- weights.pt：已产出（路径+大小）
- classify 验证：同输入稳定，真实推理 ✅
- 准确率：X%（测试集）/ 待评估（若未测）
- 测试：全绿
- git：已 commit（hash），未 push（等肆月确认）
```

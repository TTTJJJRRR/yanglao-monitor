# M4 指挥：获取真实多类 mmWave 数据 + 重训行为 CNN（解锁"真能区分行为"）

> 委托对象：本机 Cursor（粘贴到 Cursor 对话框 Ctrl+L 执行）／ 数据获取部分需肆月或周震宇配合
> 指挥：滕家瑞（肆月） / 由 WorkBuddy 代拟
> 关联：`M2`（管线+首训 placeholder）、`M3`（已产出 `weights.pt`，但**单类，等于没用**）
> 🔥 **雷达已到货（2026-08-07）**：数据获取改为**以自有 IWR6843AOP 采集为主**（见 `docs/data-collection-protocol.md` + `edge/capture_oob.py`），MMFi 降为校验/补充集。本卡重训步骤不变，仅数据来源优先级调整。

---

## 0. 现状复盘（为什么必须要这份卡）

M3 你已经交出了 `weights.pt`（118KB，合法 torch 检查点，结构没问题），**但诚实结论是：它只在 A01 单类上训过**。

- 模型输出头虽是 27 类，但训练样本只有 A01 一类 → **它实际分辨不出 walking/sitting/lying/…**，等同于"看起来不是 stub 的 stub"。
- Cursor 自己在 M3 commit message 里也写了 *"local sample contains only A01, so accuracy remains pending"* —— 透明，但事实是：雷达"行为识别"目前**功能为空**。
- 沙箱（离线、无 torch）只能验证"检查点结构合法 + 16 测试全绿 + 后端 import 正常"，**无法实跑 classify 确认它真能区分**。

**本卡唯一目标：把数据补齐到多类，重训出"对同一输入稳定、对不同类有区分度"的模型。** 这是让行为识别从装饰变功能的唯一路径。

---

## 1. 本次目标（硬交付）

1. **拿到覆盖多类的真实 mmWave 数据**（MMFi 27 类里尽可能多，至少 ≥5 类且有量）。
2. **重训 `MmWaveCNN`，产出新的 `weights.pt`**，使模型在**留出测试集**上准确率明显高于 1/N 随机基线。
3. **验证"能区分"**：A01 样本与 A12（深蹲）等其他类样本，推理结果应落到**不同**行为、且置信度非恒定。

---

## 2. 数据获取（优先级：C > B > A，类越多越好）

### 方案 C — 自有 IWR6843AOP 采集（★ 首选，雷达已到货 2026-08-07）
- 见 `docs/data-collection-protocol.md` + `edge/capture_oob.py`：周震宇烧录 AOP 固件 → 连 DATA UART → 脚本把每帧点云存成 `(N,3) float64` 的 `frame*.bin`。
- 优点：**我们的部署场景数据** + **能采到 MMFi 没有的 `falling` 类**（安全排练）。
- 文件夹结构 mirror MMFi：`data/radar/E<env>/S<subject>/A<class>/mmwave/frame*.bin`，`train.py` 零改动。
- 达标线：≥5 类、每类 ≥50 帧、≥3 受试者（详见规程文档第 5 节）。

### 方案 A — 朋友本机 D 盘全量（次选）
M2 卡里朋友的数据只在本地 `D:\S01\S01\A01\mmwave\` 暴露了 A01。**这次必须拿到完整的 MMFi 树**：
```
D:\<E>\Sxx\Axx\mmwave\frame*.bin      # 例：E01/S01/A01 ... E01/S05/A12 ... 覆盖多个 A 类
```
- 让肆月/周震宇把朋友 D 盘里 **所有 A 类目录** 拷到本机一个统一根目录 `<ROOT>`。
- 至少覆盖 A01–A05 + 几个差异大的动作（如 A12 深蹲、A15 弯腰、A20 躺/坐类），越多越好。
- **只拷到 A01 就停**＝和现在一样没用，务必多类。

### 方案 B — 下载公开 MMFi 全量（最稳，27 类齐全）
- 仓库：https://github.com/ybhbingo/MMFi_dataset （Google Drive / Baidu 链接在 README）
- 解压后得到 `<ROOT>/E01/.../A27/mmwave/frame*.bin`（27 类日常/康复动作）。
- 注意：**MMFi 不含 falling**，跌倒类留待 M1 硬件数据，不要编造。

> 若 A、B 都拿不到 → **停止并回报**，不要伪造数据或权重。拿不全 27 类没关系，但**绝不能只有 1 类**。

---

## 3. 执行步骤（自包含）

### 3.1 数据清点（先确认"多类"再训）
```bash
cd 项目根
python - <<'PY'
from pathlib import Path
import re
ROOT = Path(r"你的/数据/根目录")
classes = set()
frames_total = 0
for d in ROOT.glob("**/mmwave"):
    m = re.search(r"/(A\d+)/mmwave$", str(d).replace("\\", "/"))
    if m:
        n = len(list(d.glob("frame*.bin")))
        if n:
            classes.add(m.group(1)); frames_total += n
print("类数:", len(classes), "总帧数:", frames_total)
print("类列表:", sorted(classes))
PY
```
- **类数必须 ≥5 且总帧数足够**（每类建议 ≥50 帧才算能训）。否则回去补数据，别硬训。

### 3.2 对齐契约（别再悄悄改枚举）
- 当前 `BehaviorAction` 6 类：`walking / falling / sitting_still / standing_up / lying / normal_activity`。
- `model.py` 的 `MmWaveCNN` 输出头 **n_classes = 你实际拥有的数据类数**（27 全量就 27；只有子集就子集）。
- `classifier.py` 的 MMFi→`BehaviorAction` 映射**只可映射到现有 6 类**，不得引入新枚举值。
- `falling` 类 MMFi 没有，训练集不得编造 falling 样本。

### 3.3 重训（覆盖旧的单类权重）
- 旧 `weights.pt`（单类）没用，**直接覆盖**即可（已被 `.gitignore` 保护，不会被误提交）。
- 修改/运行 `train.py`：枚举多类数据集 → `preprocess_sequence` → `MmWaveCNN` → 存 `weights.pt`。
- 必须做 **train/val 划分**（按样本或按序列留 10–20% 作测试集），用于 3.4 验证。
- 小步先 `epoch=2` 看 loss 下降、能 `save`；再正式训（30+ epoch，GPU 优先）。
- 保存路径固定：`backend/app/inference/mmwave_cnn/weights.pt`。

### 3.4 验证"真能区分"（红线：必须做，且要比 M3 严）
```bash
python - <<'PY'
import sys; sys.path.insert(0,'.')
from backend.app.inference.behavior_classifier import register_classifier, get_classifier, RadarFrame
from backend.app.inference.mmwave_cnn.classifier import MmWaveBehaviorCNN
from backend.app.inference.mmwave_cnn.preprocess import load_mmwave_frames, preprocess_sequence
register_classifier(MmWaveBehaviorCNN())
clf = get_classifier()
for tag, d in [("A01", r"..A01/mmwave"), ("A12", r"..A12/mmwave"), ("A15", r"..A15/mmwave")]:
    seq = preprocess_sequence(load_mmwave_frames(d))
    p = clf.classify(RadarFrame("RADAR_01", 0, seq))
    print(tag, "->", p.action.value, "conf:", round(p.confidence,3))
# 断言：不同类应落到不同行为（或至少 confidence 分布非恒定）
PY
```
- 必须看到**不同 A 类落到不同行为**、且同输入多次推理**稳定一致**。
- 在 **留出测试集** 上算整体准确率，必须 **> 1/N 随机基线**（N=类数）才有资格说"真能区分"。

### 3.5 收尾 commit（诚实写明多类 + 准确率）
- 把本次重训相关改动一并提交；message 必须写：
  - 数据来源（朋友 D 盘全量 / 公开 MMFi，写明类数与总帧数）；
  - **训练类数 N、留出测试集准确率 X%（或"待评估"若真没测）**；
  - 旧单类权重已覆盖。
- **push 前先停**：等肆月确认后再 `git push origin main`。
- 确认 `backend/tests/` 全部绿（pytest 或 `__main__`）。

---

## 4. 验收标准（肆月逐条核对）

- [ ] 数据类数 ≥5、每类帧数足够（清点脚本确认）
- [ ] `weights.pt` 覆盖旧单类权重，能被 `MmWaveBehaviorCNN` 加载
- [ ] 不同 A 类样本推理落到**不同**行为，同输入稳定一致
- [ ] 留出测试集准确率 **> 1/N 随机基线**（给出具体数字 + 混淆情况）
- [ ] 后端启动日志"雷达行为 CNN 已接入"，不再 503
- [ ] 前端"活动识别"面板 `model_loaded=true`，行为标签随真实推理变化（非恒值）
- [ ] 所有测试全绿
- [ ] commit message 诚实写明训练数据与准确率（**不编造**，没测就"待评估"）
- [ ] **未 push**（等肆月确认）

---

## 5. 红线（违反即失败交付）

1. **绝不只训单类**：只有 1 类数据就停，回报缺数据，不要交"看起来能跑但分不出行为"的权重。
2. **绝不伪造准确率**：没在留出测试集评估出的数字，一律"待评估"，不得写 95%+。
3. **绝不把占位/随机当成果**：`weights.pt` 必须来自真实多类反向传播。
4. **不破坏 `BehaviorAction` 契约**：不得新增/删除枚举值，除非先回这份指挥确认。
5. **`falling` 留待 M1**：MMFi 无跌倒样本，训练集不得编造 falling。
6. **未 push**：push 权限归肆月。

---

## 6. 交付后回报格式（粘贴回群给肆月）

```
M4 数据获取+重训完成：
- 数据来源：朋友D盘全量 / 公开MMFi（二选一，写明）
- 训练类数：N 类（总帧数 M）
- weights.pt：已覆盖旧单类权重（路径+大小）
- 区分验证：A01→X / A12→Y / A15→Z（不同类落到不同行为）✅
- 留出测试集准确率：X%（或 待评估）
- 前端 model_loaded：true，行为随推理变化
- 测试：全绿
- git：已 commit（hash），未 push（等肆月确认）
```

---

## 7. 队友协同备注（非 Cursor 职责）
- `weights.pt` 被 `.gitignore` 忽略，**队友 pull 不到**。重训后由肆月走网盘 / Git LFS 发给周震宇、万砚佶等。
- M1 雷达到位后（周震宇采 IWR6843AOP 真实帧），`RadarPhaseProvider` 读 OOB TLV 替换合成相位，届时行为识别接的是真实硬件流而非 MMFi 离线数据。

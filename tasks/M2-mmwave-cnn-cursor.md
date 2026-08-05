# M2 委托卡：MMFi mmwave 行为 CNN 训练（交 Cursor 执行）

> 委托方：滕家瑞（肆月）／ WorkBuddy
> 执行方：Cursor（本机运行，有 GPU + 可下载数据）
> 模式：本卡为自包含任务书，直接粘贴进 Cursor 的 Chat（Ctrl+L）执行即可。
> 背景：后端已留好 `BehaviorClassifier` 空挡接口（`backend/app/inference/behavior_classifier.py`），
>       本任务把**真实 mmWave 行为 CNN** 训练出来并接入该接口。项目不止跌倒，活动监测全覆盖，
>       故用朋友找到的 MMFi 数据集（27 类日常/康复动作）作训练数据。

## 目标
在 MMFi 的 `mmwave` 模态上训练 `MmWaveCNN`，产出 `weights.pt`，使
`MmWaveBehaviorCNN`（实现 `BehaviorClassifier`）能对一帧雷达点云序列输出**真实**行为预测
（不是随机/伪造）。验证：`classify()` 在若干样本上的预测与 MMFi 真值动作一致（准确率 > 随机基线）。

## 已就位的代码（无需重写，直接复用）
- `backend/app/inference/mmwave_cnn/preprocess.py`：点云序列 -> (T,2,H,W) 体素化（已写好，可微调网格/量程）
- `backend/app/inference/mmwave_cnn/model.py`：MmWaveCNN（baseline 3 层 2D CNN + 时序平均池，27 类头）
- `backend/app/inference/mmwave_cnn/classifier.py`：MmWaveBehaviorCNN（接 BehaviorClassifier，惰性 import torch）
- `backend/app/inference/mmwave_cnn/train.py`：训练脚本（枚举 `E*/S*/A*/mmwave/frame*.bin`，标签=A 序号）
- `backend/app/inference/mmwave_cnn/requirements.txt`：torch / numpy / scipy / pyyaml

## 执行步骤
1. **取数据**（二选一，优先 a）：
   - a) 朋友本机 `D:\S01\S01\A01\mmwave\`（及其他样本）拷贝到本地，按 MMFi 结构放：
        `<ROOT>/E01/S01/A01/mmwave/frame*.bin` …（需要多个 A 类才能多分类；至少一个 A 类也能跑通管线）
   - b) 下载完整 MMFi_Dataset（Google Drive / Baidu，见 https://github.com/ybhbingo/MMFi_dataset ），
        解压后得到 `<ROOT>/E01/.../A27/mmwave/...`。
2. **建环境**（与 backend 同 Python 3.13 推荐）：
   ```
   cd backend
   python -m venv .venv-cnn
   .venv-cnn\Scripts\activate
   pip install -r app/inference/mmwave_cnn/requirements.txt
   ```
3. **训练**（GPU 优先）：
   ```
   PYTHONPATH=. python -m backend.app.inference.mmwave_cnn.train <ROOT> --epochs 30 --batch-size 16
   ```
   观察 loss 是否下降、最终 val 准确率。若显存不够调小 `--batch-size` / `T_FRAMES`。
4. **验证真实推理**（关键，禁止伪造）：
   ```
   PYTHONPATH=. python -c "
   import sys; sys.path.insert(0,'.')
   from backend.app.inference.mmwave_cnn.classifier import MmWaveBehaviorCNN
   from backend.app.inference.behavior_classifier import RadarFrame
   c = MmWaveBehaviorCNN()  # 加载刚训练的 weights.pt
   for d in ['<ROOT>/E01/S01/A01/mmwave','<ROOT>/E01/S02/A12/mmwave']:
       p = c.classify(RadarFrame(device_id='R', timestamp_ms=0, signature=d))
       print(d, '->', p.action.value, p.confidence)
   "
   ```
   确认输出动作与样本真实 A 类合理对应（如 A12 深蹲应映射 crouching），置信度非恒定。
5. **接入系统**：确认后端 `POST /api/edge/radar-frame` 在 `register_classifier(MmWaveBehaviorCNN())`
   后返回真实行为（不再是 503）。注册代码加在 `backend/app/main.py` 启动处（模型权重存在时）。

## 成功标准（务必真实，不得粉饰）
- [ ] loss 收敛、val 准确率明显高于 1/27 随机基线
- [ ] `classify()` 在多个样本输出合理且非恒定的行为/置信度
- [ ] `weights.pt` 生成并被 `MmWaveBehaviorCNN` 成功加载
- [ ] 在报告中给出**具体准确率数字 + 混淆情况**，不要写"已成功"之类空话

## 红线
- 不伪造结果：若数据不足/训练失败，如实报告，不要编准确率。
- 不改动 `BehaviorClassifier` 接口契约（输出必须是 `BehaviorAction` + confidence）。
- 模型仅用 MMFi 公开数据；如涉及隐私样本需确认已脱敏。
- `falling` 类 MMFi 不含，留待 M1 硬件（IWR6843AOP）采真实跌倒数据补充，不要强行映射。

## 可调优方向（你判断）
- 表征：当前是体素占据图 baseline；可改微多普勒谱 / PointNet / 时序 3D CNN 提升精度。
- 时间建模：当前时序平均池，可换 LSTM / 1D 时序卷积。
- 数据增强：点云抖动、帧采样扰动。

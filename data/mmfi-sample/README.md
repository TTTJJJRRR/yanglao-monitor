# data/mmfi-sample · MMFi 验证包（流程验证用，非最终数据集）

来源：队友朋友提供，基于公开 MMFi 多模态动作数据集的 `E01/S01/A01` 样例 + 项目格式临时接口文件。

## 本目录文件

- `radar_sample.jsonl`：雷达样例，10 行（朋友目前只给了前 10 行）。平坦 JSON，每行一个雷达帧。
  字段：`timestamp_ms` / `frame_id` / `device_id` / `subject_id` / `range_bin(*)` / `breath_rate(*)`
  / `heart_rate(*)` / `chest_displacement_mm(*)` / `motion_flag` / `ahi_index(*)` / `scene` / `note`
  （带 `*` 的字段当前为 `null` —— MMFi 无生命体征真值，朋友未伪造）。
- `meta_project.json`：7 模态各 297 帧、fps=20、合成时间戳；`privacy_status: do not upload raw RGB to cloud`。
- `labels_project.json`：动作标签占位，`project_action` 当前为 `null`（尚未映射到本项目 6 类动作）。
- `collection_parameters.md`：空白采集参数模板（真实值待周震宇填写）。
- `README_project_delivery.md`：朋友的原始交付说明。

## 用途与边界

- **仅用于验证"读取样例 → 解析 → 推送前端"管道**：后端 `app/data_source.py` 的 mmfi 模式循环读取本文件并广播（不落库）。
- 生命体征全 `null`、无行为/表情标签、场景非养老 → **不是最终数据集，绝不能写入论文或作为准确率实验依据**。
- 真数据集待 IWR6843AOP 到货后，由周震宇按 `docs/大创项目统筹需求文档.md` §6 采集，万砚佶按 §6.2 出 COCO 标注（动作 6 类 + 表情 6 类）。

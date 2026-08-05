# MMFi 临时验证数据交付包

## 用途

本目录用于让后端、前端和数据读取流程先跑通。数据来源是本机的 `D:\S01\S01\A01`，对应 MMFi 的 E01/S01/A01 样例。

这不是项目最终采集数据。MMFi 样例没有真实的心率、呼吸率和 AHI，因此这些字段在 `radar_sample.jsonl` 中保留为 `null`，不能据此做生命体征准确率实验。

## 原始样例

原始数据位置：`D:\S01\S01\A01`

- `rgb`、`depth`、`infra1`、`infra2`、`lidar`、`mmwave`、`wifi-csi`：每种模态 297 帧
- `ground_truth.npy`：形状 `(297, 17, 3)`，人体关键点数据
- 动作：`A01`，具体动作名称以 MMFi 官方动作表为准

## 交付文件

- `radar_sample.jsonl`：项目接口可读取的统一字段样例，共 10 条演示记录
- `meta.json`：样例来源、模态帧数和当前时间对齐说明
- `labels.json`：临时动作标签示例
- `collection_parameters.md`：真实雷达采集时需要补齐的参数清单

## 给队友的说明

请先用本目录验证文件读取、接口解析和前端展示。`heart_rate`、`breath_rate`、`ahi_index` 为 `null` 是因为公开样例不包含这些真值；等实际雷达采集后，直接替换 `radar_sample.jsonl`，不要把这些空值当作实验结果。

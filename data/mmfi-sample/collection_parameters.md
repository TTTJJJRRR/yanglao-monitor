# 真实采集参数清单

以下内容必须在真实雷达采集前补齐；当前 MMFi 样例不能替代这些参数。

## 雷达

- 型号：
- 设备编号：
- profile 配置文件名：
- 工作频段：
- 帧率：
- 采样率：
- 与被测者距离：
- 雷达相对被测者角度：
- 安装高度和方向：
- 输出接口：UART / TCP / 其他

## 摄像头

- 型号：
- 分辨率：
- 帧率：
- 安装位置和视角：
- 是否保存原始视频：本地保存，禁止直接上传云端

## 场景记录

- 场景：living_room / bedroom / corridor
- 光照：normal / dark / occluded
- 被测者编号：P001、P002……
- 被测者与设备距离：
- 服装或遮挡说明：
- 采集开始 UTC 时间戳（ms）：

## 真实数据验收

- 雷达和视频时间戳误差小于 200 ms
- 每条雷达记录包含 `timestamp_ms`、`device_id`、`subject_id`、`breath_rate`、`heart_rate`、`motion_flag`
- 睡眠场景补充 `ahi_index` 或 apnea 标注
- 视频上传前只保留边缘提取的骨骼和行为特征

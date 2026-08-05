# 前端 · 实时大屏

React + Vite + TypeScript（M0 脚手架）。

## 启动

```bash
cd frontend
npm install          # 若沙箱报 shim 错误，可尝试 NODE_OPTIONS="" npm install
npm run dev          # 默认 http://localhost:5173
```

后端默认地址为 http://localhost:8000（见 `src/api/client.ts` 的 `API_BASE`）。

## 使用

1. 用 `admin / admin123` 登录。
2. 大屏实时显示呼吸率、心率、最新行为+情绪、雷达示意与预警列表。
3. 右上角「数据源」按钮可在 **Mock 模拟** / **MMFi 样例** 之间切换：
   - MMFi 样例的生命体征为 `null`（仅验证管道），大屏显示 `--` 属正常现象。
   - 行为/跌倒演示：MMFi 模式下仍可用后端 `POST /api/simulate/fall` 触发红色跌倒预警（全局广播，不受数据源影响）。

## 字段容错

`VitalData.breath_rate / heart_rate / chest_displacement_mm` 类型为 `number | null`，
收到 `null` 时统一显示 `--`，不会因缺值崩溃（对齐 MMFi 样例）。

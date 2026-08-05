# 后端 · 智能康养监测系统

FastAPI 服务（M0 脚手架 + MMFi 验证包接入）。

## 启动

```bash
cd backend

# 方式一：本地 venv
python -m venv venv
venv\Scripts\pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
venv\Scripts\python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# 方式二：使用本机已就绪的 managed venv（沙箱环境可直接用）
C:/Users/tttt/.workbuddy/binaries/python/envs/backend313/Scripts/python.exe -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

启动后接口文档（Swagger）：http://localhost:8000/docs

## 演示账号

| 用户名 | 密码    | 角色  |
|--------|---------|-------|
| admin  | admin123 | admin（默认 seed，当前唯一账号） |

> family / elder 角色目前无 seed 也无注册接口。如需演示多角色，请在 `app/routers/auth.py` 的 `seed_admin` 中补充，或另写注册逻辑。

## 关键接口

| 方法 | 路径                 | 说明 |
|------|----------------------|------|
| POST | /api/auth/login      | 登录获取 JWT（response 含 access_token / role） |
| GET  | /api/data-source     | 查询当前数据源与选项 |
| POST | /api/data-source     | 切换数据源，body：`{"source":"mock" \| "mmfi"}` |
| POST | /api/simulate/fall   | 手动触发跌倒预警（全局广播，红色） |
| WS   | /ws?token=xxx        | 实时推送 vital / behavior / alert 帧 |

## 数据源（M0 收尾新增，见 app/data_source.py）

- **mock**（默认）：沿用 `mock.py` 生成器，写库 + 广播（原逻辑不变）。
- **mmfi**：读取 `../data/mmfi-sample/radar_sample.jsonl`，**仅广播不落库**。
  - 该样例由队友朋友提供，生命体征（breath_rate / heart_rate / ahi_index）为 `null`、无行为/报警真值。
  - **仅用于验证"读取样例 → 推送前端"管道**，不能作为最终数据集写入论文。
  - 切换：`POST /api/data-source {"source":"mmfi"}`；前端大屏右上角有切换按钮。

## 隐私红线

雷达不录画面；任何代码不得保存或上传视频 / RGB 图像（见 `data/mmfi-sample/meta_project.json` 的 `privacy_status` 声明）。

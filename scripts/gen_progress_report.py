# -*- coding: utf-8 -*-
"""生成《项目进度盘点报告》Word 文档。用 default venv 的 python 运行。"""
from docx import Document
from docx.shared import Pt, RGBColor, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn

# 主题色（暖苔绿系，与项目一致）
GREEN = RGBColor(0x6E, 0x8F, 0x74)
DARK = RGBColor(0x34, 0x3B, 0x32)
RED = RGBColor(0xC0, 0x5A, 0x4E)
AMBER = RGBColor(0xB9, 0x7A, 0x2E)
GRAY = RGBColor(0x7C, 0x82, 0x74)

doc = Document()

# 默认字体
style = doc.styles["Normal"]
style.font.name = "微软雅黑"
style.font.size = Pt(10.5)
style.element.rPr.rFonts.set(qn("w:eastAsia"), "微软雅黑")


def set_cn(run, size=10.5, bold=False, color=None):
    run.font.name = "微软雅黑"
    run._element.rPr.rFonts.set(qn("w:eastAsia"), "微软雅黑")
    run.font.size = Pt(size)
    run.font.bold = bold
    if color is not None:
        run.font.color.rgb = color


def h1(text):
    p = doc.add_paragraph()
    r = p.add_run(text)
    set_cn(r, 16, True, GREEN)
    p.space_before = Pt(6)
    return p


def h2(text):
    p = doc.add_paragraph()
    r = p.add_run(text)
    set_cn(r, 13, True, DARK)
    return p


def para(text, size=10.5, bold=False, color=None):
    p = doc.add_paragraph()
    r = p.add_run(text)
    set_cn(r, size, bold, color)
    return p


def bullet(text, color=None):
    p = doc.add_paragraph(style="List Bullet")
    r = p.add_run(text)
    set_cn(r, 10.5, False, color)
    return p


def table(headers, rows, widths=None):
    t = doc.add_table(rows=1, cols=len(headers))
    t.style = "Table Grid"
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    hdr = t.rows[0].cells
    for i, htxt in enumerate(headers):
        hdr[i].text = ""
        r = hdr[i].paragraphs[0].add_run(htxt)
        set_cn(r, 10, True, GREEN)
    for row in rows:
        cells = t.add_row().cells
        for i, val in enumerate(row):
            cells[i].text = ""
            r = cells[i].paragraphs[0].add_run(str(val))
            set_cn(r, 9.5)
    if widths:
        for i, w in enumerate(widths):
            for row in t.rows:
                row.cells[i].width = Cm(w)
    doc.add_paragraph()
    return t


# ================= 封面标题 =================
title = doc.add_paragraph()
title.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = title.add_run("智能康养监测系统 · 项目进度盘点报告")
set_cn(r, 20, True, GREEN)

sub = doc.add_paragraph()
sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = sub.add_run("毫米波雷达 + 视频融合的多模态主动预警系统")
set_cn(r, 11, False, GRAY)

meta = doc.add_paragraph()
meta.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = meta.add_run("盘点日期：2026-09-09 ｜ 距上次盘点（8-25）约半个月 ｜ 技术总负责：滕家瑞")
set_cn(r, 9, False, GRAY)

doc.add_paragraph()

# ================= 一、项目是什么 =================
h1("一、项目是什么（30 秒速览）")
para("面向智慧养老的一套多模态健康主动预警系统：毫米波雷达（TI IWR6843AOP，60GHz）非接触监测呼吸/心率/睡眠呼吸暂停，"
     "视频（MediaPipe 端侧骨骼化）识别跌倒/行为，二者在边缘端融合后做主动预警。关键预警「始终送达、不可静音/关闭」。")
para("技术栈：后端 FastAPI + SQLAlchemy + SQLite + JWT；前端 React + Vite + TypeScript + Tailwind；实时 WebSocket；"
     "感知 DFT+EEMD 双估计器生命体征 + MediaPipe 视觉跌倒。", size=9.5, color=GRAY)

h2("阶段时间线（当前处于 M1）")
table(
    ["阶段", "时间", "目标", "状态"],
    [
        ["M0 脚手架", "8月", "后端空壳 + 前端 + 数据契约", "✅ 完成"],
        ["M1 感知打通", "9月", "雷达→体征显示；视频→跌倒", "🔄 进行中（约 40%）"],
        ["M2 边缘AI", "9-10月", "行为/情绪识别、雷达信号分离", "⏳ 待原始数据"],
        ["M3 融合原型", "10-11月", "最小融合原型（核心创新、评审命门）", "⏳ 未开始"],
        ["M4 数据集", "10-12月", "真实采集+标注，建成数据集", "⏳ 待采集"],
        ["M5 集成部署", "12-1月", "边缘+云端联调、Docker、试点", "⏳ 代码就位、未部署"],
        ["M6 成果", "2-3月", "论文/专利/研究报告/答辩PPT", "⏳ 未开始"],
    ],
    widths=[2.5, 2.5, 7.5, 3.5],
)

# ================= 二、整体结论 =================
h1("二、现在进行到哪一步（整体结论）")
para("一句话：**框架和「能跑的壳」都搭好了**，真实算法已接通「生命体征 + 视觉跌倒」两路；"
     "但整条链路**卡在等周震宇采原始雷达点云**——没有真数据，行为识别、融合、数据集全部动不了。", bold=True)
bullet("M0 已完成，M1 进行到约 40%。")
bullet("已真集成：生命体征双估计器投票、视觉跌倒几何检测、8 类安全枚举 + 融合安全翻转、设备离线监测、机构管理端前端、家属小程序前端（交互）。")
bullet("仍是占位/演示：雷达行为 CNN（单类）、床位/老人/设备/趋势 4 类实体、预警「标记已处理」、默认 mock 合成数据源。")
bullet("最大阻塞：原始雷达点云尚未采集（雷达 8-7 已到手，但还没采数据）。")

# ================= 三、已真实完成 =================
h1("三、已真实完成（可验证，不是假的）")
table(
    ["#", "模块", "内容", "状态"],
    [
        ["1", "后端骨架", "FastAPI + JWT 三角色(family/admin/elder) + WebSocket + 数据源四态切换(mock/mmfi/real/replay)", "✅ 真实可跑"],
        ["2", "生命体征双估计器投票", "DFT 周期图 + EEMD 两个独立估计器交叉验证；分歧/低质量→needs_review 转盯防；窗口长度感知", "✅ 真算法，合成信号验证通过"],
        ["3", "视觉跌倒几何检测", "MediaPipe 33 关键点→躯干夹角+质心高度比→fall_score；3 帧滑窗连续≥3 帧才报红", "✅ 真几何，无训练，负样本不误报"],
        ["4", "8 类安全动作枚举", "walking/standing/sitting_still/standing_up/crouching/lying/lying_floor/falling + 未知兜底", "✅ 已锁定"],
        ["5", "融合安全翻转", "低置信/易混淆姿态/未知→needs_review+watch_reason，绝不静默当安全（宁误报不漏报）", "✅ 已实现"],
        ["6", "设备离线监测", "device_offline→critical 红色常驻横幅，文案「关键预警始终送达，不可静音/关闭」，零关闭入口", "✅ 已实现"],
        ["7", "机构管理端前端", "暖苔绿 8 屏；真实管道：登录 /api/auth/login、预警 /api/alerts、WS 实时体征/行为/预警/离线", "✅ 真实（登录/预警/WS 真接后端）"],
        ["8", "家属小程序前端", "390×844 手机壳 + 13 屏 + 全交互（4 tab/SOS/标记已处理/周月切换/可添加被监护人/可绑设备/骨骼化开关/FAQ）", "🟡 交互先行，未接后端"],
        ["9", "SQLite WAL 修复", "修复 100+ 个 -journal 残留：切 WAL 模式 + busy_timeout + 连接池健康检查（8-25）", "✅ 已修复并验证"],
    ],
    widths=[1, 3, 9, 3],
)

# ================= 四、做了"假的"的 =================
h1("四、做了「假的」的（诚实标注，勿当成果）")
para("以下在当前阶段是演示/占位，不能对外当「已完成成果」宣传。", color=RED, bold=True)
table(
    ["占位项", "为什么是「假的」", "何时补真"],
    [
        ["mock 合成数据源（默认）", "后端 generate_vital 生成合成体征/随机预警，不是真实测量", "采到原始点云后切 real"],
        ["床位/老人/设备/趋势 4 类实体", "后端无这些 API，前端用 src/data/demo.ts 静态填充", "M3–M5 补 API"],
        ["预警「标记已处理」", "后端无写接口，前端仅本地生效，刷新即还原", "M3–M5 补写接口"],
        ["雷达行为 CNN（weights.pt）", "真实 torch 权重，但仅单类 A01 样本，实际不能区分多类；accuracy remains pending（未编造准确率）", "采到多类真实点云后重训"],
        ["replay 回放数据", "同学给的「坐/走」是成品体征+动作标签的 jsonl，非原始雷达帧，非实时检测，仅演示前端管道", "作为过渡，最终被真实雷达替换"],
        ["real 数据源", "代码占位，RadarPhaseProvider 尚未读原始点云", "M1 接通 OOB 流"],
    ],
    widths=[3.5, 8.5, 4],
)

# ================= 五、哪里还没做 =================
h1("五、哪里还没做（15 项需求对照）")
para("需求池共 15 项（P0×5 / P1×5 / P2×5）。逐项诚实标注。", color=GRAY)
h2("P0 战略级/安全刚需（必须首发）")
table(
    ["编号", "需求", "现状"],
    [
        ["R-P0-01", "无感非接触监测（不穿戴）", "🟡 部分：方案已定，但真实体征未接通（靠 mock）"],
        ["R-P0-02", "跌倒实时预警 ≤3s + 自动通知", "🟡 部分：视觉跌倒几何已真集成；雷达跌倒、端到端≤3s 未验证"],
        ["R-P0-03", "隐私保护：边缘骨骼化不上云", "🟡 部分：edge/vision_node.py 已实现，未上真设备联调"],
        ["R-P0-04", "家属远程可见性与报警", "🟡 部分：家属小程序 13 屏交互已做，后端未接"],
        ["R-P0-05", "生命体征（呼吸/心率）连续监测", "🟡 部分：双估计器算法真，真数据未接，误差/可用率指标未验证"],
    ],
    widths=[2, 5.5, 8.5],
)
h2("P1 差异化/规模运营")
table(
    ["编号", "需求", "现状"],
    [
        ["R-P1-01", "睡眠呼吸暂停（AHI）风险筛查", "⏳ 未开始（TLV 解析有，AHI 未实现）"],
        ["R-P1-02", "行为识别 6 类（准确率≥95%）", "🟡 部分：8 类枚举+CNN 骨架有，但单类样本，准确率指标未达标"],
        ["R-P1-03", "机构多床位集中看护+可追溯", "🟡 部分：床位看板 UI 有，后端 API 未建（demo 数据）"],
        ["R-P1-04", "低误报：多模态交叉验证", "⏳ 未开始（融合安全翻转有，但真交叉验证降误报未做）"],
        ["R-P1-05", "长期趋势分析（社区医生）", "🟡 部分：趋势页 UI 有，后端未建（demo 数据）"],
    ],
    widths=[2, 5.5, 8.5],
)
h2("P2 增强体验/增值（关键路径外）")
table(
    ["编号", "需求", "现状"],
    [
        ["R-P2-01", "情绪/焦虑联动识别", "⏳ 未开始"],
        ["R-P2-02", "语音主动关怀", "⏳ 未开始"],
        ["R-P2-03", "第三方健康数据打通", "⏳ 未开始"],
        ["R-P2-04", "安心日报推送", "⏳ 未开始（且「免打扰」部分已被用户否决）"],
        ["R-P2-05", "适老化免安装形态", "⏳ 未开始"],
    ],
    widths=[2, 5.5, 8.5],
)

# ================= 六、现在在做什么 =================
h1("六、现在在做什么（当前主线 + 未提交工作）")
h2("当前主线")
para("**等周震宇用 edge/capture_oob.py 采原始雷达点云**（覆盖 8 类动作含跌倒，按 data/radar/E<环境>/S<受试者>/A<class>/mmwave/frame*.bin 归档）。"
     "这是解锁 M2 行为识别、M3 融合、M4 数据集的唯一前置。", bold=True)
h2("最近半个月（8-20 ~ 8-25）实际做的")
bullet("家属小程序前端：family.html + src/family/ 全套 13 屏交互（交互先行、未接后端）。")
bullet("Ardot 家属小程序原型修复：底部 4 Tab「激活态常驻」而非隐藏（8-21）。")
bullet("SQLite journal 爆炸修复：切 WAL 模式，根治 100+ 个 -journal 残留（8-25）。")
h2("⚠️ 有一批未提交的代码（working tree 未 commit/push）")
bullet(".gitignore / backend/app/database.py / backend/app/main.py —— SQLite WAL 修复（8-25，未提交）。", color=AMBER)
bullet("frontend/family.html / frontend/src/family/ —— 家属小程序前端（8-20，未提交）。", color=AMBER)
bullet("scripts/check_journal.py —— WAL 验证脚本（8-25，未提交）。", color=AMBER)
para("这些工作已完成但尚未提交到 git，需尽快 commit + push 以免丢失/冲突。", color=RED, bold=True)

# ================= 七、接下来怎么做 =================
h1("七、接下来怎么做（路线图）")
h2("短期（当前主线，解锁一切）")
bullet("① 采原始雷达点云（周震宇）：用 capture_oob.py 采 8 类动作含跌倒的 OOB 点云 .bin。")
bullet("② 接通真实雷达帧：RadarPhaseProvider 读原始点云→相位→DFT/EEMD 双估计器，把系统从 mock 切到真实体征。")
bullet("③ 提交未提交代码（SQLite 修复 + family 前端）。")
h2("中期（数据到位后）")
bullet("④ 重训行为 CNN：多类真实点云重训，替换单类 weights.pt，真正区分 8 类。")
bullet("⑤ 补 4 类实体 API（床位/老人/设备/趋势）+ 预警「标记已处理」写接口。")
bullet("⑥ M3 融合原型：雷达行为 + 生命体征 + 视觉跌倒边缘端决策级融合（核心创新，评审命门）。")
h2("后期")
bullet("⑦ M4 数据集（含跌倒）+ 留测试集评估指标。⑧ M5 集成部署。⑨ M6 论文/专利/答辩。")

# ================= 八、风险与阻塞 =================
h1("八、风险与阻塞（诚实）")
table(
    ["风险/阻塞", "说明", "建议"],
    [
        ["原始雷达点云未采集", "最大阻塞，依赖周震宇；没有它就动不了行为识别/融合/数据集", "催促并协助周震宇，按采集清单执行"],
        ["app.db 已膨胀到 122MB", "mock 每秒写一条 VitalRecord 从不清理（freelist=0 全是真数据）", "加保留策略（只留最近 N 小时/N 条），待拍板"],
        ["未提交代码堆积", "SQLite 修复 + family 前端共约 40+ 文件未 commit", "尽快 commit + push"],
        ["CNN 单类样本", "weights.pt 不能区分多类，准确率未达标", "采多类数据后重训"],
        ["准确率宣称口径", "未对 P0/P1 指标（≤3s、误差±2次/分、准确率≥95%）做任何真实标定", "M4 留测试集统一标定，勿提前宣称"],
    ],
    widths=[3.5, 7, 5.5],
)

# ================= 九、一句话总结 =================
h1("九、一句话总结（诚实基线）")
para("项目目前是「**框架完整、算法两路真集成、数据零真采集**」的状态：能跑的壳、能展示的 UI、能验证的生命体征/视觉跌倒算法都到位了；"
     "但从「真实雷达数据」往后的行为识别、融合、数据集、准确率全部空白，唯一要务是采到原始点云。", bold=True)

# 页脚说明
doc.add_paragraph()
foot = doc.add_paragraph()
r = foot.add_run("本报告遵循「诚实基线」原则：明确区分已真集成 vs 演示/占位，不把 mock 当成果。单一需求真相源见 docs/大创项目统筹需求文档.md。")
set_cn(r, 8.5, False, GRAY)

out = r"C:\Users\tttt\WorkBuddy\大创-真正版本\deliverables\项目进度盘点报告-2026-09-09.docx"
doc.save(out)
print("saved:", out)

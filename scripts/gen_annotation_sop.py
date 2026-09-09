# -*- coding: utf-8 -*-
"""生成毫米波雷达行为识别训练数据整理与标注 SOP。"""
from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_CELL_VERTICAL_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor

OUT = r"C:\Users\tttt\WorkBuddy\大创-真正版本\deliverables\毫米波雷达行为识别训练数据整理与标注SOP.docx"
GREEN = RGBColor(0x3F, 0x75, 0x5B)
DARK = RGBColor(0x26, 0x32, 0x2B)
RED = RGBColor(0xB4, 0x4E, 0x43)
AMBER = RGBColor(0xA0, 0x6B, 0x20)
GRAY = RGBColor(0x6B, 0x73, 0x6D)


doc = Document()
sec = doc.sections[0]
sec.top_margin = Cm(1.8)
sec.bottom_margin = Cm(1.8)
sec.left_margin = Cm(2.0)
sec.right_margin = Cm(2.0)
style = doc.styles["Normal"]
style.font.name = "微软雅黑"
style.font.size = Pt(10.5)
style.element.rPr.rFonts.set(qn("w:eastAsia"), "微软雅黑")


def run_style(run, size=10.5, bold=False, color=DARK, font="微软雅黑"):
    run.font.name = font
    run._element.rPr.rFonts.set(qn("w:eastAsia"), font)
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.color.rgb = color


def para(text="", size=10.5, bold=False, color=DARK, align=None):
    p = doc.add_paragraph()
    if align is not None:
        p.alignment = align
    r = p.add_run(text)
    run_style(r, size, bold, color)
    p.paragraph_format.space_after = Pt(5)
    return p


def heading(text, level=1):
    p = doc.add_paragraph()
    r = p.add_run(text)
    run_style(r, 16 if level == 1 else 12.5, True, GREEN if level == 1 else DARK)
    p.paragraph_format.space_before = Pt(10 if level == 1 else 6)
    p.paragraph_format.space_after = Pt(5)
    return p


def bullet(text, color=DARK):
    p = doc.add_paragraph(style="List Bullet")
    r = p.add_run(text)
    run_style(r, 10.5, False, color)
    p.paragraph_format.space_after = Pt(2)
    return p


def shade(cell, fill):
    tc_pr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:fill"), fill)
    tc_pr.append(shd)


def table(headers, rows, widths=None, font_size=9.2):
    t = doc.add_table(rows=1, cols=len(headers))
    t.style = "Table Grid"
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    for i, text in enumerate(headers):
        cell = t.rows[0].cells[i]
        shade(cell, "E8F1EB")
        cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
        r = cell.paragraphs[0].add_run(text)
        run_style(r, font_size, True, GREEN)
    for row in rows:
        cells = t.add_row().cells
        for i, value in enumerate(row):
            cells[i].vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
            r = cells[i].paragraphs[0].add_run(str(value))
            run_style(r, font_size, False, DARK)
    if widths:
        for row in t.rows:
            for i, width in enumerate(widths):
                row.cells[i].width = Cm(width)
    doc.add_paragraph().paragraph_format.space_after = Pt(1)
    return t


def code(text):
    p = doc.add_paragraph()
    p.paragraph_format.left_indent = Cm(0.5)
    p.paragraph_format.right_indent = Cm(0.5)
    p.paragraph_format.space_after = Pt(6)
    r = p.add_run(text)
    run_style(r, 9, False, DARK, "Consolas")
    return p


# Cover
p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
p.paragraph_format.space_before = Pt(35)
r = p.add_run("毫米波雷达行为识别训练数据\n整理与标注标准 SOP")
run_style(r, 21, True, GREEN)
p2 = doc.add_paragraph()
p2.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = p2.add_run("交付对象：数据标注人员、原始素材提供人员、模型训练人员")
run_style(r, 11, False, GRAY)
p3 = doc.add_paragraph()
p3.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = p3.add_run("版本：V1.0 ｜ 适用项目：智能康养监测系统 ｜ 日期：2026-09-09")
run_style(r, 9.5, False, GRAY)
doc.add_paragraph()
para("本文件的目标不是“把视频文件改个名字”，而是把视频、雷达原始帧、动作标签和质量说明整理成训练人员可以直接读取、复核和追溯的数据包。任何缺失、猜测或无法确认的内容必须显式标记，不得用空文件、复制文件或编造字段凑数。", 11, True, DARK)

heading("一、先看结论：什么才算“可直接训练”")
para("本项目当前雷达 CNN 的训练输入是三维点云帧，不是仅含 timestamp、motion_flag、心率等字段的回放 JSONL。训练数据的最低闭环必须同时具备：")
bullet("真实雷达原始点云：每帧一个 frameXXXX.bin，能解析为 N×3 的 float32 或 float64 点云。")
bullet("动作标签：标签必须能追溯到一个动作类别和明确时间区间；整段窗口不能把大量其他动作混进正类。")
bullet("视频或人工复核依据：用于确认动作是否发生、发生在哪个时间点；视频不是模型输入时，也不能替代雷达原始点云。")
bullet("采集元数据：受试者、采集会话、环境、设备、雷达位置、光照、遮挡等。")
bullet("质量状态：每个样本必须是 verified、needs_review 或 rejected 之一，不能全部停留在 candidate_pending。")
para("当前识别测试目录中的 JSONL 可用于回放和时间管道验证，但其中大量体征字段为空，且不包含当前 CNN 所需的 frame*.bin。因此，标注人员不能把 JSONL 单独交付为“已可训练点云数据”。", 10.5, True, RED)

heading("二、动作标签字典：必须严格使用")
table(["编号", "目录标签", "系统标签", "标注定义", "特别注意"], [
    ["A01", "walking", "walking", "连续走动、转弯、往返行走", "不要把起步/停步单独标作 standing_up"],
    ["A02", "standing", "standing", "站立，基本无明显位移", "从坐姿起身过程属于 A05"],
    ["A03", "sitting", "sitting_still", "坐姿保持，允许轻微手部/姿态变化", "坐下和起身过程另标转换"],
    ["A04", "lying", "lying", "正常躺卧休息", "正常躺卧不能含跌倒后倒地"],
    ["A05", "standing_up", "standing_up", "坐姿到站立的连续转换", "重点标中间转换区，不把整段坐姿都标成起身"],
    ["A06", "crouching", "crouching", "弯腰、蹲下、拾物等低姿态动作", "必须作为独立类，防止误报跌倒"],
    ["A07", "lying_floor", "lying_floor", "倒地后在地面保持不动/低活动", "与正在跌倒的动态过程分开"],
    ["A08", "falling", "falling", "正在发生的受控模拟跌倒过程", "严禁真实自由落体；需安全垫和保护人"],
    ["背景", "other", "normal_activity", "无法归入以上类别的正常背景活动", "不能当作一个明确动作类，也不能代替 standing/crouching"],
], [1.3, 2.8, 3.0, 6.1, 4.0], 8.8)

heading("三、标准交付目录：照这个结构整理")
para("推荐交付根目录为 dataset_v1，不要把所有文件平铺在一个文件夹。目录标签即训练标签，A 编号必须与上表一致。")
code("dataset_v1/\n  manifest.json\n  README.txt\n  E01/\n    S01/\n      A01/\n        mmwave/frame0000.bin\n        mmwave/frame0001.bin\n        ...\n        metadata.json\n        annotation.json\n      A08/\n        mmwave/frame0000.bin\n        metadata.json\n        annotation.json\n  qc/\n    sample_quality.csv\n    rejected/\n")
para("路径规则：E 表示环境编号，S 表示受试者编号，A 表示动作编号。一个动作片段对应一个 A 目录；若同一受试者同一动作有多次独立重复，必须使用不同的 session 或 sample 目录，不能覆盖前一次文件。", 10, False, GRAY)

heading("四、标注人员的标准工作流程")
for title, text in [
    ("1. 接收与登记", "记录素材提供人、接收日期、原始文件名、来源设备、采集日期、是否有视频、是否有雷达 bin、是否有原始会话目录。先登记再修改文件。"),
    ("2. 建立样本清单", "每个独立动作重复建立一个 sample_id。不要把同一段长视频随意复制成多个样本；只有时间区间确实独立、雷达帧可对应时才拆分。"),
    ("3. 对齐视频与雷达", "以雷达 timestamp_ms 为主时间轴，核对视频起止时间和雷达首末帧。记录偏移量；无法对齐时不得直接标 verified。"),
    ("4. 视频人工复核", "确认动作类别、动作开始和结束、前后上下文、是否有人遮挡、是否有其他人进入、是否发生断帧或明显异常。跌倒必须记录 event_start_s 和 event_end_s。"),
    ("5. 核查雷达原始帧", "确认 mmwave 目录存在 frame*.bin；随机抽帧解析，必须是 N×3、数值有限、不是空文件。记录总帧数、有效帧数、空帧数和格式。"),
    ("6. 裁剪与命名", "只保留动作训练需要的时间窗口，同时保留少量前后上下文。不要为了增加数量重复同一批帧。文件名按 frame0000.bin 连续编号。"),
    ("7. 填写元数据和标注", "填写 metadata.json、annotation.json 和总 manifest。字段不能凭猜测填写；未知用 null，并在 missing_reason 中说明。"),
    ("8. 质量分级", "符合标准为 verified；存在可修复问题但暂不能训练为 needs_review；关键输入缺失、严重错标或无法追溯为 rejected。"),
    ("9. 交叉复核", "标注人员完成后，由另一人抽查至少 20% 样本，重点检查 falling、standing_up、lying_floor、crouching 的边界。"),
    ("10. 打包交付", "交付原始备份、训练目录、manifest、质量表和缺失清单。训练目录与原始素材不得混为一份，避免覆盖和误删。"),
]:
    p = doc.add_paragraph()
    r = p.add_run(title + "：")
    run_style(r, 10.5, True, GREEN)
    r = p.add_run(text)
    run_style(r, 10.5, False, DARK)
    p.paragraph_format.space_after = Pt(4)

heading("五、每个样本必须填写的标准格式")
heading("5.1 metadata.json（样本元数据）", 2)
code('''{
  "sample_id": "E01_S01_A08_001",
  "environment_id": "E01",
  "subject_id": "S01",
  "action_id": "A08",
  "action": "falling",
  "session_id": "session_20260909_001",
  "scene": "living_room",
  "env_light": "normal",
  "radar_device_id": "RADAR_01",
  "radar_mount_height_m": 1.20,
  "radar_distance_m": 2.50,
  "radar_orientation": "胸腹方向，水平",
  "source_video": "raw/session_001.mp4",
  "radar_format": "point_cloud_xyz_bin",
  "radar_dtype": "float64",
  "radar_frame_count": 168,
  "valid_frame_count": 163,
  "timestamp_start_ms": 1788,
  "timestamp_end_ms": 1798,
  "label_status": "verified",
  "annotator": "姓名或编号",
  "reviewer": "复核人姓名或编号",
  "missing_fields": [],
  "notes": "受控侧倒，使用安全垫，未发生真实伤害"
}''')
heading("5.2 annotation.json（动作时间标注）", 2)
code('''{
  "sample_id": "E01_S01_A08_001",
  "label_status": "verified",
  "segments": [
    {"label": "standing", "start_s": 0.0, "end_s": 3.2},
    {"label": "falling", "start_s": 3.2, "end_s": 4.8},
    {"label": "lying_floor", "start_s": 4.8, "end_s": 10.0}
  ],
  "target_segment": {
    "label": "falling",
    "start_s": 3.2,
    "end_s": 4.8,
    "confidence": "high"
  },
  "occlusion": "none",
  "other_person_present": false,
  "quality_note": "动作起止由视频逐帧复核，雷达时间轴已对齐"
}''')
para("对于静态动作，target_segment 可以覆盖稳定保持区间；对于 falling 和 standing_up，必须把动作转换区间单独标出。若一个窗口包含多个动作，不能只写一个总标签后交付为 verified。", 10, False, AMBER)

heading("5.3 manifest.json（全局清单）", 2)
code('''[
  {
    "sample_id": "E01_S01_A08_001",
    "path": "E01/S01/A08/",
    "label": "falling",
    "subject_id": "S01",
    "session_id": "session_20260909_001",
    "frame_count": 168,
    "valid_frame_count": 163,
    "label_status": "verified"
  }
]''')

heading("六、原始雷达 bin 的验收标准")
table(["检查项", "合格标准", "不合格处理"], [
    ["文件存在", "每个样本有 frame*.bin，不能只有 JSONL", "标记 missing_raw_pointcloud，不进入训练"],
    ["可解析", "读取后为 N×3，N>0；支持 float32/float64", "保留原文件，记录损坏文件名并退回"],
    ["数值有效", "x、y、z 为有限数值，无 NaN/Inf；异常比例需记录", "异常帧隔离，不能静默删除"],
    ["帧序连续", "frame 编号连续或有明确缺帧清单", "补原始帧或标记缺帧范围"],
    ["时间对应", "雷达帧时间覆盖标注动作区间", "不能用视频标签替代雷达时间"],
    ["样本独立", "不同重复来自不同采集动作/会话", "重复复制的样本全部标记疑似重复"],
    ["数量", "目标每人每类至少 10 次独立重复；每类至少 3 人", "不足时列入补采清单，不得伪装达标"],
], [3.0, 8.0, 6.0], 9.0)
para("当前模型的预处理会把每个样本的点云序列均匀采样/补零为固定时空张量。因此标注人员只负责保证原始帧真实、完整、可追溯，不要自行把点云转换成图片、CSV 或手工填写伪造坐标。", 10, True, DARK)

heading("七、不同动作的专项标注规则")
for label, rules in [
    ("falling（跌倒）", ["只标真实发生的受控模拟跌倒过程，不把整个窗口全部标成 falling。", "必须拆出跌倒前 standing/walking 和跌倒后 lying_floor。", "必须有安全垫、保护人和安全记录；素材不安全时拒收并反馈。"]),
    ("standing_up（起身）", ["核心是坐到站的连续变化，target_segment 只覆盖转换过程。", "坐姿保持和站立保持应作为上下文或独立样本，不能污染正类。"]),
    ("lying_floor（倒地后）", ["表示跌倒后在地面保持的状态，不等同于正常床上 lying。", "需要视频确认人与地面的空间关系；不确定时 needs_review。"]),
    ("crouching（弯腰/蹲下）", ["必须独立于 falling，保留完整下蹲和恢复过程。", "如果只有弯腰一瞬间且视频不清晰，不要强行归类。"]),
    ("normal_activity（背景）", ["只作为其他/背景活动，不代表系统确认安全。", "不能用 normal_activity 填补缺少 standing 或 crouching 的数据。"]),
]:
    p = doc.add_paragraph()
    r = p.add_run(label)
    run_style(r, 10.5, True, GREEN)
    for rule in rules:
        bullet(rule)

heading("八、缺失和异常怎么处理")
para("核心原则：标注人员负责发现和记录，不能自行猜测补齐；原始素材提供人员负责解释采集过程、补交原始文件或确认确实无法提供。")
table(["问题", "标注人员动作", "发给素材提供人的要求"], [
    ["只有 JSONL，没有 frame*.bin", "状态设为 needs_review 或 rejected；不要转成假 bin", "请提供同一时间段的原始雷达点云 frame*.bin 及原始目录；若没有，请明确回复“未保存原始点云”"],
    ["视频有，雷达没有", "可保留为视频标注参考，但不进入雷达 CNN 训练集", "请确认是否存在另一份设备导出、缓存或原始会话目录"],
    ["雷达有，视频没有", "可做技术格式检查，但动作标签不能直接 verified", "请补充原始视频或逐段动作时间说明，并说明标签来源"],
    ["动作标签不确定", "标记 needs_review，不要自行改成最相近类别", "请确认实际动作、动作发生时间和是否包含前后动作"],
    ["缺少 A02/A06/A07 等类别", "在 qc/sample_quality.csv 列入 class_missing", "请补采缺失类别，不要用 normal_activity 或 lying 代替"],
    ["只有一个人/一个房间/一种光照", "照常整理，但在元数据记录限制，不能称为泛化数据", "请说明能否补充其他受试者、距离、角度、环境和暗光条件"],
    ["时间戳断裂或对不上视频", "记录 gap_start、gap_end、offset_ms；样本暂不验收", "请提供原始时钟、导出方式和完整会话文件，不能凭估计改时间戳"],
    ["bin 文件为空/损坏/格式未知", "隔离文件并记录文件名、大小、解析错误", "请重新导出原始帧，说明 dtype、坐标顺序和导出软件版本"],
    ["动作窗口混入其他动作", "拆分 segments；无法拆分则 needs_review", "请重新给出动作起止时间，或补交更干净的短窗口"],
], [3.2, 6.2, 8.0], 8.5)

heading("九、标准缺失反馈模板（直接复制发送）")
code('''【训练数据补充请求】
样本/会话：E__ / S__ / A__ / session________
发现问题：□缺少原始点云 □缺少视频 □标签不确定 □时间对不上
          □缺少动作类别 □bin损坏 □动作窗口混杂 □其他：____
当前收到的文件：____________________________
具体缺失文件或范围：__________________________
对训练的影响：该样本暂不能进入雷达行为 CNN 训练集/只能作参考
请提供或确认：
1. 同一会话对应的原始 frame*.bin 点云文件；
2. 原始视频或动作发生的起止时间（秒）；
3. 受试者、场景、光照、雷达距离和设备编号；
4. 若文件确实不存在，请明确回复“原始点云未保存”，不要用转换文件代替。
截止时间：________  回复人：________''')

heading("十、质量状态与验收门槛")
table(["状态", "含义", "是否进入训练"], [
    ["verified", "原始点云可解析、标签已复核、时间已对齐、元数据完整、无关键异常", "可以"],
    ["needs_review", "有可修复问题或边界不清，已记录具体问题和责任人", "不可以，修复后重新复核"],
    ["rejected", "关键原始输入缺失、严重错标、损坏、无法追溯或存在安全问题", "不可以"],
    ["reference_only", "只有 JSONL/视频等参考素材，不能直接用于当前雷达 CNN", "不可以，仅作回放/标注依据"],
], [3.2, 11.0, 3.2], 9.0)
para("整批数据验收要求：至少 5 个动作类别才能开始初步训练管线；正式实验建议 8 类齐全，每类每位受试者至少 10 次独立重复，至少 3 名受试者。训练、验证、测试必须按受试者或采集会话隔离，不能把同一动作重复切片后同时放入训练和测试。", 10.5, True, RED)

heading("十一、交付前逐项检查表")
for item in [
    "是否存在全局 manifest.json、README.txt 和 qc/sample_quality.csv？",
    "每个 sample_id 是否唯一，目录是否符合 E/S/A/mmwave 结构？",
    "每个训练样本是否真的有 frame*.bin，而不是只有 JSONL？",
    "随机抽查的 bin 是否均可解析为 N×3 点云，是否记录了空帧和损坏帧？",
    "每个样本是否填写 subject、session、scene、env_light、设备和雷达位置？",
    "所有标签是否已从 candidate_pending 改为 verified、needs_review 或 rejected？",
    "falling 是否拆出了跌倒前、跌倒中、跌倒后，未把整段窗口粗暴标成一个类？",
    "standing_up、crouching、lying_floor 是否按专项规则单独处理？",
    "缺失项是否已形成清单，并逐项向素材提供人询问？",
    "是否存在复制重复、同一会话泄漏、标签与目录不一致？",
    "训练集、验证集、测试集是否按受试者/会话隔离？",
    "是否没有编造数据、坐标、动作发生时间和准确率？",
]:
    bullet("□ " + item)

heading("十二、给标注人员的最终原则")
para("宁可交付“缺失清单 + 待补样本”，也不要交付看起来整齐但无法训练的假数据。JSONL 能证明存在一段回放记录，不能自动证明存在原始点云；视频能帮助确认动作，不能替代雷达输入；同一人的大量切片能增加文件数量，不能增加真正的泛化能力。", 11, True, GREEN)
para("本 SOP 对应项目当前训练代码：数据集扫描目录为 E*/S*/A*/mmwave，单帧点云格式为 N×3，训练前必须由模型人员再次运行数据清点、解析和留出测试集评估。没有评估数字时，统一写“待评估”，不得填写推测准确率。", 9.5, False, GRAY)

# footer
for section in doc.sections:
    footer = section.footer.paragraphs[0]
    footer.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = footer.add_run("毫米波雷达行为识别训练数据整理与标注标准 SOP ｜ 仅限项目数据协作使用")
    run_style(r, 8, False, GRAY)

doc.save(OUT)
print("saved:", OUT)

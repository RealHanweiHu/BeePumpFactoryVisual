#!/usr/bin/env python3
"""Local, source-preserving correction of the user-identified 8F passenger entry.

Display pixels reproduce a marked screenshot; they are never CAD/site coordinates.
The old packages remain historical evidence and are not rewritten by this script.
"""
import base64
import copy
import hashlib
import html
import json
from pathlib import Path
import shutil
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / '交付_8楼'
DESIGN = ROOT / 'design/v2/entry_v2.7'
OUT = SRC / '客梯入口修订_V2.7'
V25 = SRC / '图纸标注_V2.5'
V26 = SRC / '逐项样式尺寸_参观预览_V2.6'
PERSISTED_EVIDENCE = OUT / 'evidence/用户标注_客梯与进入方向_2026-10-17.png'
ATTACHMENT = PERSISTED_EVIDENCE if PERSISTED_EVIDENCE.exists() else Path('/var/folders/sv/npxlc_k53696tn8hryg5dx5w0000gn/T/codex-clipboard-d3f79d39-ab8b-41fd-ae6a-9fbb78998039.png')
NS = 'http://www.w3.org/2000/svg'
ET.register_namespace('', NS)
REV = 'V2.7-ENTRY-CORRECTION-DRAFT'
PURPLE = '#8A3F86'
ANCHOR = [1319, 200]
# Sparse directional strokes from the user's mark, in the 2200x1679 source image.
# Gaps intentionally remain: this is not surveyed door-to-door navigation geometry.
SEGMENTS = [
    [[1386, 222], [1453, 222]],
    [[1412, 258], [1412, 329]],
    [[1424, 370], [1504, 370]],
    [[1489, 441], [1505, 512], [1505, 569], [1469, 604]],
    [[1420, 612], [1185, 612]],
]


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def write_json(p, value):
    p.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')


def element(tag, **attrs):
    return ET.Element(f'{{{NS}}}{tag}', {k.replace('_', '-'): str(v) for k, v in attrs.items()})


def text(parent, x, y, value, size=27, color='#222', bold=False):
    t = element('text', x=x, y=y, font_size=size, fill=color,
                font_weight=700 if bold else 400)
    t.text = value
    parent.append(t)
    return t


def metadata(source=None):
    return {
        'revision': REV, 'date': '2026-10-17', 'status': 'draft',
        'record_type': 'user_annotated_entry_correction',
        'source_file': str(source.relative_to(ROOT)) if source else None,
        'source_file_sha256': sha(source) if source else None,
        'evidence_path': 'evidence/用户标注_客梯与进入方向_2026-10-17.png',
        'evidence_sha256': sha(ATTACHMENT),
        'source_base_sha256': sha(V26 / '原始底图_只读.png'),
        'display_coordinate_frame': 'source screenshot pixels, origin top-left, x right, y down',
        'display_anchor_pixels': ANCHOR,
        'position_world': None, 'actual_route_geometry_world': None,
        'physical_units_confirmed': False, 'floor_identity_confirmed': False,
        'approved_route': False, 'production_release': False,
        'scope': 'Passenger-entry location and user-marked directional sequence only; no L1/L2 material-route confirmation.',
    }


def callout(root, offset_x, offset_y, label='01', color='#FF6600'):
    x, y = ANCHOR[0] + offset_x, ANCHOR[1] + offset_y
    bx, by = x - 95, y - 75
    g = element('g', id='corrected-passenger-entry')
    g.append(element('path', d=f'M{x} {y} L{bx} {by}', stroke=color,
                     stroke_width=4, fill='none', stroke_dasharray='7 6'))
    g.append(element('circle', cx=x, cy=y, r=25, stroke=color, stroke_width=5, fill='none'))
    if label == '01':
        g.append(element('circle', cx=bx, cy=by, r=30, fill='white', stroke=color, stroke_width=5))
        text(g, bx-18, by+10, label, 28, '#000', True)
    else:
        g.append(element('rect', x=bx-47, y=by-27, width=94, height=54,
                         fill='white', stroke=color, stroke_width=4))
        text(g, bx-38, by+10, label, 25, color, True)
    root.append(g)


def direction_segments(root, ox, oy):
    defs = element('defs')
    marker = element('marker', id='p1-direction', markerWidth=12, markerHeight=12,
                     refX=9, refY=5, orient='auto', markerUnits='userSpaceOnUse')
    marker.append(element('path', d='M1 1 L9 5 L1 9', fill='none', stroke=PURPLE, stroke_width=2))
    defs.append(marker)
    root.append(defs)
    g = element('g', id='user-marked-entry-directions')
    for segment in SEGMENTS:
        points = [[x + ox, y + oy] for x, y in segment]
        d = 'M' + ' L'.join(f'{x} {y}' for x, y in points)
        g.append(element('path', d=d, fill='none', stroke='white', stroke_width=10, opacity='.85'))
        g.append(element('path', d=d, fill='none', stroke=PURPLE, stroke_width=5,
                         stroke_dasharray='12 7', marker_end='url(#p1-direction)'))
    root.append(g)


def save_svg(root, name, source=None):
    for e in list(root):
        if e.tag.endswith('metadata'):
            root.remove(e)
    m = element('metadata')
    m.text = json.dumps(metadata(source), ensure_ascii=False)
    root.insert(0, m)
    path = DESIGN / name
    ET.ElementTree(root).write(path, encoding='utf-8', xml_declaration=True)
    write_json(path.with_suffix('.meta.json'), metadata(source))
    return path


def revise_existing(source, name, kind):
    root = ET.parse(source).getroot()
    old = list(root)
    start, stop = (9, 14) if kind in ('install', 'flow') else (7, 11)
    for e in old[start:stop]:
        root.remove(e)
    if kind == 'flow':
        # Remove both underlay and stroke of the discredited lower-right P1.
        for e in list(root):
            if e.tag.endswith('path') and e.get('d', '').startswith('M 1369.97 1573.78'):
                root.remove(e)
        direction_segments(root, 40, 235)
    for e in root.iter(f'{{{NS}}}text'):
        value = e.text or ''
        value = value.replace('V2.5-ANNOTATION-DRAFT', REV).replace('V2.6-DETAIL-DRAFT', REV)
        value = value.replace('合用前室接口：到层形象 / 导览', '右上客梯接口：到层形象 / 导览')
        value = value.replace('只核退出前室后的实体墙；不把前室当展示面', '用户指认右上客梯；墙面与接待停留面另核')
        value = value.replace('P1  到层 → 实际进入条件 → 获准作业', 'P1  右上客梯 → 用户标注进入方向')
        value = value.replace('图上核对索引：01 → 08 → 03；实际道路须实走另定', '东 → 南 → 东 → 南 → 西；逐门通行条件另核')
        value = value.replace('虚线连接 = 业务关系，不是通行路线', '蓝线：未核业务关系；紫线：用户进入示意')
        value = value.replace('实际到层口待核；退出前室后接手，核范围/进入条件，不默认进更衣/风淋。', '右上客梯由用户图上指认；接待停留面与参观权限另核。')
        value = value.replace('待填：实际入口/使用梯、走段、停留面、人数与时间、拍摄权限、物流交叉控制及返程；不能按本页组织无陪同参观。', '入口已按用户标注修正；访客走段、停留面、人数、拍摄及返程仍待核，不据此开放参观。')
        value = value.replace('候选方案｜图上编号核对观察对象；右侧连线为讲解顺序；实际入口、走段及停留面待实走确认', '入口纠错 V2.7｜VP07 移至用户指认右上客梯；右侧仍为候选讲解顺序')
        if kind in ('install', 'flow') and value.startswith('八层图身 /'):
            value = '右上客梯按用户标注纠正｜八层/三层图签与单位仍待核'
        if kind == 'overview' and value.startswith('底图结构保持'):
            value = '01 已改至右上客梯；底图保持原截图；墙面、安装尺寸/高度/数量仍待核'
        e.text = value
    ox = 40 if kind in ('install', 'flow') else 35
    callout(root, ox, 235, 'VP07' if kind == 'visitor' else '01',
            '#006B8F' if kind in ('flow', 'visitor') else '#FF6600')
    return save_svg(root, name, source)


def correction_sheet():
    root = element('svg', width=3400, height=2200, viewBox='0 0 3400 2200')
    st = element('style'); st.text = 'text{font-family:"PingFang SC",Arial,sans-serif}'
    root.append(st)
    root.append(element('rect', width=3400, height=2200, fill='white'))
    root.append(element('rect', width=3400, height=175, fill='#000000'))
    text(root, 45, 72, 'BeePump 8楼｜客梯位置与进入方向修正', 46, '#FFFFFF', True)
    text(root, 45, 135, 'V2.7｜依据用户 2026-10-17 标注；底图几何未改', 28, '#FFFFFF')
    source = ET.parse(V26 / '8楼_样式尺寸总览_1.svg').getroot()
    root.append(copy.deepcopy(next(e for e in source if e.get('id') == 'immutable-source')))
    text(root, 40, 210, '紫色箭头仅复述用户进入方向；留有断口，不代表实测逐门路线或地面标线', 26)
    callout(root, 35, 235, '01', PURPLE)
    direction_segments(root, 35, 235)
    root.append(element('rect', x=2280, y=235, width=1060, height=1700, fill='#F5F5F2'))
    lines = [
        (295, '01 右上客梯｜更衣室北侧', 35, True),
        (360, '用户在原图截图上圈定，作为本次设计纠错依据。', 27, False),
        (435, '进入方向（按红箭头顺序）', 30, True),
        (500, '① 出客梯后向东', 28, False),
        (560, '② 向南，经更衣／风淋接口一带', 28, False),
        (620, '③ 向东至原料仓东侧通道', 28, False),
        (680, '④ 沿该通道向南', 28, False),
        (740, '⑤ 转向西，朝生产区进入', 28, False),
        (845, '撤回旧起点', 30, True),
        (905, '右下 F0A17“合用前室”不再作为到层客梯依据。', 26, False),
        (965, '旧 01 → 08 → 03 人行直连线撤除。', 27, False),
        (1070, '联动调整', 30, True),
        (1130, '安装读面核对图的 01、样式尺寸总览 1 的 01；', 26, False),
        (1190, '人员进入 P1、参观入口候选对象 VP07、D01。', 26, False),
        (1295, '仍需分别核对', 30, True),
        (1355, '标注不是客梯运货许可，L1／L2 物流尚未确认。', 26, False),
        (1415, '访客是否沿此进入、接待停留与返程另核。', 27, False),
        (1475, '箭头只表示方向，不细化未经核实的门槛穿越。', 26, False),
        (1580, 'BE-02／WF-01 选用版面保留', 29, True),
        (1640, '品牌墙／导览需重新核墙面，未确定实体安装点。', 26, False),
        (1700, '名义尺寸沿用；实际尺寸、高度、数量仍待核。', 26, False),
        (1810, '来源：用户原始红线图附在 evidence/，字节留存。', 25, False),
    ]
    for y, value, size, bold in lines:
        text(root, 2310, y, value, size, '#222', bold)
    root.append(element('rect', x=35, y=1980, width=3300, height=180, fill='#FFF1E6'))
    text(root, 60, 2025, '本次确认范围：用户图上指认的客梯位置及进入方向；不是楼层图签、物理单位、安装或安全批准。', 28)
    text(root, 60, 2080, '源图左侧仍有裁切；世界坐标、长度、净宽、实物点位与数量保持未测。P02／P05 阻塞不变。', 26)
    text(root, 60, 2125, REV + '｜production_release=false', 24)
    return save_svg(root, '8楼_客梯与进入方向修正_V2.7.svg')


def d01_sheet():
    source = V26/'8楼_样式尺寸总览_1.svg'
    old = ET.parse(source).getroot()
    root = element('svg', width=3400, height=2200, viewBox='0 0 3400 2200')
    for e in list(old)[:7]:
        root.append(copy.deepcopy(e))
    for e in root.iter(f'{{{NS}}}text'):
        if '样式与尺寸标注' in (e.text or ''):
            e.text = 'BeePump 8楼｜D01 到层形象与入场导览修正'
        elif (e.text or '').startswith('D 为'):
            e.text = 'REQ-8F-01｜入口对象修正，沿用 BE-02 / WF-01 版面；不确定实体墙面与安装量'
        elif (e.text or '').startswith('底图结构'):
            e.text = '01 已改至右上客梯；底图结构保持；具体接待面、安装位置和进入权限另核'
    for e in list(old)[11:22]:
        root.append(copy.deepcopy(e))
    for e in root.iter(f'{{{NS}}}text'):
        if '01 合用前室接口' in (e.text or ''):
            e.text = '01 右上客梯接口：形象 / 导览'
    callout(root, 35, 235)
    lines = [
        (760, '入口依据', 32, True),
        (825, '用户圈定：右上、更衣室北侧客梯。', 28, False),
        (890, '原右下“合用前室”入口候选已撤回。', 28, False),
        (1020, '保留', 32, True),
        (1085, 'BE-02 品牌形象与 WF-01 楼层导览分工。', 27, False),
        (1150, '整版名义尺寸沿用；不按墙面裁切压字。', 27, False),
        (1280, '重新核对', 32, True),
        (1345, '退出梯口后的实际可用墙面与接待停留面；', 27, False),
        (1410, '门扇、通行、检修及原有安全设施；', 27, False),
        (1475, '正式内容、Logo、实体尺寸、固定方法及数量。', 27, False),
        (1610, '用户进入箭头另见“客梯与进入方向修正”图。', 26, False),
        (1675, '该顺序未自动授予访客进入或客梯运货许可。', 26, False),
    ]
    for y, value, size, bold in lines:
        text(root, 2310, y, value, size, '#222', bold)
    root.append(element('rect', x=35, y=1980, width=3300, height=180, fill='#FFF1E6'))
    text(root, 60, 2025, 'D01 是功能需求详情，不是一块标牌或实际点位；入口指认与具体安装面、运营和安全批准分开记录。', 27)
    text(root, 60, 2080, '图签/单位仍待核。实际坐标、高度、尺寸、数量及具名批准均保持未填。', 26)
    text(root, 60, 2125, REV + '｜production_release=false', 24)
    return save_svg(root, 'D01_到层形象与入场导览_V2.7.svg', source)


def main():
    DESIGN.mkdir(parents=True, exist_ok=True)
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / 'evidence').mkdir(exist_ok=True)
    if ATTACHMENT.resolve() != PERSISTED_EVIDENCE.resolve():
        shutil.copyfile(ATTACHMENT, PERSISTED_EVIDENCE)
    sources = [V25/'8楼_安装读面标注.svg', V25/'8楼_物流人流核对.svg',
               V26/'8楼_样式尺寸总览_1.svg', V26/'8楼_参观路线预览.svg',
               V26/'output/pdf/BeePump_8F_Point_Styles_Visitor_V2.6.pdf']
    originals = {str(p.relative_to(ROOT)): sha(p) for p in sources}
    correction_sheet()
    d01_sheet()
    for source, name, kind in [
        (sources[0], '8楼_安装读面标注_V2.7.svg', 'install'),
        (sources[1], '8楼_物流人流核对_V2.7.svg', 'flow'),
        (sources[2], '8楼_样式尺寸总览_1_V2.7.svg', 'overview'),
        (sources[3], '8楼_参观入口预览_V2.7.svg', 'visitor'),
    ]:
        revise_existing(source, name, kind)
    ledger = json.loads((V25/'标注来源与核对台账.json').read_text())
    ann = ledger['annotations'][0]
    old_ann = copy.deepcopy(ann)
    ann.update(title='右上客梯接口：到层形象 / 导览', source_entity_handle=None,
               source_text='用户图上指认：更衣室北侧客梯', source_preview_pixel_anchor=ANCHOR,
               badge_offset_pixels=[-95, -75],
               site_check='按用户指认改入口；具体墙面/接待停留面、净空与安装另核',
               entry_location_status='user_identified_on_source_image',
               supersedes_wrong_candidate=old_ann,
               evidence_path='evidence/用户标注_客梯与进入方向_2026-10-17.png',
               evidence_sha256=sha(ATTACHMENT))
    ledger.update(revision=REV, user_entry_correction=metadata())
    p1 = next(c for c in ledger['functional_connections'] if c['label'] == 'P1')
    p1.update(annotation_refs=['01'], description='右上客梯 → 东 → 南 → 东 → 南 → 西（用户进入方向）',
              display_directional_segments_pixels=SEGMENTS,
              path_status='user_marked_sequence_pending_site_and_access_review',
              superseded_annotation_refs=['01', '08', '03'])
    write_json(OUT/'标注来源与核对台账_V2.7.json', ledger)
    reqs = json.loads((V26/'逐项需求与来源.json').read_text())
    reqs['revision'] = REV
    reqs['source_annotation_map']['REQ-8F-01'] = ann
    reqs['requirements'][0]['entry_location_evidence'] = metadata()
    reqs['requirements'][0]['relative_installation_face'] = '用户指认右上客梯到层后，具体获准墙面与接待停留面待核'
    write_json(OUT/'逐项需求与来源_V2.7.json', reqs)
    visitor = json.loads((V26/'参观候选节点.json').read_text())
    visitor.update(revision=REV, source_annotation_ledger_path='标注来源与核对台账_V2.7.json',
                   entry_choice_status='user_identified_on_source_image',
                   entry_selected_by_user={'annotation_id':'ANN-8F-01', 'evidence':metadata()},
                   entry_preview_note='右上、更衣室北侧客梯由用户图上指认；访客进入段及接待停留面另核。')
    stop = visitor['stops'][0]
    stop.update(observation_summary=visitor['entry_preview_note'],
                observation_face='右上客梯到层后的获准接待面，具体位置待核',
                proposed_stop_read_face='右上客梯到层后的获准接待面，具体位置待核',
                entry_location_evidence=metadata())
    for ref in stop.get('source_anchor_references', []):
        if ref.get('annotation_reference') == 'ANN-8F-01':
            ref.update(source_entity_handle=None, source_text=ann['source_text'],
                       source_preview_pixel_anchor=ANCHOR, evidence=metadata())
    write_json(OUT/'参观候选节点_V2.7.json', visitor)
    report = {
        **metadata(), 'original_file_hashes':originals,
        'changes':[{'object':'ANN-8F-01','action':'Refine','preserve':'Source geometry and BE-02/WF-01 nominal templates',
                    'reason':'User identified the upper-right passenger elevator, invalidating the lower-right entrance candidate'},
                   {'object':'P1','action':'Retire old direct connection; reproduce marked directional strokes',
                    'preserve':'No material route confirmation'},
                   {'object':'VP07 / REQ-8F-01','action':'Refine linked entry object; installation and access remain pending'}],
        'superseded_visuals':[str(p.relative_to(ROOT)) for p in sources[:4]],
        'historical_pdf_notice':'V2.6 PDF remains historical; affected entry illustrations are replaced by this correction package.',
    }
    write_json(OUT/'修订记录与来源_V2.7.json', report)
    for p in DESIGN.iterdir():
        if p.is_file(): shutil.copyfile(p, OUT/p.name)
    titles = [
        ('8楼_客梯与进入方向修正_V2.7', '客梯位置与进入方向'),
        ('8楼_安装读面标注_V2.7', '安装读面：01 入口对象修正'),
        ('8楼_物流人流核对_V2.7', '物流与人流：替换 P1，L1/L2 仍未核'),
        ('8楼_样式尺寸总览_1_V2.7', '样式尺寸总览 1：01 修正'),
        ('8楼_参观入口预览_V2.7', '参观入口：VP07 对象修正'),
        ('D01_到层形象与入场导览_V2.7', 'D01：入口关联修正详情'),
    ]
    sections = ''.join(f'<section><h2>{html.escape(title)}</h2><p><a href="{stem}.png">查看 PNG</a> · <a href="{stem}.svg">可编辑 SVG</a></p><a href="{stem}.png"><img src="{stem}.png" alt="{html.escape(title)}"></a></section>' for stem,title in titles)
    page = '''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>8楼客梯入口纠错 V2.7</title><style>body{margin:0;background:#fff;color:#3e3a39;font:17px/1.75 system-ui,-apple-system,"PingFang SC",sans-serif}main{max-width:1500px;margin:auto;padding:24px}h1{color:#000;border-left:7px solid #ff6600;padding-left:18px}section{margin:42px 0}img{width:100%;height:auto}a{color:#000;overflow-wrap:anywhere}a:focus-visible{outline:3px solid #ff6600}.note{border-left:4px solid #ff6600;background:#fff4eb;padding:14px 20px}@media(max-width:600px){main{padding:16px}h1{font-size:26px}}</style><main><p><a href="../打开这里.html">返回 8 楼交付目录</a></p><h1>8楼｜客梯入口修订 V2.7</h1><p class="note">用户于 2026-10-17 在底图圈定右上、更衣室北侧客梯，并画出进入方向。旧右下合用前室入口选择撤回。以下六图替代旧版对应入口、01／D01、P1 与 VP07；旧 PDF／ZIP 保留为历史评审稿。</p><p>紫色箭头复述用户方向示意，断口不补画成实测门槛路线。L1／L2 物流、访客进入、安装及安全状态分别待核；楼层图签与单位问题未解，production_release=false。</p><p><a href="evidence/用户标注_客梯与进入方向_2026-10-17.png">用户原始标注</a> · <a href="标注来源与核对台账_V2.7.json">修订标注台账</a> · <a href="逐项需求与来源_V2.7.json">需求与来源</a> · <a href="参观候选节点_V2.7.json">候选参观节点</a> · <a href="修订记录与来源_V2.7.json">版本与来源记录</a></p>'''+sections+'<p>原始底图嵌入字节保持；显示像素没有换算为世界坐标、长度或数量。未创建实际点位或批准记录。</p></main></html>'
    (OUT/'START_HERE.html').write_text(page)
    (OUT/'README.md').write_text('# 8楼客梯入口修订 V2.7\n\n入口位置按用户2026-10-17红线纠正：右上、更衣室北侧客梯。\n\n六张修订图仅替代旧版对应的到层入口、01/D01、P1及VP07；旧图/PDF/ZIP保留为历史记录。START_HERE.html是本次入口。SVG在design/v2/entry_v2.7另有编辑源稿与元数据。evidence/保留原始标注字节。\n\nP1是用户方向示意而非实测门槛路线；用户没有确认L1/L2物料路线、访客进入、墙面、安装数量或专项安全批准。楼层/物理单位与P02/P05阻塞保留。production_release=false。\n')
    assert all(sha(ROOT/p) == digest for p, digest in originals.items())
    print(json.dumps({'output':str(OUT), 'svg_count':len(list(DESIGN.glob('*.svg'))),
                      'original_artwork_unchanged':True}, ensure_ascii=False))


if __name__ == '__main__':
    main()

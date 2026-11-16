#!/usr/bin/env python3
"""Build three local, editable options from the 26 supplied 8F templates.

No point locations, installed dimensions, copy, status semantics, or signatures
are generated here. All text and text geometry are compared to source byte for
byte / attribute for attribute after each transformation. Template-specific
panels change the relationship between fixed labels and editable information.
"""
from __future__ import annotations

import copy
import csv
import hashlib
import json
from pathlib import Path
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = ROOT / '交付_8楼/逐项样式尺寸_参观预览_V2.6'
OUT = ROOT / 'design/v2/options_v2.8'
NS = 'http://www.w3.org/2000/svg'
ET.register_namespace('', NS)
BLACK, WHITE, ORANGE, GRAY = '#000000', '#FFFFFF', '#FF6600', '#3E3A39'
QUALITY = {'QC-01': '#005EB8', 'QC-02': '#009639', 'QC-03': '#DA291C', 'QC-04': '#FFD100'}
STYLES = [
    {'id': 'A', 'label': '原版黑橙', 'description': '保留现有版面作为比较基准；黑橙品牌标题、原有表格和更新区。'},
    {'id': 'B', 'label': '白底信息优先', 'description': '品牌标题白底黑字与橙细线，表格开放分隔；品质状态标题带冻结。'},
    {'id': 'C', 'label': '固定标签分区', 'description': '固定标签与填写区分开，使用黑底索引、步骤标题和白底更新格；品质状态标题带冻结。'},
]


def tag(name):
    return '{' + NS + '}' + name


def num(el, attr, default=0):
    return float(el.get(attr, default))


def fmt(value):
    return f'{value:g}'


def texts(root):
    return list(root.iter(tag('text')))


def text_contract(root):
    """All copy including whitespace, tspans, and geometry must stay fixed."""
    return [(list(t.itertext()), {k: v for k, v in t.attrib.items() if k != 'fill'}) for t in texts(root)]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def parent_of(root, child):
    return next(p for p in root.iter() if child in list(p))


def select(root, *, y=None, x=None, contains=None, exact=None):
    return [t for t in texts(root)
            if (y is None or abs(num(t, 'y') - y) < .02)
            and (x is None or abs(num(t, 'x') - x) < .02)
            and (contains is None or contains in ''.join(t.itertext()))
            and (exact is None or exact == ''.join(t.itertext()))]


def panel(root, x, y, w, h, ts, fill=BLACK, stroke=None, invert=True):
    """Insert a panel under the existing copy without reparenting the copy."""
    if not ts:
        raise ValueError(f'Panel has no source text: {x,y,w,h}')
    p = parent_of(root, ts[0])
    rect = ET.Element(tag('rect'), {'x': fmt(x), 'y': fmt(y), 'width': fmt(w),
                                  'height': fmt(h), 'fill': fill, 'data-option-panel': 'true'})
    if stroke:
        rect.set('stroke', stroke)
        rect.set('stroke-width', fmt(max(.2, min(w, h) * .012)))
    p.insert(list(p).index(ts[0]), rect)
    if invert:
        for t in ts:
            t.set('fill', WHITE if fill == BLACK else BLACK)
    return rect


def rule(root, x1, y, x2, ts, stroke=ORANGE, width=1):
    p = parent_of(root, ts[0])
    line = ET.Element(tag('line'), {'x1': fmt(x1), 'y1': fmt(y), 'x2': fmt(x2),
                                   'y2': fmt(y), 'stroke': stroke,
                                   'stroke-width': fmt(width), 'data-option-rule': 'true'})
    p.insert(list(p).index(ts[0]), line)


def header_height(root, w, h):
    candidates = [num(e, 'height') for e in root.iter(tag('rect'))
                  if num(e, 'y') == 0 and num(e, 'x') == 0
                  and num(e, 'width') >= .98 * w and e.get('fill') == BLACK]
    return min(candidates) if candidates else min(h * .16, 125)


def white_header(root, w, h, code):
    if code in QUALITY:
        return 19
    hh = header_height(root, w, h)
    for e in root.iter(tag('rect')):
        if num(e, 'x') == 0 and num(e, 'y') == 0 and num(e, 'height') == hh:
            if e.get('fill') == BLACK:
                e.set('fill', WHITE)
            elif e.get('fill') == ORANGE and num(e, 'width') < .03 * w:
                e.set('fill', WHITE)
    for t in texts(root):
        if num(t, 'y') <= hh and t.get('fill') == WHITE:
            t.set('fill', BLACK)
    # Full black direction templates include inset dark direction cells.
    if code == 'WF-03':
        for e in root.iter(tag('rect')):
            if e.get('fill') == BLACK:
                e.set('fill', WHITE)
    source_header = [t for t in texts(root) if num(t, 'y') <= hh]
    rule(root, w * .034, hh - max(.6, h * .003), w * .966,
         source_header, width=max(.5, min(w, h) * .006))
    return hh


def pair_fields(root, ys, left_x, right_x, right_end, row_height, style):
    """Make the fixed-label / update-field relationship explicit."""
    for y in ys:
        ls, rs = select(root, y=y, x=left_x), select(root, y=y, x=right_x)
        if not ls or not rs:
            raise ValueError(f'Missing pair at {left_x,right_x,y}')
        fs = max(num(t, 'font-size') for t in ls + rs)
        top = y - fs * 1.25
        bottom = min(top + row_height, y + fs * .55)
        height = bottom - top
        if style == 'C':
            panel(root, left_x - fs * .45, top, right_x - left_x - fs * .1,
                  height, ls, BLACK)
        else:
            for t in ls:
                t.set('fill', BLACK)
        panel(root, right_x - fs * .2, top, right_end - right_x + fs * .2,
              height, rs, WHITE, GRAY, invert=False)


def open_panels(root, w, hh, code):
    """Use open rules, while keeping code/photo reserved areas intact."""
    excluded = {'WH-01', 'SW-01', 'EQ-01'}
    if code in excluded:
        return
    rects = list(root.iter(tag('rect')))
    for e in rects:
        x, y, rw, rh = [num(e, a) for a in ('x', 'y', 'width', 'height')]
        fill, stroke = e.get('fill'), e.get('stroke')
        if y <= hh or rw < w * .12:
            continue
        neutral = fill in ('#F2F2F2', '#F2F3F4', '#F2F3F5', '#F5F5F5') or (
            fill == GRAY and num(e, 'opacity', 1) < .2)
        if neutral or (fill == WHITE and stroke and stroke != ORANGE):
            e.set('fill', WHITE)
            e.set('opacity', '1')
            e.set('stroke', 'none')
            p = parent_of(root, e)
            line = ET.Element(tag('line'), {'x1': fmt(x), 'y1': fmt(y + rh),
                                           'x2': fmt(x + rw), 'y2': fmt(y + rh),
                                           'stroke': GRAY, 'stroke-width': fmt(max(.25, w*.00065)),
                                           'data-option-rule': 'true'})
            p.insert(list(p).index(e) + 1, line)


def template_specific(root, code, style, w, h):
    c = style == 'C'
    if code == 'BE-02':
        if c:
            ts = [t for t in texts(root) if num(t, 'x') >= 950 and num(t, 'y') < 850]
            panel(root, 850, 0, 2750, 850, ts, WHITE)
            for x, y in [(140, 1085), (1250, 1085), (2360, 1085)]:
                panel(root, x-50, 970, 1020, 155, select(root,x=x,y=y))
        else:
            for x in [140, 1250, 2360]:
                rule(root, x, 1130, x+920, select(root,x=x,y=1085), width=5)
    elif code == 'WF-01':
        for i, y in enumerate([275,386,497,608,719,830,941,1052,1163]):
            t = select(root, x=60,y=y)
            if c:
                panel(root,32,215+i*111,145,105,t)
                if i == 1:
                    t[0].set('fill', ORANGE)
            else:
                rule(root,177,215+i*111+105,868,t,GRAY,.7)
    elif code == 'WF-02':
        if c:
            ts = [t for t in texts(root) if num(t,'x') >= 330]
            panel(root,273,0,w-273,350,ts,WHITE)
        else:
            rule(root,330,350,1150,select(root,y=319),GRAY,1)
    elif code == 'WF-04':
        for y, top, bottom, value_y in [(618,584,643,694),(792,758,812,846)]:
            labels = select(root,y=y)
            if c:
                panel(root,20,top,320,bottom-top,labels)
            panel(root,20,bottom,320,(731 if y==618 else 888)-bottom,
                  select(root,y=value_y),WHITE,GRAY,invert=False)
    elif code == 'PM-01':
        if c:
            for x in [88,643,1198]:
                panel(root,x-28,225,520,73,select(root,x=x,y=274))
                panel(root,x-28,310,520,130,select(root,x=x,y=407),WHITE,GRAY,invert=False)
            for x, ww, yy in [(60,1120,652),(1270,1070,652)]:
                ts = [t for t in select(root,y=yy) if x <= num(t,'x') < x+ww]
                panel(root,x,610,ww,62,ts)
        else:
            for x in [88,643,1198]:
                rule(root,x-28,442,x+492,select(root,x=x,y=407),GRAY,1.2)
    elif code == 'PM-02':
        if c:
            for x in [60,526,992,1458,1924]:
                ts=select(root,x=x,y=315)+select(root,x=x+113,y=305)
                panel(root,x-12,208,442,146,ts)
            panel(root,60,884,2280,57,select(root,y=923))
        else:
            for x in [60,526,992,1458,1924]:
                for y in [505,595,685,775]:
                    panel(root,x-7,y-39,405,49,select(root,x=x,y=y),WHITE,GRAY,invert=False)
    elif code == 'WH-01':
        ts=select(root,x=8,y=42)+select(root,x=8,y=54)
        if c:
            panel(root,4,23,143,36,ts)
        else:
            rule(root,8,59,145,ts,GRAY,.35)
    elif code == 'FL-01':
        for x in [25,316]:
            if c:
                panel(root,x-1,103,266,32,select(root,x=x,y=126))
            panel(root,x-1,142,266,56,select(root,x=x,y=182),WHITE,GRAY,invert=False)
    elif code == 'FL-02':
        for x in [60,440,820]:
            if c:
                panel(root,x-20,170,360,67,select(root,x=x,y=219))
            else:
                rule(root,x,237,x+320,select(root,x=x,y=219),GRAY,1)
    elif code == 'SW-01':
        for x in [14,147,280]:
            ts=select(root,x=x,y=159)
            if c:
                panel(root,x-2,148,126,16,ts)
            else:
                rule(root,x,166,x+124,ts,GRAY,.35)
    elif code == 'EQ-01':
        if c:
            panel(root,7,49,213,48,select(root,x=11,y=62)+select(root,x=11,y=84))
        pair_fields(root,[116,133,150,167],11,103,289,13,style)
    elif code == 'EQ-03':
        pair_fields(root,[30,40,50],5,39,95,7.5,style)
    elif code in QUALITY:
        pair_fields(root,[24,29.7,35.4,41.1],5,54,95,4.8,style)
    elif code == 'BT-02':
        pair_fields(root,[48.2,61.6,75,88.4,101.8,115.2],9.45,110,200.55,10.5,style)
    elif code == 'SW-02':
        for y in [108,150,192]:
            if c:
                # Existing three-step titles become a fixed vertical index rail.
                panel(root,14,y-20,86,34,select(root,x=17,y=y))
            else:
                rule(root,14,y+13,403,select(root,x=17,y=y),GRAY,.4)
    elif code == 'WH-03':
        if c:
            panel(root,8,73,194,15,select(root,y=82))
        for y in [35,46,57,68]:
            for x in [8,110]:
                panel(root,x-1,y-6,93,9.3,select(root,x=x,y=y),WHITE,GRAY,invert=False)
    elif code == 'WH-05':
        for x in [52,487]:
            if c:
                panel(root,x-16,275,393,51,select(root,x=x,y=311))
            else:
                rule(root,x,328,x+345,select(root,x=x,y=311),GRAY,1.2)
    elif code == 'VT-01':
        for y in [281,405,529]:
            if c:
                panel(root,35,y-31,524,41,select(root,x=59,y=y))
            else:
                rule(root,59,y+12,559,select(root,x=59,y=y),GRAY,.8)
        if c:
            panel(root,35,641,524,48,select(root,y=677))
    elif code == 'WF-03':
        if c:
            ts=[t for t in texts(root) if 43 < num(t,'y') < 303 and num(t,'x') < 875]
            panel(root,16,43,844,260,ts,WHITE)
        else:
            rule(root,45,178,1155,select(root,y=152),GRAY,1.5)
    elif code == 'ES-01':
        for y in [231,321,411,501,591]:
            if c:
                panel(root,24,y-28,546,39,select(root,y=y))
            else:
                rule(root,26.73,y+9,567.27,select(root,y=y),GRAY,.8)
        pair_fields(root,[707,749],26.73,318,567.27,32,style)
    elif code == 'BT-01':
        pair_fields(root,[219.15,268.15,317.15,366.15,415.15,464.15,513.15,562.15],
                    26.73,298,567.27,35,style)
    elif code == 'QC-05':
        if c:
            # This source is column-major: later white header-cell rects are
            # painted after the first heading. A single added band behind the
            # first heading would be covered by those later cells. Refinish
            # each existing cell instead, preserving all source geometry.
            for cell in root.iter(tag('rect')):
                if abs(num(cell,'y')-172)<.02 and abs(num(cell,'height')-65)<.02:
                    cell.set('fill',BLACK)
            for heading in select(root,y=215):
                heading.set('fill',WHITE)
        else:
            rule(root,36,237,1161,select(root,y=215),GRAY,1)
    elif code == 'EQ-02':
        pair_fields(root,[26,37,48,59,70],7.2,88,152.8,8.7,style)
    else:
        raise ValueError('No reviewed handler: '+code)


def quality_signature(root, code):
    if code not in QUALITY:
        return None
    header_rect=[e for e in root.iter(tag('rect')) if num(e,'x')==0 and num(e,'y')==0
                 and num(e,'width')==100 and num(e,'height')==19]
    return [ET.tostring(e,encoding='unicode') for e in header_rect] + [
        ET.tostring(t,encoding='unicode') for t in texts(root) if num(t,'y') <= 19]


def build():
    rows=list(csv.DictReader((SOURCE_DIR/'逐项样式与尺寸清单.csv').open(encoding='utf-8-sig')))
    unique={}
    for row in rows:
        unique.setdefault(row['可编辑源稿'],row)
    assert len(unique)==26
    variants=[]
    audits=[]
    for relative,row in unique.items():
        source=SOURCE_DIR/relative
        assert sha(source)==row['源稿SHA256'], source
        srcroot=ET.parse(source).getroot()
        contract=text_contract(srcroot)
        code=row['模板代码']
        w,h=int(row['板面名义宽_mm']),int(row['板面名义高_mm'])
        assert srcroot.get('width')==f'{w}mm' and srcroot.get('height')==f'{h}mm'
        old_metadata=[e.text for e in srcroot.iter(tag('metadata'))]
        qs=quality_signature(srcroot,code)
        graphics=[]
        for style in STYLES:
            sid=style['id']
            root=copy.deepcopy(srcroot)
            if sid=='B':
                hh=white_header(root,w,h,code)
                open_panels(root,w,hh,code)
                template_specific(root,code,sid,w,h)
            elif sid=='C':
                template_specific(root,code,sid,w,h)
            assert text_contract(root)==contract, (source,sid,'copy or geometry changed')
            assert quality_signature(root,code)==qs,(source,sid,'quality header changed')
            target=OUT/'styles'/sid/f'{source.stem}_STYLE-{sid}_V2.8-DRAFT.svg'
            target.parent.mkdir(parents=True,exist_ok=True)
            meta={
                'schema_version':'1.0','revision':'V2.8-CHOICE-DRAFT','style_id':sid,
                'style_label':style['label'],'code':code,'template_code':code,
                'source_path':str(source.relative_to(ROOT)),'source_sha256':sha(source),
                'nominal_size_mm':[w,h],'status':'style_option_pending_review',
                'production_release':False,'actual_point_id':None,'actual_dimensions_mm':None,
                'installation_height_mm':None,'world_coordinates':None,'quantity':None,
                'text_preserved':True,'text_geometry_preserved':True,'quality_header_preserved':True,
                'printed_source_revision_note':'Source wording, including printed source revision, is preserved verbatim; option edition appears in this metadata and review UI.',
                'source_metadata':old_metadata,
            }
            for p in root.iter():
                for el in list(p):
                    if el.tag==tag('metadata'):
                        p.remove(el)
            md=ET.Element(tag('metadata'),{'id':'beepump-v28-style-draft'})
            md.text=json.dumps(meta,ensure_ascii=False)
            root.insert(0,md)
            ET.ElementTree(root).write(target,encoding='utf-8',xml_declaration=True)
            sidecar=target.with_suffix('.meta.json')
            sidecar.write_text(json.dumps(meta,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
            variants.append({'style_id':sid,'source_path':str(source.relative_to(ROOT)),
                             'path':str(target.relative_to(ROOT)),'code':code,'name':row['模板名称'],
                             'nominal_size_mm':[w,h],'source_sha256':sha(source),'sha256':sha(target),
                             'text_preserved':True,'text_geometry_preserved':True,
                             'quality_header_preserved':True,'production_release':False})
            graphics.append(ET.tostring(root,encoding='unicode').split('</metadata>',1)[-1])
        assert len(set(graphics))==3,source
        audits.append({'code':code,'name':row['模板名称'],'source_path':str(source.relative_to(ROOT)),
                       'source_sha256':sha(source),'review':'Preserve source / Refine visual grouping',
                       'preserve':'全部源文字、字段、文字坐标、字号、名义整版宽高、模板代码、品质状态与动作',
                       'refine_B':STYLES[1]['description'],'refine_C':STYLES[2]['description'],
                       'source_render_evidence':[
                           f'交付_8楼/逐项样式尺寸_参观预览_V2.6/逐项详图/{row["详图编号"]}.png',
                           f'reports/options_v2.8/source_render/{code}.png'],
                       'required_follow_up':'逐份渲染对比；现场字高、固定面、实际尺寸、数量和安装仍需联合复核'})
    manifest={'revision':'V2.8-CHOICE-DRAFT','production_release':False,'floor_scope':'8F design baseline',
              'styles':STYLES,'source_count':len(unique),'variant_count':len(variants),
              'variants':variants,'audit':audits,
              'render_validation':'Pending main review renderer; XML/text/dimensions/quality contracts passed.',
              'source_index':str((SOURCE_DIR/'逐项样式与尺寸清单.csv').relative_to(ROOT))}
    OUT.mkdir(parents=True,exist_ok=True)
    (OUT/'style_manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'sources_reviewed':len(unique),'svg_options':len(variants),'text_preserved':True,
                      'text_geometry_preserved':True,'quality_header_preserved':True,
                      'manifest':str((OUT/'style_manifest.json').relative_to(ROOT))},ensure_ascii=False))


if __name__=='__main__':
    build()

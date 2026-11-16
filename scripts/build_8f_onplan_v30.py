#!/usr/bin/env python3
"""Direct annotations on the immutable 8F source preview, in display pixels only."""
import base64
import csv
import hashlib
import html
import json
import shutil
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SRC=ROOT/'design/v2/ground_logistics_v3.0'
OUT=ROOT/'交付_8楼/地面物流规划_V3.0'
REV='V3.0-ONPLAN-DRAFT'
W,H=3400,2400
BLUE,GREEN,RED,YELLOW,PURPLE='#005EB8','#00864A','#D81920','#F4C400','#8A3F86'
SHA='d368c39f3f5c9fdd2b783c8fc2949b6d1a744b03d5e9cafd172b17bc60a76918'

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
def txt(x,y,s,size=30,color='#000000',bold=False,anchor='start'):
    return f'<text x="{x}" y="{y}" font-size="{size}" fill="{color}" font-weight="{700 if bold else 400}" text-anchor="{anchor}">{html.escape(s)}</text>'
def rect(x,y,w,h,fill='none',stroke='none',sw=1,extra=''):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}" {extra}/>'
def line(points,color='#000000',sw=5,dash='',arrow=True):
    d='M'+' L'.join(f'{x},{y}' for x,y in points)
    return f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{sw}" stroke-dasharray="{dash}" stroke-linejoin="round"'+(' marker-end="url(#arrow)"' if arrow else '')+'/>'
def badge(x,y,s,color='#000000',small=False):
    w=48 if small else max(64,len(s)*17+14);return rect(x-w/2,y-15,w,29,'#FFFFFF',color,1.5)+txt(x,y+6,s,18 if small else 17,color,True,'middle')
def note(x,y,title,rows,width=1030):
    s=txt(x,y,title,34,bold=True)
    for i,row in enumerate(rows):s+=txt(x,y+46+i*40,row,27,'#3E3A39')
    return s

def main():
    SRC.mkdir(parents=True,exist_ok=True);OUT.mkdir(parents=True,exist_ok=True);(SRC/'地贴样式').mkdir(exist_ok=True)
    source=ROOT/'交付_8楼/地面物流规划_V2.9.1/原始底图_只读.png'
    expected=json.loads((ROOT/'交付_8楼/地面物流规划_V2.9.1/规划与来源.json').read_text())['source_png_sha256']
    assert sha(source)==expected
    frozen=json.loads((ROOT/'data/sources.json').read_text())['inputs']
    for f in frozen:assert sha(ROOT/f['path'])==f['sha256'],f['path']
    img='data:image/png;base64,'+base64.b64encode(source.read_bytes()).decode()
    evidence={'revision':REV,'recorded_on':'2026-10-18','source':'direct user messages in this chat','production_release':False,
        'verbatim_distance_statement':'我们的图纸距离等应该还是标准的。 请在图纸上直接标记',
        'distance_statement_scope':'用户认为图纸距离应为标准，要求直接标图；作为规划参考，不推定物理单位/图签冲突已经核验。',
        'verbatim_lift_reply':'原料仓附近的电梯组是收料，例如注塑壳等。 左上电梯组用于成品下楼去成品仓等。左下和右下电梯组暂时没有规划使用',
        'verbatim_employee_correction':'实际上员工是从原料仓旁边 中间的货梯上来的，因为货梯也可以载人。 只有客人从客梯上来',
        'lift_roles':{'raw_store_nearby_group':'收料＋员工到层（原料仓旁中间货梯，用户说明可载人）','upper_left_group':'成品下楼去成品仓等','lower_left_group':'暂未规划使用','lower_right_group':'暂未规划使用','small_passenger_lift_north_of_changing_room':'访客到层；位置沿用V2.7用户指认'},
        'door_to_door_paths_confirmed':False,'physical_unit_confirmed':False,'installation_approved':False}
    dump(OUT/'用户确认_收发电梯与直接标图.json',evidence)
    # These are display proposals, never survey/installation coordinates or bill quantities.
    routes=[
      {'id':'L01','name':'原料仓/电子仓 → 东侧补料主线','segments':[[[1233,484],[1182,484]],[[1233,711],[1182,711]],[[1182,406],[1182,739]]],'status':'proposed_internal_corridor','style':'solid'},
      {'id':'L02','name':'线体西端 → 适用测试/老化接口','segments':[[[696,423],[661,423],[661,610],[381,610],[381,638]]],'status':'proposed_output_side_and_test_interface','style':'solid'},
      {'id':'L03','name':'测试结论后 → 包装核对候选面','segments':[[[381,638],[381,622],[603,622],[603,337],[820,337],[820,316]]],'status':'after_quality_release_only','style':'dash'},
      {'id':'L04','name':'包装核对 → 成品交接 → 左上成品梯方向','segments':[[[900,275],[930,275]],[[1020,234],[1020,220],[234,220]]],'status':'upper_left_destination_user_confirmed_local_exit_pending','style':'solid'},
      {'id':'L05','name':'线边空车 → 空车归位候选面','segments':[[[687,464],[679,464],[679,345],[592,345],[592,318]]],'status':'empty_only_route_proposal','style':'dash'},
      {'id':'P01','name':'访客：已指认小客梯 → 既有进入示意；接待与获准观察范围另核','segments':[[[1386,222],[1453,222]],[[1412,258],[1412,329]],[[1424,370],[1504,370]],[[1489,441],[1505,512],[1505,569],[1469,604]],[[1420,612],[1185,612]]],'status':'visitor_only_prior_user_direction_sketch_not_approved_walkway','style':'purple_dash'},
      {'id':'P02','name':'员工：原料仓旁中间货梯到层；后续更衣/进入走段待核','segments':[[[1236,348],[1212,348],[1212,376]]],'status':'staff_arrival_user_confirmed_only_local_interface_indication_onward_path_unconfirmed','style':'purple_dot'},
      {'id':'C-IN','name':'原料仓旁收料梯出门接驳段待核','segments':[[[1236,315],[1182,315],[1182,394]]],'status':'interface_link_not_traversable_route_confirmed','style':'fine_dash'},
      {'id':'C-OUT','name':'左上梯接驳/分隔边界穿越门口待核','segments':[[[234,220],[164,220],[164,435],[126,435]]],'status':'interface_link_not_traversable_route_confirmed','style':'fine_dash'},
    ]
    # Individual line interfaces stop outside the source line bodies; no through-line route is asserted.
    for y in [423,530,610,722]:routes[0]['segments'].append([[1182,y],[1142,y]])
    for y in [530,610,721]:routes[1]['segments'].append([[696,y],[661,y]])
    routes[1]['segments'].append([[661,721],[661,610]])
    zones=[
      ('Z01','来料交接候选面',[1270,417,165,42],'#3E3A39','原料仓内侧；接收/批次/状态核对，非全批待检认定'),
      ('Z02','已放行备料候选面',[1270,527,165,40],GREEN,'原料仓内侧；仅实际放行批次与用途'),
      ('Z03','线边接收面候选',[1028,461,92,28],'#3E3A39','首段间隙示意；接口可调整，不缩窄东侧主线'),
      ('Z04','WIP等待候选面',[734,461,130,28],'#3E3A39','实际载具、批次、容量另核；非格位数量'),
      ('Z05','待测/适用老化候选面',[415,589,62,29],BLUE,'老化房北侧候选，需核门扇/取放及容量'),
      ('Z06','普通不合格候选面',[553,666,68,28],RED,'维修房接口候选，仅普通不良；不代替异常电池专项隔离'),
      ('Z07','冻结候选面',[553,729,68,25],YELLOW,'暂停使用；有独立批次与授权处置记录'),
      ('Z08','包装核对候选面',[760,235,140,80],'#3E3A39','现有成品区内提案，不表示已有包装设备'),
      ('Z09','成品放行交接候选面',[930,235,180,80],GREEN,'包装/放行后去左上电梯；等待量和接收预约另核'),
      ('Z10','空车归位候选面',[540,266,105,52],'#3E3A39','空车/空箱专用候选，不并入待检/不良/成品'),
    ]
    dims=[('D1','6773：线体东侧至原料仓侧向尺寸',[1195,567],'保留原图数值，不认作核定通道净宽'),('D2','2500：图示部分线体间距',[1153,475],'不自动变成可停车位或电动通道'),('D3','3500：仓边/端部局部尺寸',[1475,598],'门扇、载荷、操作及人行仍须核定')]
    def overlay(mode):
        s='<g data-layer="reserve" id="reserve">'
        # An indicative envelope follows the visible east-side corridor only.
        s+=rect(1148,399,74,349,'url(#reserveHatch)','#3E3A39',2,'stroke-dasharray="9 5"')
        s+=badge(1185,765,'E01')+'</g>'
        s+='<g data-layer="zones" id="zones">'
        for idx,name,(x,y,w,h),color,meaning in zones:
            if mode=='future' and idx not in ['Z03','Z10']:continue
            s+=rect(x,y,w,h,'#FFFFFF',color,3,'fill-opacity="0.62"')
            s+=txt(x+w/2,y+h/2+5,idx,15,'#000000' if color==YELLOW else color,True,'middle')
        s+='</g><g data-layer="routes" id="routes">'
        for route in routes:
            if route['id'] in ['P01','P02']:continue
            if mode=='future' and route['id'] not in ['L01','C-IN','C-OUT']:continue
            dash={'solid':'','dash':'10 6','fine_dash':'4 6'}[route['style']]
            sw=2.8 if route['style']=='fine_dash' else 5
            for seg in route['segments']:
                s+=line(seg,'#FFFFFF',sw+3,dash,False)+line(seg,'#000000',sw,dash)
        if mode!='future':
            for x,y,k in [(1182,449,'L01'),(660,551,'L02'),(603,475,'L03'),(537,220,'L04'),(678,375,'L05')]:s+=badge(x,y,k)
        s+='</g><g data-layer="people" id="people">'
        for seg in next(r for r in routes if r['id']=='P01')['segments']:
            s+=line(seg,'#FFFFFF',8,'10 6',False)+line(seg,PURPLE,4.5,'10 6',False)
        s+=badge(1530,424,'P01',PURPLE)
        for seg in next(r for r in routes if r['id']=='P02')['segments']:
            s+=line(seg,'#FFFFFF',8,'3 5',False)+line(seg,PURPLE,4.5,'3 5',False)
        s+=badge(1195,370,'P02',PURPLE)
        s+='</g><g data-layer="interfaces" id="interfaces">'
        for x,y,w,h,label in [(1248,259,80,115,'收料/员工'),(39,268,68,110,'成品梯')]:
            s+=rect(x,y,w,h,'none','#000000',4,'stroke-dasharray="7 4"')+badge(x+w/2,y-18,label)
        s+=badge(1319,180,'访客梯',PURPLE)
        for x,y in [(63,1248),(1289,1245)]:
            s+=rect(x-45,y-65,90,130,'none','#6B6B6B',2,'stroke-dasharray="4 4"')+badge(x,y+87,'暂不用','#6B6B6B')
        for x,y,idx in [(1184,612,'C1'),(213,220,'C2'),(1237,315,'C3')]:
            s+=f'<circle cx="{x}" cy="{y}" r="19" fill="white" stroke="#000000" stroke-width="2"/>'+txt(x,y+6,idx,17,bold=True,anchor='middle')
        for idx,name,(x,y),meaning in dims:s+=badge(x,y,idx,'#3E3A39',True)
        s+='</g>'
        return s
    layers={k:overlay(k) for k in ['total','detail','future']}
    pages=[]
    def make(num,title,body,kind,crop,transform):
        meta=dict(revision=REV,date='2026-10-18',status='direct_on_source_draft',source_drawing_sha256=SHA,source_png_sha256=expected,
            source_png_dimensions_px=[2200,1679],display_coordinate_frame='source PNG pixels: origin upper left, x right, y down',
            source_crop_display_px=crop,source_to_page_display_transform=transform,
            world_positions=None,physical_dimensions_mm=None,actual_quantity=None,approved_quantity=None,
            production_release=False,user_confirmed_lift_roles=evidence['lift_roles'],source_geometry_changed=False,
            annotations='proposed spatial overlay, not surveyed CAD points or fabrication dimensions')
        titlefull='8F 地面物流｜'+title
        svg=f'''<svg xmlns="http://www.w3.org/2000/svg" width="3400" height="2400" viewBox="0 0 3400 2400" role="img" aria-labelledby="title desc"><title id="title">{titlefull} {REV}</title><desc id="desc">直接叠加原图的物流/定置提案。原PNG字节保留，坐标为显示像素，尺寸与安装未放行。</desc><metadata>{html.escape(json.dumps(meta,ensure_ascii=False))}</metadata>
<defs><marker id="arrow" markerWidth="9" markerHeight="9" refX="7" refY="4" orient="auto" markerUnits="userSpaceOnUse"><path d="M0 0 L7 4 L0 8 Z" fill="#000000"/></marker><pattern id="reserveHatch" width="14" height="14" patternUnits="userSpaceOnUse"><path d="M-4 14 L14 -4 M3 21 L21 3" stroke="#3E3A39" stroke-width="1.2" opacity="0.28"/></pattern></defs>
<g font-family="PingFang SC,Microsoft YaHei,Noto Sans CJK SC,Arial,sans-serif">{rect(0,0,W,H,'#FFFFFF')}{rect(0,0,W,170,'#000000')}{txt(50,58,'BEEPUMP / 8F / 原图直接标注 / '+REV,28,'#FFFFFF')}{txt(50,125,titlefull,52,'#FFFFFF',True)}{txt(3340,113,f'{num:02d} / 03',36,'#FFFFFF',True,'end')}{txt(50,224,'原料仓旁中间货梯＝收料＋员工到层　｜　小客梯＝访客　｜　左上梯＝成品下楼　｜　左下/右下暂不用',31,bold=True)}
{body}
{line([[50,2255],[3350,2255]],'#A0A0A0',1,arrow=False)}{txt(50,2300,'直接标图评审稿 · 原图尺寸保留作规划参考 · 线/框为提案，尚非毫米放样与刷漆施工图',30,bold=True)}{txt(50,2347,'黑线=物流提案；P01紫虚线=访客示意，P02紫点线=员工到层接口；斜线带=未来电动预留。',27,'#3E3A39')}{txt(50,2384,'原图未改墙体/电梯/消防；图签、单位与真实通行/材料/数量待工程及现场核对。品牌橙不上地面。',25,'#3E3A39')}</g></svg>'''
        name=f'{num:02d}_{title}.svg';(SRC/name).write_text(svg);dump(SRC/name.replace('.svg','.meta.json'),meta);pages.append(name)
    def drawing(kind,x,y,width,height,vb):
        return f'<svg x="{x}" y="{y}" width="{width}" height="{height}" viewBox="{vb}" overflow="hidden"><image href="{img}" x="0" y="0" width="2200" height="1679"/>'+layers[kind]+'</svg>'

    body=drawing('total',50,270,2200,1679,'0 0 2200 1679')
    x=2310
    body+=note(x,305,'先看收发与员工/访客到层',['原料仓旁中间货梯：收料＋员工到层','左上梯组：包装/放行后下楼至成品仓','右上小客梯：访客到层；员工不走此入口'])
    body+=note(x,520,'黑色物流提案',['L01　原料仓/电子仓 → 东侧补料主线','L02　线体西端 → 测试/适用老化接口','L03　测试结论后 → 包装核对候选面','L04　包装 → 成品交接 → 左上梯方向','L05　线边空车 → 空车归位候选面'])
    body+=note(x,830,'图上定置索引（均为候选面）',['Z01 来料交接　　Z02 已放行备料','Z03 线边接收　　Z04 WIP等待','Z05 待测/老化　 Z06 普通不合格','Z07 冻结　　　　Z08 包装核对','Z09 成品交接　　Z10 空车归位'])
    body+=note(x,1138,'员工/访客分开标，电动另预留',['P01 紫虚线：客梯到层的访客进入示意','P02 紫点线：中间货梯的员工到层接口','E01 斜线带：未来电动预留关系，宽度另核','员工后续更衣/进入条件与走段另核'])
    body+=note(x,1405,'C1-C3 必须保留的接驳核查',['C1：访客示意与东侧补料主线交叉处','C2：成品去左上梯的分隔边界/门口','C3：中间梯收料/员工到层的接驳与分流','细点虚线只表达连接目标，尚未核通行'])
    body+=note(x,1680,'使用本图',['先审走向、收发、候选面及冲突；再量尺','框数/线条数/索引数不作为现场数量','本轮不改原CAD、不建真实点位或工程量'])
    body+=note(70,2040,'原图尺寸仍可追溯',['D1=原图6773；D2=部分线体间距2500；D3=仓边局部3500。均为原图标签，不是本轮新定路宽。','完整底图保持原像素与纵横关系；局部放大见第2、3页。空白部分不认定为可新增生产或堆放场地。'])
    make(1,'收发物流与定置总图',body,'total',[0,0,2200,1679],[1,0,0,1,50,270])

    # Crop and scale the SAME embedded image and SAME overlay; do not re-place objects.
    body=drawing('detail',50,280,3300,1254,'0 165 1850 703')
    body+=note(60,1630,'图上走线怎么用',['来料在原料仓旁梯组上楼；C3细虚线段先核出门/接驳，再接L01补料主线。','线边只接收有身份与放行依据的物料；Z03/Z04是候选接口，容量与真实格位数另核。','L02不表示每一工单都必须老化；普通返修按处置单接Z06，完成后回指定复验接口。'],width=1600)
    body+=note(1760,1630,'包装与成品怎么走',['测试结论合格后按L03到Z08包装核对；Z09放行交接后去左上成品梯。','左上梯用途已确认，C2穿越边界与具体门口尚待核对；不得按虚线穿墙。','Z10为空车归位候选；空车身份与满载物料、品质状态分开，不占主线。'],width=1590)
    body+=note(60,1910,'地面标识对应',['Z03/Z04/Z08/Z10：白框配用途文字；真实位号、长宽、字高与上限经核定后填。','Z05蓝待检、Z09绿放行、Z06红不合格、Z07黄冻结：状态词、批次/容器和动作范围同时可见。','L01等黑线仅为图纸物流注释；未来可用的通道边界漆色沿FM-01规则另核，不将黑/紫路线照搬刷漆。'])
    make(2,'作业区物流与地标放大图',body,'detail',[0,165,1850,703],[3300/1850,0,0,1254/703,50,280-165*1254/703])

    body=drawing('future',70,280,2332,1632.4,'540 165 1080 756')
    body+=note(2460,330,'E01 东侧电动预留',['沿现有线体与仓房之间标关系范围','不以图上斜线带像素反算毫米','满载外廓含货物、车辆与操作人员','直线、转弯、会车和交接联动核定'])
    body+=note(2460,650,'P01 访客；P02 员工到层',['P01：访客由右上小客梯到层','P02：员工由原料仓旁中间货梯到层','P02只标到层接口，不套用客人走线','员工后续更衣/进入条件与走段待核'])
    body+=note(2460,970,'中间梯收料与员工接驳',['中间货梯：收料＋员工到层（用户确认）','小客梯：仅访客到层','C3处核员工出梯与物料交接的分流','两组电梯的具体设备条件分别确认'])
    body+=note(2460,1285,'优先避免的定置冲突',['线边接收面不新增在E01主线中央','不把原料仓门口变成临时等候位','货物外廓、转向及取放不得侵入人行','当前人工用法与未来电动分别核定'])
    body+=note(2460,1600,'现阶段放样安排',['先核员工、访客、收料各自接驳','范围未核前，线边框位可调整','门口、消防、检修等原边界不动','车型未定，不放置充电/换电设施'])
    body+=note(70,2020,'保留原图距离，不把它当成新批准尺寸',['D1=6773、D2=2500、D3=3500均源于原图标注；净宽还须扣核固定边界、门扇、载荷与操作范围。','未来电动是预留意向：需型号/工况参数和现场演练后，才确定控制包络、线宽、地贴尺寸及数量。'])
    future_scale=2332/1080
    make(3,'人行与电动预留放大图',body,'future',[540,165,1080,756],[future_scale,0,0,future_scale,70-540*future_scale,280-165*future_scale])

    refs=['data/8F_logistics_user_requirements_v2.9.1.json','data/tasks.json','docs/DECISIONS.md','outputs/drawings/8F_candidate_calibration.json','outputs/implementation_v2.4/cad/8F_existing_candidate_partial_metadata.json','交付_8楼/客梯入口修订_V2.7/标注来源与核对台账_V2.7.json','docs/CAD_WORKFLOW.md']
    for r in routes:r.update(display_units='source_png_px',world_geometry=None,physical_quantity=None,approved=False)
    zrecords=[dict(id=i,name=n,source_display_rect_px=box,outline_semantics=c,meaning=meaning,area_id=None,world_polygon=None,physical_dimensions_mm=None,actual_quantity=None,approved_quantity=None,status='candidate_interface_region_not_measured') for i,n,box,c,meaning in zones]
    manifest=dict(revision=REV,created_on='2026-10-18',source_png_path=str(source.relative_to(ROOT)),source_png_sha256=expected,source_drawing_sha256=SHA,immutable_inputs_verified=len(frozen),production_release=False,
        user_confirmations=evidence,source_records=[dict(path=p,sha256=sha(ROOT/p)) for p in refs],pages=pages,proposed_display_routes=routes,proposed_display_zones=zrecords,
        actual_cad_points=[],actual_cad_routes=[],physical_unit=None,mm_factor=None,actual_quantities=None,
        reservation=dict(id='E01',source_display_rect_px=[1148,399,74,349],kind='indicative_spatial_envelope_only',actual_width_mm=None,world_polygon=None),
        numeric_dimensions=[dict(id=i,label=n,source_display_anchor_px=p,meaning=meaning,not_new_design_dimension=True) for i,n,p,meaning in dims],
        unresolved=['图身八层/图签三层与物理单位仍待核验','C1访客示意与物流交叉条件','C2左上梯分隔边界与门口','C3中间梯收料与员工到层接驳/分流','P02员工后续更衣/进入条件与实际走段','线头接收面/西侧出料与测试适用性/候选面实际可用性','人工实车与未来电动车型/转弯包络/接收容量','地面线宽/字高/坐标/材料/数量/制作安装及适用专项确认'])
    dump(OUT/'原图标注与来源.json',manifest)
    dump(SRC/'revision_metadata.json',dict(revision=REV,status='draft',production_release=False,manifest='交付_8楼/地面物流规划_V3.0/原图标注与来源.json',physical_dimensions_mm=None))
    with (OUT/'图上标记核对清单.csv').open('w',encoding='utf-8-sig',newline='') as f:
        fields=['索引','类别','用途','来源或依据','待核内容','CAD世界坐标','真实尺寸_mm','提案工程量','批准工程量','制作安装放行'];w=csv.DictWriter(f,fieldnames=fields);w.writeheader()
        for r in routes:w.writerow(dict(zip(fields,[r['id'],'图上候选路线',r['name'],'用户收发梯及主流程；源图门口/通道关系',r['status'],'','','','','否'])))
        for z in zrecords:w.writerow(dict(zip(fields,[z['id'],'图上候选定置面',z['name'],'原图显示关系；候选选面',z['meaning'],'','','','','否'])))
        w.writerow(dict(zip(fields,['E01','图上候选预留','未来电动搬运空间','用户未来电动预留意向','未来型号/两工况/宽度与转弯均待核','','','','','否'])))
    shutil.copy2(source,OUT/'原始底图_只读.png');shutil.copytree(SRC,OUT/'可编辑SVG',dirs_exist_ok=True)
    (OUT/'先读说明.md').write_text('''# 8F 原图直接标注 V3.0（评审稿）

已按用户指定直接在原图上叠加空间提案：原料仓旁中间货梯收料＋员工到层，左上梯成品下楼；左下/右下暂不规划使用。更衣室北侧小客梯仅访客到层，位置延用此前用户指认。人工周转车现状、未来考虑电动搬运预留和主流程沿用本次用户确认。用户说明该货梯可以载人，作为用户运营说明记录；没有代造设备批准记录。

01总图保留完整PNG；02放大作业区；03放大东侧补料、人行与电动预留。三个图使用同一张只读PNG及同一组叠加图形，裁切/显示变换另存。原墙体、柱、电梯、门和文字不编辑，源PNG嵌入哈希保留。

L01-L05是空间路线提案；P01是访客既有进入示意；P02只标员工在原料仓旁中间货梯到层接口，后续更衣/进入条件与走段待核，不沿用客人路线。C-IN/C-OUT细点虚线是尚未核实的接驳关系，禁止据此穿墙或组织车辆通行。C1核访客交叉；C2核成品至左上梯的分隔边界/门口；C3核中间梯收料、员工到层接驳与分流。老化按实际工单适用，不强制所有产品经过。电子仓不改称电池仓。普通返修不包含异常电池包专项处置。

Z01-Z10是候选用途/选面索引，不是区域正式编号、实际格位数或地贴件数。E01是图上候选预留关系，不是经核定的车道包络；框宽像素不对应实际宽度。候选位置仍须生产、品质、工程与安全按职责现场核查。原图空白不证明现场可用空地。

原图尺寸D1=6773、D2=部分线体间距2500、D3=局部3500仅作来源核对，不是本轮新给的毫米设计尺寸或合规净宽。用户认为原图距离应为标准，作为规划参考记录；图签/物理单位及两向现场尺度仍待核。未生成实际CAD点、毫米坐标、线长/面积、工程量或批准记录。

黑/紫线是图纸注释。质量色含蓝待检、绿放行、红不合格、黄冻结，需保留用途文字、批次/容器、动作与范围；不赋予通行优先。品牌橙不上地面。实际刷漆/贴标另用经核定的定位图、材料、线宽/字高/成品尺寸和数量。
''')
    # Inline source maps permit offline layer toggles without fetch or external requests.
    maps=''.join('<section>'+ (SRC/n).read_text()+'</section>' for n in pages)
    controls=''.join(f'<label><input type="checkbox" checked data-toggle="{k}">{v}</label>' for k,v in [('routes','物流提案'),('people','人员示意'),('zones','定置候选面'),('reserve','电动预留'),('interfaces','接口与核查索引')])
    (OUT/'打开原图标注.html').write_text('''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>8F 原图直接标注 V3.0</title><style>body{margin:0;font-family:PingFang SC,Arial,sans-serif;background:#eee}header{padding:24px;background:white}h1{margin-top:0}p,label,a{font-size:18px;line-height:1.6}label{display:inline-block;margin-right:24px}input{margin-right:7px}a{color:#000}a:focus-visible,input:focus-visible{outline:3px solid #005EB8}section{margin:24px auto;max-width:3400px;background:white}section>svg{width:100%;height:auto;display:block}@media print{header{display:none}section{margin:0;break-after:page}@page{size:A3 landscape;margin:0}}</style><header><h1>8F 地面物流：原图直接标注 V3.0</h1><p>收料梯与成品下楼梯已按用户说明标出；线、框及预留带为候选提案。先审位置关系，未毫米放样或制作安装放行。</p><p><a href="8F_地面物流与地标规划_评审稿.pdf">打开3页PDF</a> · <a href="图上标记核对清单.csv">标记核对清单</a> · <a href="原图标注与来源.json">来源与坐标边界</a></p>'''+controls+'</header>'+maps+'''<script>document.querySelectorAll('[data-toggle]').forEach(i=>i.addEventListener('change',()=>document.querySelectorAll('[data-layer="'+i.dataset.toggle+'"]').forEach(g=>g.style.display=i.checked?'':'none')))</script></html>''')
    print(json.dumps(dict(revision=REV,pages=len(pages),output=str(OUT)),ensure_ascii=False))

if __name__=='__main__':main()

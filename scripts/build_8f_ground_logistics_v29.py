#!/usr/bin/env python3
"""Local 8F floor-marking review; no world points, dimensions or approvals."""
import base64
import csv
import hashlib
import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / 'design/v2/ground_logistics_v2.9'
OUT = ROOT / '交付_8楼/地面物流规划_V2.9'
REV = 'V2.9-GROUND-LOGISTICS-DRAFT'
SHA = 'd368c39f3f5c9fdd2b783c8fc2949b6d1a744b03d5e9cafd172b17bc60a76918'
COL = dict(yellow='#F4C400', blue='#005EB8', green='#00864A', red='#D81920', gray='#969B9F')
W, H = 1680, 1188

def dump(p, data):
    p.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')

def text(x, y, value, size=24, fill='#000000', weight=400, anchor='start'):
    return f'<text x="{x}" y="{y}" font-size="{size}" fill="{fill}" font-weight="{weight}" text-anchor="{anchor}">{html.escape(value)}</text>'

def lines(x, y, rows, size=23, gap=36, fill='#3E3A39', weight=400):
    return ''.join(text(x, y+i*gap, s, size, fill, weight) for i, s in enumerate(rows))

def rect(x,y,w,h,fill='none',stroke='none',sw=1):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>'

def path(d,stroke='#3E3A39',sw=4,dash='',arrow=False):
    return f'<path d="{d}" fill="none" stroke="{stroke}" stroke-width="{sw}" stroke-dasharray="{dash}"'+(' marker-end="url(#arrow)"' if arrow else '')+'/>'

def panel(x,y,w,h,title,rows):
    return rect(x,y,w,h,'#F3F3F3')+text(x+24,y+42,title,28,weight=700)+lines(x+24,y+85,rows,22,34)

def page(num,title,subtitle,body,code='FM-01'):
    meta = dict(revision=REV,status='draft_review_only',floor_scope='8F',template_reference=code,
        created_on='2026-10-18',page_unit='display_px',physical_dimensions_mm=None,
        position_world=None,actual_quantity=None,approved_quantity=None,production_release=False,
        source_drawing_sha256=SHA,scale='not_to_scale',original_geometry_changed=False)
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="1680" height="1188" viewBox="0 0 1680 1188" role="img" aria-labelledby="title desc">
<title id="title">{html.escape(title)} {REV}</title><desc id="desc">设计评审草案，不按比例；不是定位放样图。尺寸、数量与批准待核。</desc>
<metadata>{html.escape(json.dumps(meta,ensure_ascii=False))}</metadata>
<defs><marker id="arrow" markerWidth="10" markerHeight="10" refX="8" refY="5" orient="auto-start-reverse"><path d="M0 1 L8 5 L0 9" fill="none" stroke="#3E3A39" stroke-width="1.7"/></marker></defs>
<g font-family="PingFang SC,Microsoft YaHei,Noto Sans CJK SC,Arial,sans-serif">
{rect(0,0,W,H,'#FFFFFF')}{rect(0,0,W,115,'#000000')}
{text(40,40,'BEEPUMP / 8F / 地面物流与定置规划',20,'#FFFFFF',500)}
{text(40,88,title,36,'#FFFFFF',700)}{text(1640,45,f'{code} · {num:02d} / 07',21,'#FFFFFF',700,'end')}
{text(40,154,subtitle,23)}
{body}
{path('M40 1105 H1640','#B0B0B0',1)}
{text(40,1138,'评审草案 · 不按比例 · 图中像素不是毫米 · 不得直接放样施工',21,weight=700)}
{text(40,1170,REV+' / 2026-10-18 / 品牌橙不上地面 / 实际点位未勘测，数量待核',18,'#3E3A39')}
{text(1640,1154,f'{num:02d}',32,weight=700,anchor='end')}
</g></svg>'''
    name=f'{num:02d}_{title.split("｜")[-1]}.svg'
    (SRC/name).write_text(svg,encoding='utf-8')
    dump(SRC/name.replace('.svg','.meta.json'),meta)
    return name

def write_csv(name, fields, rows):
    with (OUT/name).open('w',encoding='utf-8-sig',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=fields);writer.writeheader();writer.writerows(rows)

def main():
    SRC.mkdir(parents=True,exist_ok=True);OUT.mkdir(parents=True,exist_ok=True)
    (SRC/'地贴样式').mkdir(exist_ok=True)
    inventory=json.loads((ROOT/'data/sources.json').read_text())
    for item in inventory['inputs']:
        assert hashlib.sha256((ROOT/item['path']).read_bytes()).hexdigest()==item['sha256'],item['path']
    ann_path=ROOT/'交付_8楼/客梯入口修订_V2.7/标注来源与核对台账_V2.7.json'
    ann=json.loads(ann_path.read_text())
    source=ROOT/ann['source_png']
    assert hashlib.sha256(source.read_bytes()).hexdigest()==ann['source_png_sha256']
    png='data:image/png;base64,'+base64.b64encode(source.read_bytes()).decode()
    pages=[]

    # Relationship map: schematic, with no architectural outline or real route.
    b=text(40,207,'主物流：按工单和品质结论向下游交接',29,weight=700)
    nodes=[('跨层来料','货梯及收货端待核'),('收讫 / 状态核对','待检与放行分开'),('已放行备料','原料 / 电子物料'),('装配线边接收','先入先用 · 满位停收'),('测试 / 适用老化','按实际工艺分支'),('包装 / 成品交接','放行后预约转运')]
    for i,(title,sub) in enumerate(nodes):
        x=40+i*270
        b+=rect(x,239,247,140,'#F3F3F3','#3E3A39',2)+text(x+18,283,title,25,weight=700)+text(x+18,328,sub,18)
        if i<5:b+=path(f'M{x+247} 309 H{x+265}',arrow=True,sw=3)
    b+=rect(40,412,1600,144,'#D8DADB')+path('M65 432 H1615',COL['yellow'],7)+path('M65 536 H1615',COL['yellow'],7)
    b+=text(75,484,'物流通道示意',29,weight=700)+text(420,484,'供料 → 接收 → 下游交接；实际单／双向、转弯及净宽待核',26)
    b+=text(75,518,'本带仅表达功能，不对应原图上的任何一条通道',19)
    b+=path('M290 603 H1540',sw=4,dash='12 9',arrow=True)
    b+=text(40,610,'人员关系',27,weight=700)+text(330,646,'右上客梯（用户指认） → 更衣／进入条件核对 → 已确认人行路径 → 岗位',25)
    b+=text(330,681,'访客由陪同带到获准观察面；不默认进入线边、测试房或物流作业面',23)
    b+=panel(40,729,505,201,'返回支线｜空车 / 空箱',['线边退出 → 清点检查 → 核定空车位','返程与供料是否共道，按实车演练决定','不以空车位代替待检或不良区'])
    b+=panel(565,729,520,201,'质量支线｜待检 / 冻结 / 不合格',['在对应接口受控分流；颜色加文字','普通返修按处置单 → 指定复验口','异常电池包另按已批准专项流程'])
    b+=panel(1105,729,535,201,'布置原则｜先分流，再定置',['物流到线边接收面，不穿过操作位','收、发、空车分位；满位停止接收','出入口、转弯及交叉处不新增堆位'])
    b+=lines(40,987,['图纸来源：V2.3物流研究、V2.4功能关系、V2.7客梯修订；本轮未确认实际工序顺序。','老化是条件分支；电子仓不等于电池仓；PCBA文字不证明现场PCBA制造。'],22,37)
    pages.append(page(1,'8F 地面物流规划｜物流关系总图','先确定“从哪里来、交给谁、在哪里等、空车怎么回”；本页不表示建筑位置。',b,'FM-01 / FL-02'))

    # Source anchors retain the original PNG; no proposed route lines on unverified geometry.
    b=rect(40,184,1080,824,'#FFFFFF','#B0B0B0')
    b+=f'<image href="{png}" x="40" y="184" width="1080" height="824" preserveAspectRatio="xMidYMid meet"/>'
    # A badge marks an existing source object only. No world-coordinate conversion is performed.
    anchors=[('A','原料仓',1310,470),('B','电子仓',1317.21,710.36),('C','PCBA / 半成品',1620.86,719.78),('D','成排工位图形',910,490),('E','老化房 / 维修房',455,705),('F','成品区',1032.16,287.41),('G','客梯 / 更衣接口',1319,200)]
    source_refs=[]
    for letter,title,x,y in anchors:
        sx=40+x*1080/2200;sy=184+y*824/1679
        b+=f'<circle cx="{sx}" cy="{sy}" r="19" fill="#FFFFFF" stroke="#000000" stroke-width="2"/>'+text(sx,sy+7,letter,23,weight=700,anchor='middle')
        source_refs.append(dict(drawing_index=letter,source_object=title,source_preview_pixel_anchor=[x,y],anchor_is_source_reference_only=True,position_world=None,proposed_installation_position=None))
    b+=text(1150,215,'沿这些源对象核对定置接口',25,weight=700)
    items=[('A 原料仓','核收货、放行储位及发料接口'),('B 电子仓','核线边供料；不命名为电池仓'),('C PCBA / 半成品','先核实际业务与接收对象'),('D 成排工位图形','核实际线尾／线头与补料面'),('E 老化房 / 维修房','核测试支线、普通返修及复验'),('F 成品区','核包装、放行与待运是否在此'),('G 客梯 / 更衣接口','延用用户右上客梯指认；核人行')]
    for i,(a,c) in enumerate(items):b+=text(1150,269+i*85,a,24,weight=700)+text(1150,301+i*85,c,20)
    b+=lines(1150,904,['货梯身份与货物出入口：待核','不把客梯当默认物流入口','A-G是资料核对索引，不是安装点'],20,34,weight=500)
    b+=text(40,1046,'底图完整嵌入原PNG；保留墙、柱、电梯及源文字。标记只指向来源对象，未画可施工路线。',21)
    b+=text(40,1080,'图身“八层”／图签“三层”冲突；单位未核；部分实体、字体未完整复现。源图空白不证明可堆物。',21)
    pages.append(page(2,'8F 地面物流规划｜原图核对索引','原图只用于核对对象和候选接口；不量图、不由像素反算毫米。',b))

    # Six drawing details. Display geometry is illustrative only.
    details=[('M01 物流通道','长边界可评估刷漆；箭头作可更换地贴','线色沿用V1黄色示例，待现场样色确认'),('M02 人行通路','文字与物流区分；不使用质量放行绿','交叉处另核可视性、候行及实际控制'),('M03 周转车定位','白色外框 + 用途文字 + 经确认位号','按满载外廓与取放空间核定车位'),('M04 固定设备定位','白色角标只表达设备归位关系','检修、门扇和操作边界另行核定'),('M05 线边 FIFO','入位／出位口与等待格分开识别','实际车格数和WIP上限由现场核定'),('M06 保持畅通提示','普通管理文字；不替代安全标识','只用于已确认的保持畅通边界')]
    b=''
    for i,(title,desc,note) in enumerate(details):
        x=40+(i%3)*545;y=192+(i//3)*430
        b+=text(x,y+28,title,26,weight=700)+rect(x,y+50,510,230,COL['gray'])
        if i in [0,1]:
            b+=path(f'M{x+25} {y+86} H{x+485} M{x+25} {y+244} H{x+485}',COL['yellow'],7)
            b+=text(x+255,y+180,'物流 →' if i==0 else '人行通路',40,'#FFFFFF',700,'middle')
        elif i==2:
            b+=rect(x+45,y+80,420,165,'none','#FFFFFF',7)+text(x+255,y+155,'周转车',36,'#FFFFFF',700,'middle')+text(x+255,y+210,'位号待核',24,'#FFFFFF',500,'middle')
        elif i==3:
            for xx,yy,dx,dy in [(x+50,y+90,65,55),(x+460,y+90,-65,55),(x+50,y+242,65,-55),(x+460,y+242,-65,-55)]:
                b+=path(f'M{xx+dx} {yy} H{xx} V{yy+dy}','#FFFFFF',7)
            b+=text(x+255,y+180,'设备归位',36,'#FFFFFF',700,'middle')
        elif i==4:
            b+=rect(x+45,y+85,420,155,'none','#FFFFFF',7)+path(f'M{x+255} {y+85} V{y+240}','#FFFFFF',4)
            b+=text(x+140,y+180,'先入',32,'#FFFFFF',700,'middle')+text(x+360,y+180,'后入',32,'#FFFFFF',700,'middle')
        else:b+=rect(x+45,y+85,420,155,'none','#FFFFFF',7)+text(x+255,y+180,'保持畅通',38,'#FFFFFF',700,'middle')
        b+=text(x,y+321,desc,21)+text(x,y+358,note,20)+text(x,y+393,'线宽 / 实际长宽 / 位置：待核',20,weight=700)
    b+=text(40,1080,'M01-M06为详图索引；不是新增模板编号或地面位置。黄色通道线与黄色“冻结”区靠用途文字区分。',21)
    pages.append(page(3,'8F 地面物流规划｜刷漆与定置样式','延续FM-01原有通道边界、移动物框和设备角标；不将线色示例作为安全标准。',b))

    labels=[('S01','物流方向 →','方向按真实通行核定','#FFFFFF','#000000'),('S02','人行通路','仅用于已确认人行路径','#FFFFFF','#000000'),('S03','线边接收','满位停收 · 上限另卡管理','#FFFFFF','#000000'),('S04','空车返回','保持空车与物料身份分开','#FFFFFF','#000000'),('S05','待检','未经放行不得投入使用',COL['blue'],'#FFFFFF'),('S06','合格放行','仅限实际放行批次及用途',COL['green'],'#FFFFFF'),('S07','不合格','隔离 · 按处置单流转',COL['red'],'#FFFFFF'),('S08','冻结 HOLD','暂停使用 · 待授权处置',COL['yellow'],'#000000')]
    b=''
    for i,(idx,title,sub,color,fg) in enumerate(labels):
        x=40+(i%4)*405;y=195+(i//4)*350
        b+=text(x,y+25,idx+' / 地贴文字样式',21,weight=700)+rect(x,y+48,385,150,color,'#3E3A39',2)
        b+=text(x+192.5,y+110,title,32,fg,700,'middle')+text(x+192.5,y+160,sub,18,fg,400,'middle')
        b+=lines(x,y+238,['实际成品长宽 / 字高：待核','材质 / 表面 / 粘接：待实地试样'],20,33)
        metadata=dict(revision=REV,template_reference='FM-01',detail_index=idx,detail_index_is_not_location_id=True,
            physical_dimensions_mm=None,actual_quantity=None,production_release=False,position_world=None,
            status='artwork_review_only_not_cut_file',source_drawing_sha256=SHA,source_template='FM-01')
        artwork=f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 400" width="800" height="400"><title>{idx} {html.escape(title)} 评审草案</title><metadata>{html.escape(json.dumps(metadata,ensure_ascii=False))}</metadata><g font-family="PingFang SC,Microsoft YaHei,Arial,sans-serif">'+rect(0,0,800,400,'#FFFFFF')+text(25,35,idx+' / '+REV+' / 尺寸待核，未制作放行',20)+rect(25,65,750,270,color,'#3E3A39',2)+text(400,185,title,67,fg,700,'middle')+text(400,265,sub,34,fg,400,'middle')+text(25,380,'评审画布单位为px；不是1:1切割／打印文件。',24)+'</g></svg>'
        (SRC/'地贴样式'/f'{idx}.svg').write_text(artwork,encoding='utf-8');dump(SRC/'地贴样式'/f'{idx}.meta.json',metadata)
    b+=panel(40,940,1600,140,'文字、框位与状态卡协同',['地贴表示区域用途；品质状态仍须关联批次、容器和实际放行记录。颜色本身不能批准使用或通行。','黄冻结保留“冻结 HOLD”；地面不增加疏散箭头、消防、电池应急或ESD符号，专项素材另经确认。'])
    pages.append(page(4,'8F 地面物流规划｜地贴文字样式','先核文字和辨识，再确认成品尺寸；S01-S08是样式索引，不是地贴数量。',b))

    b=''
    for i,(title,rows) in enumerate([
        ('交接端｜到货、待运、空车分开',['实际货梯身份与可用出入口先确认','到货接收位 / 成品待运位 / 空车位分别核定','前室、门扇及设备前不作为默认等候位']),
        ('线边｜接收面与操作面分开',['物流端交给指定线边接口，核实取放姿态','按真实容器设置FIFO位；不在通道追加格位','上限由真实接收容量确定，满位暂停接收']),
        ('测试｜按工艺分支与结论流转',['待检 → 适用测试／老化 → 结论后分流','放行到下一接口；普通不合格按单返修','返修完成回指定复验口，不直接回合格区']),
        ('交叉｜人行到岗位，物流到接收面',['优先评估减少物流与正常人行的交叉','交叉点实测可视性、满载转弯与候行空间','需要实体隔离／控制的，由工程和安全深化'])]):
        x=40+(i%2)*815;y=190+(i//2)*435
        b+=text(x,y+30,title,28,weight=700)+lines(x,y+77,rows,23,37)
        b+=rect(x,y+196,780,166,'#D8DADB')
        if i==0:
            for j,t in enumerate(['到货接收','成品待运','空车归位']):b+=rect(x+25+j*250,y+221,230,112,'none','#FFFFFF',5)+text(x+140+j*250,y+285,t,25,weight=700,anchor='middle')
        elif i==1:
            b+=text(x+25,y+243,'物流侧 →',23,weight=700)+rect(x+190,y+213,340,126,'none','#FFFFFF',5)+text(x+360,y+269,'FIFO接收位',28,weight=700,anchor='middle')+text(x+360,y+311,'数量 / 上限待核',21,anchor='middle')+text(x+570,y+286,'→ 作业侧',24,weight=700)
        elif i==2:
            for j,(t,c) in enumerate([('待检',COL['blue']),('放行',COL['green']),('不合格',COL['red'])]):b+=rect(x+25+j*250,y+221,230,112,'#FFFFFF',c,6)+text(x+140+j*250,y+285,t,28,c,700,'middle')
        else:
            b+=text(x+35,y+254,'人行路径',26,weight=700)+path(f'M{x+210} {y+247} H{x+700}',sw=3,dash='10 8',arrow=True)+text(x+35,y+323,'物流到接收面：实际交叉方式、让行和隔离条件待核',22)
    b+=text(40,1080,'本页小框只表达接口分离关系；框数不等于车位数，示意宽度不等于实际净宽。异常电池包按专项流程。',21)
    pages.append(page(5,'8F 地面物流规划｜关键接口详图','把“可通行、可接收、可识别、可返回”逐项落到操作；详图不对应实际坐标。',b,'FM-01 / FL-01 / FL-02'))

    b=panel(40,190,780,260,'先做可移除放样，再决定刷漆',['① 锁定有效8F底图、现场用途和货梯接口','② 测车辆满载外廓、双向会车及转弯包络','③ 核门扇、消防、疏散、检修和人行边界','④ 临时放样并实车演练，形成问题和修订记录','⑤ 内容、位置、安装及适用安全记录闭合后发施工图'])
    b+=panel(850,190,790,260,'刷漆 / 地贴的分工提案',['稳定且确认的长边界：评估地坪兼容标线涂层','方向、用途和易改位文字：评估可更换地贴','质量状态以区域文字配合实际批次状态卡','现场确认基层、防滑、清洁及适用ESD相容性','涂层体系、固化与恢复通行按获准产品资料执行'])
    b+=text(40,508,'必须在现场填实的尺寸与依据',30,weight=700)
    rows=[('通道净宽 W','车辆与货物最大外廓、会车／单向方案、人员分流','待核'),('转弯／交叉包络 R','实车满载演练、视线及门扇范围；不套示意半径','待核'),('线宽 b / 线色','批准专项图、既有现场体系、样色及可辨识性','待核'),('车位长宽 L × B','实际容器外廓、取放和经核定余量；不是图上格子','待核'),('字高 h / 地贴长宽','真实观看方向、距离、遮挡与足尺样品核读','待核'),('总线长 / 数量','经核定路线、真实格位与去重清单；不按需求条数算','待核')]
    yy=543
    b+=rect(40,yy,1600,48,'#000000')+text(60,yy+32,'项目',23,'#FFFFFF',700)+text(430,yy+32,'确定依据',23,'#FFFFFF',700)+text(1510,yy+32,'数值',23,'#FFFFFF',700)
    for i,(a,c,d) in enumerate(rows):
        y=yy+48+i*61;b+=rect(40,y,1600,61,'#F3F3F3' if i%2==0 else '#FFFFFF','#D0D0D0')+text(60,y+38,a,23)+text(430,y+38,c,22)+text(1510,y+38,d,23,weight=700)
    b+=lines(40,1007,['地面试样记录：附着、轮载／转向、边缘翘起、湿清洁与防滑；适用时测ESD性能。结果留待实测。','不新造养护时间、材料厚度、地坪面积或采购量；破损／反光／识别不足时修订做法，再复验。'],22,38)
    pages.append(page(6,'8F 地面物流规划｜放样与施工交接','先完成可审阅方案；实际施工仅使用现场核定并经责任人确认的尺寸、材料和边界。',b))

    b=text(40,207,'核量口径：刷漆、胶带、地贴分开；提案量与批准量分开',28,weight=700)
    qty=[('通道／分区漆线','m；m²','按实际每条线段核长，分色分线宽；含两侧则两侧分别核',''),('白色车位框／角标','m；m²','按真实框／角标逐段累计；车位格数另列',''),('方向／人行／用途地贴','枚','按核定位置逐枚计；正反或组合图案按清单约定',''),('质量分区地贴／色线','枚；m','蓝待检／绿放行／红不合格／黄冻结分别列项',''),('现场放样／基层处理','项；m²','与刷漆和贴标范围互斥，实际范围和计量方式另核','')]
    yy=239; widths=[310,170,850,270];xs=[40,350,520,1370]
    for x,w,t in zip(xs,widths,['工作项','单位','计量方法','提案量 / 批准量']):b+=rect(x,yy,w,52,'#000000')+text(x+15,yy+34,t,22,'#FFFFFF',700)
    for i,(a,u,c,d) in enumerate(qty):
        y=yy+52+i*86
        for x,w,v in zip(xs,widths,[a,u,c,'待核 / 未批准']):b+=rect(x,y,w,86,'#F3F3F3' if i%2==0 else '#FFFFFF','#D0D0D0')+text(x+15,y+49,v,20)
    b+=lines(40,783,['漆线净面积 = Σ（实测线长m × 批准线宽m）－重复覆盖面积m²。地贴覆盖面积另列，不并入漆线量。','采购涂料量按获准产品的有效耗量、道数及核定损耗另算；当前没有数量、单价、总价或采购建议。'],23,38)
    b+=panel(40,877,780,185,'尚未完成｜阻塞实际放样',['有效8F图框与单位、原生完整底图仍待核','实际货梯、工艺顺序、车辆与现场净空待核','真实路线 / 定置坐标 / 成品尺寸 / 工程量未定'])
    b+=panel(850,877,790,185,'下一步｜现场联合核对',['生产：物流与接收容量；品质：状态与放行范围','工程：底图、实测、地坪与安装；安全：适用专项','把核定记录带回，另出定位尺寸图和实际核量清单'])
    pages.append(page(7,'8F 地面物流规划｜核量与待闭合事项','附CSV可编辑核量表；空值表示尚未测量，不表示不需要、不表示数量为零。',b))

    fields=['详图索引','工作项','用途或文字','颜色语义','单位','实际位置','世界X','世界Y','单位换算','线宽_mm','实际长度_m','实际宽_mm','实际高_mm','字高_mm','提案数量','批准数量','净面积_m2','材料规格','测量证据','内容确认','位置确认','安装确认','安全专项确认','状态']
    qrows=[]
    for idx,title,color,unit in [('M01','物流通道边界','黄：通道示例，待批准','m'),('M02','人行通路','白文字；边界待专项核定','m'),('M03','周转车定位框','白','m'),('M04','固定设备角标','白','m'),('M05','线边FIFO位','白','m'),('M06','保持畅通提示','白','枚')]+[(i,t,c,'枚') for i,t,sub,c,fg in labels]:
        row={f:'' for f in fields};row.update({'详图索引':idx,'工作项':title,'用途或文字':title,'颜色语义':color,'单位':unit,'状态':'未勘测 / 草案未放行'});qrows.append(row)
    write_csv('8F_地面放样与核量_待填.csv',fields,qrows)
    params=[dict(parameter=k,actual_value=None,unit=u,evidence=None,reviewer=None,approval=None) for k,u in [('vehicle_type',None),('loaded_vehicle_width','mm'),('loaded_vehicle_length','mm'),('aisle_clear_width','mm'),('line_width','mm'),('turning_envelope',None),('bay_width','mm'),('bay_length','mm'),('sticker_width','mm'),('sticker_height','mm'),('letter_height','mm')]]
    refs=['docs/PROJECT_BRIEF.md','docs/TASTE_ADAPTATION.md','docs/CAD_WORKFLOW.md','data/tasks.json','data/floors.json','outputs/flow_review/research/logistics_analysis.md','outputs/flow_review/02_8F功能泳道.json','outputs/implementation_v2.4/8F_功能分区与相对选址.json',str(ann_path.relative_to(ROOT)),ann['source_png'],'outputs/implementation_v2.4/cad/8F_existing_candidate_partial_metadata.json','inputs/v1/BeePump_Design_Package/03_Templates_SVG/FM-01_地面定置图例.svg','design/v2/implementation_ops_v2.4/FM-01_地面定置图例_V2.4-IMPLEMENTATION-DRAFT.svg']
    manifest=dict(revision=REV,created_on='2026-10-18',floor_scope='8F',status='functional_planning_and_artwork_review',production_release=False,
        source_drawing_sha256=SHA,source_png_sha256=ann['source_png_sha256'],input_hashes_verified=len(inventory['inputs']),
        source_records=[dict(path=p,sha256=hashlib.sha256((ROOT/p).read_bytes()).hexdigest()) for p in refs],
        pages=pages,style_indices=[v[0] for v in labels],style_count_is_not_quantity=True,source_reference_anchors=source_refs,
        actual_points=[],actual_routes=[],actual_points_status='not_surveyed_not_zero_required',actual_dimensions=None,actual_quantities=None,approved_quantities=None,
        parameters=params,assumptions=['主流程待用户核对；老化为条件分支','车辆类型未获确认；没有采用具体宽度','沿用V2.7用户指认的右上客梯，仅用于人员关系','原料仓A锚点为源预览对象人工核对索引，非现场事实'],
        unresolved=['8F图身/3F图签冲突','CAD物理单位与现场两向校核','原生完整底图、缺失实体/字体','货梯身份与入口、工艺与满载车辆','通道、转弯、保持畅通及质量分区的真实边界','现场尺寸、材料、数量和人类批准'])
    dump(OUT/'规划与来源.json',manifest)
    dump(SRC/'revision_metadata.json',dict(revision=REV,status='draft',production_release=False,manifest='交付_8楼/地面物流规划_V2.9/规划与来源.json',actual_points=[],page_unit='display_px',physical_dimensions_mm=None))
    dump(OUT/'FM-01_针对性审查.json',dict(revision=REV,template_code='FM-01',decision='Refine',source_render='reports/implementation_operations_render/v1/FM-01.png',preserve=['白色移动物框及设备角标','蓝待检、绿放行、红不合格','无橙色地面','线宽以批准图确定'],refine=['补黄冻结及用途文字','把图例扩展成物流/人行/返回接口与地贴样式','补实际尺寸、核量空字段及制作放行边界'],scope='只深化FM-01及FL-01/FL-02关联，不声明重新审查全部模板',production_release=False))
    # Keep editable source copies together with the final offline handoff.
    import shutil
    shutil.copy2(source,OUT/'原始底图_只读.png')
    shutil.copytree(SRC,OUT/'可编辑SVG',dirs_exist_ok=True)
    links=''.join(f'<li><a href="可编辑SVG/{html.escape(n)}">{html.escape(n)}</a></li>' for n in pages)
    pictures=''.join(f'<section><img src="预览/{n[:-4]}.png" alt="{html.escape(n[:-4])}"></section>' for n in pages)
    (OUT/'打开地面物流方案.html').write_text('''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>8F 地面物流规划 V2.9</title><style>body{font-family:PingFang SC,Arial,sans-serif;margin:0;background:#eee;color:#000}header,nav{max-width:1400px;margin:20px auto;padding:20px;background:white}h1{font-size:32px}p,li,a{font-size:18px;line-height:1.6}a{color:#000;text-underline-offset:4px}a:focus-visible{outline:3px solid #005EB8}section{margin:24px auto;max-width:1680px}img{width:100%;display:block}ul{columns:2}@media(max-width:750px){ul{columns:1}}@media print{header,nav{display:none}section{margin:0;break-after:page}@page{size:A3 landscape;margin:0}}</style><header><h1>8F 地面物流与地标规划 · V2.9</h1><p>设计评审已成稿；实际定位、尺寸与核量待现场确认。请勿直接用于刷漆放样。图纸身份和单位仍有待核项。</p><p><a href="8F_地面物流与地标规划_评审稿.pdf">打开7页A3评审册</a> · <a href="8F_地面放样与核量_待填.csv">编辑放样与核量表</a> · <a href="规划与来源.json">查看来源与空值台账</a></p></header><nav><strong>可编辑SVG</strong><ul>'''+links+'</ul></nav>'+pictures+'</html>',encoding='utf-8')
    (OUT/'先读说明.md').write_text('''# 8F 地面物流与地标规划 V2.9

这是地面物流关系、刷漆定置和地贴文字的设计评审交付。不是定位施工图。请从“打开地面物流方案.html”或7页A3评审册开始。

## 已有内容

- 物流主线、人员关系、空车返回及质量分流；老化按真实工艺条件启用。
- 原图只读嵌入及A-G来源对象核对索引；延用V2.7右上客梯用户指认。
- M01-M06刷漆/定置详图与S01-S08地贴样式索引。索引数不是安装量。
- 可编辑SVG、材料与放样流程、空白CSV核量表及来源哈希。

## 使用顺序

1. 生产核物流、实际收发接口、工艺及接收容量；品质核质量分区和放行范围。
2. 工程锁定真实8F图框、单位、至少两个不同方向标注及现场尺度；核货梯、满载车辆、门扇和地坪。
3. 安全负责人核疏散、消防、交叉、保持畅通和适用专项边界。
4. 在核定范围内做可移除放样、足尺字样及实车试走；将结果填写CSV并回传。
5. 坐标、尺寸、数量、材料及内容/位置/安装/适用专项记录齐备后，另发定位尺寸图和制作稿，再刷漆贴标。

## 明确空值

真实点位与真实路线数组为空表示未勘测，非零需求；实际毫米尺寸、线宽、通道净宽、地贴字高、工程量、采购量均未确定。所有SVG单位为评审画布px；PDF A3是纸张尺寸，不是1:1地贴或施工比例。不得将框数、箭头数、源对象坐标或图上像素转为实际点数与毫米尺寸。

8F图身与3F图签冲突、CAD单位未核、原生出图和字体依赖仍未闭合；源图局部空白不代表现场空地。原始输入未改；未上传或发布；未生成批准记录。品牌橙不上地面。质量颜色不能充当通行优先或安全批准。异常电池包不并入普通返修支线。
''',encoding='utf-8')
    print(json.dumps(dict(pages=len(pages),style_artworks=len(labels),output=str(OUT),immutable_inputs_verified=len(inventory['inputs'])),ensure_ascii=False))

if __name__=='__main__':main()

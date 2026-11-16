#!/usr/bin/env python3
"""Author the 12 local V2.4 proposals; source templates remain immutable."""
import hashlib
import html
import json
from pathlib import Path
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[3]
DEST = ROOT / 'design/v2/implementation_v2.4'
OUT = ROOT / 'outputs/implementation_v2.4'
FONT = 'Noto Sans CJK SC, Source Han Sans SC, PingFang SC, Microsoft YaHei, sans-serif'
BLACK, ORANGE, WHITE, GRAY = '#000000', '#FF6600', '#FFFFFF', '#3E3A39'
SRC = {t['code']: t for t in json.loads((ROOT/'data/templates.json').read_text()) if t['revision']=='V1.0'}

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def text(x,y,value,size,fill=BLACK,weight=400,anchor='start'):
    return f'<text x="{x}" y="{y}" font-size="{size}" fill="{fill}" font-weight="{weight}" text-anchor="{anchor}">{html.escape(value)}</text>'

def rect(x,y,w,h,fill=WHITE,stroke=None,sw=1):
    attrs=f' fill="{fill}"'+(f' stroke="{stroke}" stroke-width="{sw}"' if stroke else '')
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}"{attrs}/>'

def line(x1,y1,x2,y2,color=GRAY,sw=1):
    return f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" stroke-width="{sw}"/>'

def header(w,h,title,en,title_size,meta=''):
    pad=w*.034
    return [rect(0,0,w,h,BLACK),rect(0,0,w*.01,h,ORANGE),text(pad,h*.47,title,title_size,WHITE,600),text(pad,h*.81,en,title_size*.39,WHITE),text(w-pad,h*.47,meta,title_size*.43,ORANGE,500,'end')]

def footer(w,h,code,revision,info,size):
    pad=w*.034
    return [line(pad,h-size*3,w-pad,h-size*3,GRAY,.5),text(pad,h-size,info,size,GRAY),text(w-pad,h-size,code+' / '+revision,size*.82,GRAY,400,'end')]

def panels(y,items,x=90,gap=90,w=1020,h=660,title_size=72,body_size=51,black=False):
    res=[]
    for i,(title,rows) in enumerate(items):
        xx=x+i*(w+gap)
        res += [rect(xx,y,w,h,BLACK if black else WHITE,GRAY,2),rect(xx,y,12,h,ORANGE),text(xx+50,y+115,title,title_size,WHITE if black else BLACK,600)]
        for j,row in enumerate(rows):
            res.append(text(xx+50,y+230+j*100,row,body_size,WHITE if black else BLACK))
    return res

def brand_entrance():
    r=[rect(0,0,3600,2200,BLACK),rect(90,100,15,610,ORANGE),text(160,310,'BeePump',220,ORANGE,600),text(165,500,'MANUFACTURING',72,WHITE,500),text(165,710,'让制造过程看得见',148,WHITE,600),text(165,840,'入口接待 · 现场观察 · 证据核验',72,WHITE)]
    r += panels(1030,[('先接待',['请先登记来访事项','由接待人员确认陪同','按获准路线开始参观']),('看现场',['在指定观察点停留','不进入运输与作业范围','拍照与接触产品先获许可']),('看证据',['展示获准照片或实物','用受控记录说明控制点','客户资料按授权范围公开'])],black=True)
    r += [text(165,1900,'1F主入口内容提案 / 墙面、观看点和接待位置待现场核对',53,WHITE),text(165,2020,'正式Logo待提供；BeePump仅为字标排版示意；无历史或认证承诺',43,WHITE),text(165,2130,'BE-01 / V2.4-IMPLEMENTATION-DRAFT / 成品尺寸与安装另经批准',33,WHITE)]
    return r

def lobby():
    r=[rect(0,0,3600,2200,WHITE),rect(0,0,3600,850,BLACK),rect(0,0,36,850,ORANGE),text(150,490,'8F',340,ORANGE,600),text(950,330,'锂电充气泵装配',155,WHITE,600),text(960,485,'ELECTRIC PUMP ASSEMBLY',62,WHITE),line(960,585,3420,585,ORANGE,8),text(960,725,'楼层到达识别 / 用途为V1基线提案，图纸与现场待核',50,WHITE)]
    r += panels(970,[('先确认入场',['员工按本岗要求入场','访客须由授权人员陪同','PPE与权限按现场批准要求']),('进入指定区域',['先辨认楼层与目标区域','在导览牌核对获准路线','区域ID及方向待现场定稿']),('保持现场有序',['物品放回批准位置','不占门前、前室与通道','异常报告指定责任角色'])],h=740,title_size=72,body_size=50)
    r += [text(150,1890,'物流到达、员工入场与访客停留须分别复核，不能仅凭墙面文字放行',50),text(150,2000,'电梯厅墙面模块 / 不改现有门、梯与专项设施 / 配套WF-01、WF-03按实际进路定向',42),text(150,2130,'BE-02 / V2.4-IMPLEMENTATION-DRAFT / 楼层、内容、墙面与安装均待签核',33,GRAY)]
    return r

FLOORS=[('9F','喷漆专项接口','PAINTING / SPECIALIST INTERFACE'),('8F','锂电充气泵装配','ELECTRIC PUMP ASSEMBLY'),('7F','用途待确认','FUNCTION PENDING'),('6F','用途待确认','FUNCTION PENDING'),('5F','半成品仓 / 来料检','COMPONENT WAREHOUSE / IQC'),('4F','手打气筒装配','MANUAL PUMP ASSEMBLY'),('3F','成品仓','FINISHED GOODS WAREHOUSE'),('2F','注塑车间','INJECTION MOLDING'),('1F','金工 / 出货 / 主入口','METALWORKING / SHIPPING / ENTRANCE')]

def directory(floor):
    r=header(900,180,'楼层导览','FLOOR DIRECTORY',50,floor+' 本层提案')
    for i,(f,cn,en) in enumerate(FLOORS):
        y=215+i*111
        r += [rect(32,y,836,105,WHITE,ORANGE if f==floor else GRAY,3 if f==floor else .5),text(60,y+60,f,52,ORANGE if f==floor else BLACK,600),text(205,y+42,cn,32,BLACK,600),text(205,y+78,en,13,GRAY),text(835,y+42,'待核',16,GRAY,400,'end')]
        if f==floor:
            r.append(text(835,y+80,'本层',17,ORANGE,600,'end'))
    r += [text(43,1265,'楼层用途依据V1；6F/7F用途未取得，不赋予新功能。',22),text(43,1310,'本牌用于目的地检索；实际路线、进路和方向另核。',22),text(43,1355,'楼层号、区域号、参观节点号分别管理。',22),text(43,1400,'身份/权限与现场用途确认后，替换全部“待核”。',20,GRAY)]
    r+=footer(900,1500,'WF-01','V2.4-'+floor+'-DRAFT','名义模块900×1500mm；非现场尺寸',14)
    return r

def area(floor):
    cn,en=('金工生产区','METALWORKING') if floor=='1F' else ('锂电泵装配','ELECTRIC PUMP ASSEMBLY')
    r=[rect(0,0,1200,400,BLACK),rect(0,0,14,400,ORANGE),line(270,40,270,350,ORANGE,3),text(140,75,'楼层 / FLOOR',19,WHITE,400,'middle'),text(140,215,floor,108,ORANGE,600,'middle'),text(140,297,'区域ID待确认',20,WHITE,400,'middle'),text(330,169,cn,80,WHITE,600),text(335,228,en,26,WHITE),line(335,263,1150,263,ORANGE,3),text(335,319,'名称为基线提案；区域边界与安装面待核',22,WHITE),text(42,378,'WF-02 / V2.4-'+floor+'-DRAFT · 无实际指向 · 名义模块1200×400mm',13,WHITE)]
    return r

def eq_id():
    r=header(300,42,'设备身份牌','EQUIPMENT ID',14,'EQ-01')
    r += [text(11,62,'永久资产ID',7,GRAY),text(11,84,'待登记',15,BLACK,600),rect(240,56,47,47,WHITE,GRAY,.7),text(263.5,76,'档案码区',5,GRAY,400,'middle'),text(263.5,88,'链接待批准',4,GRAY,400,'middle')]
    rows=[('设备名称 / 型号','按批准资产台账待填'),('现场位置码','按现场位置台账待填'),('责任角色 / 接手','工程资产 / 生产使用，人员待定'),('维护文件 / 版次','按受控档案待填；状态另挂EQ-03')]
    for i,(a,b) in enumerate(rows):
        y=116+i*17
        r += [text(11,y,a,5.3,GRAY),text(103,y,b,5.1),line(11,y+5,287,y+5,GRAY,.25)]
    r += [text(11,183,'搬迁更新位置，不改永久ID；不得遮盖原厂铭牌、安全警告或操作件。',4.05,GRAY),text(11,194,'EQ-01 / V2.4-IMPLEMENTATION-DRAFT · 名义300×200mm · 印前字段待核',3.4,GRAY)]
    return r

def eq_state():
    r=[rect(0,0,100,70,WHITE),rect(0,0,100,20,BLACK),rect(0,0,1,20,ORANGE),text(5,8,'设备当前状态',5.2,WHITE,600),text(5,16,'待核实际状态',4.3,WHITE)]
    for i,(a,b) in enumerate([('资产ID','待填'),('状态开始时间','待填'),('接手人 / 下一步','待填')]):
        y=30+i*10
        r += [text(5,y,a,3.05,GRAY),text(39,y,b,3.3),line(5,y+3,95,y+3,GRAY,.18)]
    r += [text(5,59,'可选词：运行 / 待料 / 故障 / 停用',2.8),text(5,65,'恢复记录与权限待核；卡片不替代锁定或检修许可。',2.1,GRAY),text(5,69,'EQ-03 / V2.4-IMPLEMENTATION-DRAFT / 名义100×70mm',1.65,GRAY)]
    return r

def sop():
    r=header(420,43,'标准作业指导书','STANDARD OPERATING PROCEDURE',12,'SW-01 受控框架')
    r += [text(14,57,'文件ID / 版次：待批准',5.8,BLACK,600),text(217,57,'产品 / 工位：待核',5.8),text(14,72,'生效批次或日期：待批准',5.2),text(217,72,'内容批准 / 现场验证：待记录',5.2)]
    for i in range(3):
        x=14+i*133
        r += [rect(x,86,124,55,WHITE,GRAY,.6),text(x+62,109,'受控本工位照片待提供',4.9,GRAY,400,'middle'),text(x+62,125,'仅为版面位置，不代替现场作业',3.7,GRAY,400,'middle'),text(x,159,f'步骤 {i+1:02d} / 动作：待批准',6.1,BLACK,600),text(x,176,'关键点 / 判定：待批准',5.2),text(x,193,'原因 / 风险：待确认',5.2,GRAY)]
    r += [line(14,207,406,207,ORANGE,.8),text(14,223,'受控参数、检验口径、工装 / 量具及文件引用：待批准',5.8,BLACK,600),text(14,241,'异常：按本岗批准流程暂停、保留追溯并呼叫指定角色；接手与恢复记录待核。',4.7),text(14,258,'扫码仅补充完整文件；离线仍能读到本岗关键步骤。换型换版须撤回旧版。',4.7),text(14,276,'技术编制 / 品质判定 / 生产验证 / 工程条件：具体责任人与批准证据待登记。',4.2,GRAY),text(14,290,'SW-01 / V2.4-IMPLEMENTATION-DRAFT · 名义A3横版 · 未填受控内容前不得作为完整SOP上岗',3.7,GRAY)]
    return r

def pack():
    r=header(420,43,'换型与包装核对','CHANGEOVER & PACK VERIFICATION',12,'SW-02')
    r += [text(14,57,'产品 / 工单 / 生效批次：待填',5.6),text(219,57,'包装规范 / 版次：待批准',5.6),text(14,72,'换型原因 / 原版本 / 新版本：待填',5.2),text(219,72,'批准样例ID / 现场核对：待登记',5.2)]
    items=[('01 清线','旧物料、包装、标签及样品撤离并核清','程序 / 参数切换按批准适用范围核对'),('02 换版','物料、SOP、工装与测试版本对应当前工单','新旧版本、生效批次及领退料记录相互一致'),('03 首件','授权人员依据受控包规核对实物及标签','首件证据与批量许可待确认，不先做后补')]
    for i,(a,b,c) in enumerate(items):
        y=87+i*42
        r += [text(17,y+21,a,9,ORANGE,600),text(109,y+14,b,5.2),text(109,y+30,c,5.2),line(14,y+37,406,y+37,GRAY,.3)]
    for i,a in enumerate(['彩盒','说明书','配件','标签','市场版本']):
        x=14+i*78.4
        r += [rect(x,222,78.4,32,WHITE,GRAY,.3),text(x+39.2,236,a,6.3,BLACK,600,'middle'),text(x+39.2,249,'实物 / 料号 / 版次待核',3.4,GRAY,400,'middle')]
    r += [text(14,268,'执行 / 核对 / 批量许可 / 时间 / 记录ID：按批准权限登记；不合成签名。',4.5),text(14,279,'客户专用包规与订单信息须脱敏；异常组合退出批量包装并保留追溯。',4.3,GRAY),text(14,291,'SW-02 / V2.4-IMPLEMENTATION-DRAFT · 名义A3横版 · 适用项目与权限待核',3.6,GRAY)]
    return r

def sample_queue():
    r=header(1200,125,'试模样件验证队列','SAMPLE VERIFICATION QUEUE',44,'位置 / 责任区域待核')
    cols=[('样件 / 版本',160),('首次提交',130),('齐套受理',130),('接手 / 承诺',155),('阻塞 / 下一步',215),('报告 / 反馈',180),('技术确认',155)]
    x=36
    for title,w in cols:
        r += [rect(x,172,w,65,WHITE,GRAY,.5),text(x+12,215,title,23,BLACK,600)]
        for row in range(3):
            y=237+row*92
            r += [rect(x,y,w,92,WHITE,GRAY,.5),text(x+12,y+49,'待填',20,GRAY)]
        x+=w
    r += [text(38,559,'检验口径 / 文件ID / 版次 / 适用样件：待品质与技术确认',25,BLACK,600),text(38,612,'资料齐套条件：样件ID、版本、提交目的、验证项目及适用要求均可追溯',23),text(38,662,'首次提交与齐套受理分别记录；承诺、阻塞原因和接手角色按事件更新',23),text(38,712,'报告出具不等于技术确认关闭；结论、整改接手和复验要求各有记录',23),text(38,765,'技术发起 / 生产制样 / 品质验证 / 技术确认 / 工程整改支持：具体人员待定',21,GRAY),text(38,822,'表格行仅为版面容量，不代表现场队列上限、样件数量或批准时效。',19,GRAY)]
    r+=footer(1200,900,'QC-05','V2.4-IMPLEMENTATION-DRAFT','名义1200×900mm；无默认2F位置',13)
    return r

def capability():
    r=header(3600,260,'从部件到产品：用证据说明控制','FROM COMPONENTS TO PRODUCTS',98,'BE-04')
    items=[('金工','图样与工序口径','批准图样 / 检验记录'),('注塑','材料与版本追溯','料批 / 验证记录'),('物料管理','身份与放行分离','物料ID / 放行依据'),('装配','手动与锂电并行','受控SOP / 工单追溯'),('测试','依据批准项目判定','受控项目 / 判定记录'),('交付','齐套与交接分开','包装核对 / 交接记录')]
    for i,(cn,control,evidence) in enumerate(items):
        x=95+i*575
        r += [text(x,415,f'{i+1:02d}',76,ORANGE,500),text(x,560,cn,65,BLACK,600),rect(x,645,530,415,WHITE,GRAY,2),text(x+265,810,'真实照片 / 实物位置',36,GRAY,400,'middle'),text(x+265,895,'内容与展陈固定待批准',29,GRAY,400,'middle'),text(x,1160,control,39,BLACK,600),text(x,1250,evidence,32),text(x,1340,'证据ID / 版次 / 权限待确认',26,GRAY)]
    r += [line(95,1450,3505,1450,ORANGE,5),text(95,1545,'展示的是获准控制点与真实证据；不公布未经验证的产能、客户、认证或检测承诺。',46,BLACK,600),text(95,1630,'内容栏目为展陈排序；不推导物流工序、楼层顺序或访客进入权限。',41),text(95,1710,'BE-04 / V2.4-IMPLEMENTATION-DRAFT · 名义3600×1800mm · 照片、实物、表面及固定方案待批准',29,GRAY)]
    return r

ENTRIES=[
 ('BE-01',None,'入口接待与可见制造文案',brand_entrance,['保留品牌入口和可见制造目标；删除未获证实的SINCE 1994','字标明确为排版示意，正式Logo与主文案待批准','补齐接待、指定观察和证据核验的三层实际内容提案'],['品牌与入口识别','来访下一步','陪同和授权边界']),
 ('BE-02','8F','楼层到达识别及入场/6S文字区',lobby,['保留原电梯厅楼层到达识别，不重命名模板','移除未经确认SMT导向，装配用途明确为V1基线','增加入场、导览、秩序和权限说明，不改固定前室或安全设施'],['楼层与用途','入场与目的区域','秩序及异常报告']),
 ('WF-01','1F','1F本层高亮导览',lambda:directory('1F'),['保留1F至9F楼层检索和6F/7F未知用途','本层提案改为1F，所有用途注明待核','不画未经核实指向，不以参观节点代替楼层'],['楼层检索','本层突出','路线与命名确认']),
 ('WF-01','8F','8F本层高亮导览',lambda:directory('8F'),['保留1F至9F楼层检索和6F/7F未知用途','本层提案保持8F，所有用途注明待核','不画未经核实指向，不以参观节点代替楼层'],['楼层检索','本层突出','路线与命名确认']),
 ('WF-02','1F','金工生产区基线提案',lambda:area('1F'),['独立表达楼层与区域ID，区域ID待确认','名称为1F金工基线提案，不能替代原图功能确认','取消未核A或8F-A实例，无实际箭头，双面进路分别定稿'],['楼层与区域功能','区域身份待核','名称边界和安装面']),
 ('WF-02','8F','锂电泵装配基线提案',lambda:area('8F'),['独立表达楼层与区域ID，区域ID待确认','名称为8F锂电装配基线提案，不能替代原图功能确认','取消未核A或8F-A实例，无实际箭头，双面进路分别定稿'],['楼层与区域功能','区域身份待核','名称边界和安装面']),
 ('EQ-01',None,'永久身份/位置/档案分离',eq_id,['删除示例EQ-000123、注塑机和2F-IM-05，不编造资产','永久资产ID与现场位置分别记录，档案码仅留待批准位置','设备状态另挂EQ-03，保留原厂铭牌和操作/检修边界'],['永久资产身份','现场位置与档案','动态状态另挂']),
 ('EQ-03',None,'当前状态待核换卡框架',eq_state,['移除默认运行状态，当前状态待核；原设备状态语义保存在溯源','保留资产关联、开始时间、接手与下一步','增加恢复证据/权限提示，不替代检修许可或锁定程序'],['当前状态','接手与下一步','恢复证据与权限']),
 ('SW-01',None,'受控SOP文件框',sop,['保留步骤照片、动作、关键点、原因与异常动作','受控ID、版次、产品、工位、生效和批准字段独立待核','关键作业不只依靠扫码；三个步骤仅为布局，不表示工艺步骤数'],['产品工位和受控版次','步骤关键点与判定','异常/换版与完整文件']),
 ('SW-02',None,'换型/包规/首件/许可闭环',pack,['保留清线、换版、首件与五类包装组合核对','产品、工单、生效批次、批准样例ID及记录字段待填','现场核对权限不伪签，不默认所有产品均有测试程序或特定包规'],['换型执行与当前版','首件与批量许可','组合一致/保密边界']),
 ('QC-05',None,'样件队列及受控验证口径',sample_queue,['保留试模样件首次提交与齐套受理两种时间，不替换成普通检验牌','加入受控检验口径、版本、报告及技术反馈/整改闭环','移除未核2F地点、示例日期和默认时效，行数不是批准容量'],['样件身份与齐套受理','接手/承诺/阻塞','报告与技术确认']),
 ('BE-04',None,'真实控制点与客户证据展陈',capability,['保留六个制造能力栏目和手动/锂电并行含义','补充每栏可核验控制点和证据类型，不虚构能力完成情况','照片/实物、证据ID/版本和授权待核，栏目不表示物流顺序'],['制造控制点','真实证据','展陈与保密授权']),
]

def main():
    DEST.mkdir(parents=True,exist_ok=True)
    OUT.mkdir(parents=True,exist_ok=True)
    manifest=[]
    audits=[]
    for code,floor,variant,build,reasons,hierarchy in ENTRIES:
        src=SRC[code]
        rev=('V2.4-'+floor+'-DRAFT') if code in ['WF-01','WF-02'] else 'V2.4-IMPLEMENTATION-DRAFT'
        ident=code+('-'+floor if code in ['WF-01','WF-02'] else '')
        filename=f'{ident}_{src["name"]}_{rev}'
        p=DEST/(filename+'.svg')
        side=DEST/(filename+'.sidecar.json')
        texts=[''.join(n.itertext()) for n in ET.parse(ROOT/src['path']).getroot().iter() if n.tag.endswith('}text')]
        meta={'template_code':code,'template_name':src['name'],'revision':rev,'variant_id':ident,'content_variant':variant,'floor_proposal':floor,'status':'implementation_review_proposal','source_template':{'path':src['path'],'sha256':sha(ROOT/src['path'])},'original_text_preserved':texts,'change_reasons':reasons,'nominal_dimensions_mm':[src['w'],src['h']],'viewbox_contract':'1 SVG user unit = 1 nominal mm','nominal_font_size_note':'font-size is nominal em in template units, not printed glyph height or site readability approval','actual_point_id':None,'actual_floor_id':None,'actual_area_id':None,'actual_direction_degrees':None,'actual_installation_height_mm':None,'actual_installed_quantity':None,'actual_face_count':None,'approved_capacity':None,'production_release':False,'approvals':{'content':None,'location':None,'operation':None,'installation':None,'safety_when_applicable':None},'orange_floor_markings':False,'safety_graphics_changed':False,'font_stack':FONT,'font_files_distributed':False,'template_slots_are_not_site_counts':True,'read_update_hierarchy':hierarchy,'render_review':{'status':'pending_digital_render_review','physical_1_to_1_sample_tested':False,'site_reading_distance_approved':False,'installation_approved':False},'path':str(p.relative_to(ROOT)),'sidecar_path':str(side.relative_to(ROOT))}
        body='\n'.join(build())
        svg=f'<?xml version="1.0" encoding="UTF-8"?>\n<svg xmlns="http://www.w3.org/2000/svg" width="{src["w"]}mm" height="{src["h"]}mm" viewBox="0 0 {src["w"]} {src["h"]}" role="img" aria-label="{html.escape(src["name"]+" / "+variant+" / 草案")}">\n<title>{html.escape(src["name"]+" / "+rev)}</title>\n<desc>可编辑实施评审草案。名义模板尺寸，不构成现场施工放行。源文件和原始文字在侧车保存；实际位置、数量、方向、安装及批准均未取得。</desc>\n<metadata>{html.escape(json.dumps({k:meta[k] for k in ["template_code","revision","variant_id","floor_proposal","nominal_dimensions_mm","actual_point_id","production_release","source_template"]},ensure_ascii=False))}</metadata>\n<g font-family="{FONT}">\n{body}\n</g>\n</svg>\n'
        p.write_text(svg,encoding='utf-8')
        meta['svg_sha256']=sha(p)
        side.write_text(json.dumps(meta,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        item={'code':code,'name':src['name'],'revision':rev,'variant_id':ident,'content_variant':variant,'floor_proposal':floor,'w':src['w'],'h':src['h'],'physical_size_mm':[src['w'],src['h']],'path':str(p.relative_to(ROOT)),'sidecar_path':str(side.relative_to(ROOT)),'source_path':src['path'],'source_sha256':sha(ROOT/src['path']),'decision':'Refine','drawing_status':'template_only','approval_status':'not_for_production','actual_point_id':None,'production_release':False,'change_reasons':reasons,'original_text_preserved_in_metadata':texts,'source_render_png':'reports/implementation_template_render/v1/'+code+'.png','render_png':'reports/implementation_template_render/'+ident+'.png','render_review_status':'pending_digital_render_review','font_sizes_are_nominal_em_mm':True,'printed_font_and_installation_height':'not verified; 1:1/site review required','svg_sha256':sha(p),'sidecar_sha256':sha(side),'render_qa_path':'reports/implementation_template_render/render_qa.json'}
        manifest.append(item)
        audits += [f'## {ident} · {src["name"]}',f'保留原模板业务含义，名义尺寸{src["w"]}×{src["h"]}mm。版本：{rev}。内容变体：{variant}。',f'源图：`{src["path"]}`；SHA-256 `{item["source_sha256"]}`。',*['- '+r for r in reasons],f'原版像素：`{item["source_render_png"]}`；新稿：`{item["render_png"]}`。',f'读面：{" / ".join(hierarchy)}。字段、观看距离、实际点位、朝向、安装、材料与各批准记录待核。','']
    (OUT/'template_manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    head='# 12款实施评审模板审查 / V2.4-IMPLEMENTATION-DRAFT\n\n2026-10-07。先实际查看10种V1像素，再定向深化为12个变体；原文件和原TEXT保留。BE-02仍是电梯厅到达识别，QC-05仍是样件验证队列，附加文字不替换其业务含义。\n\n本批采用项目Taste适用子集：主次、对齐、字距、留白、状态分工和更新结构。无动画、纹理、网页假数据或虚构日期。原BE-01历史词SINCE 1994无可靠证据，移入侧车溯源、不印入新稿。原WF-02的8F-A/A未经确认，替换为明确待核字段。\n\n原版数字检查无出界；BE-01品牌/英文与WF-02楼层/A有墨迹边界相交候选，实际原PNG已查看。新稿独立分层，不用横向字形压缩。\n\n十二款均是版面变体，不表示十二个安装点；同一实物双面另登记，实际实物数量为空。质量/安全图形未更改；无橙色地面。未填字段或未经内容/现场/安装签核不得标为施工放行。\n\n'
    (OUT/'template_audit.md').write_text(head+'\n'.join(audits),encoding='utf-8')
    print(json.dumps({'templates':len(manifest),'manifest':str((OUT/'template_manifest.json').relative_to(ROOT))},ensure_ascii=False))

if __name__=='__main__':
    main()

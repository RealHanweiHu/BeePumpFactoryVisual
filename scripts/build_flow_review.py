#!/usr/bin/env python3
"""Author local functional flow diagrams and V2.3 review documents. No site geometry."""
from pathlib import Path
import base64, csv, hashlib, html, json, textwrap

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'outputs/flow_review'
REV = 'V2.3-FLOW-DRAFT'
DATE = '2026-10-05'
OUT.mkdir(parents=True, exist_ok=True)

def read(path): return json.loads((ROOT/path).read_text())
def write_json(path, data):
    p=ROOT/path; p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
def esc(s): return html.escape(str(s))
def csv_file(name, rows, fields):
    with (OUT/name).open('w',newline='',encoding='utf-8-sig') as f:
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader()
        for row in rows:
            w.writerow({k:'待核' if row.get(k) is None else '；'.join(row[k]) if isinstance(row[k],list) else row[k] for k in fields})
def data_url(path):
    p=ROOT/path; mime='image/svg+xml' if p.suffix=='.svg' else 'image/png'
    return 'data:'+mime+';base64,'+base64.b64encode(p.read_bytes()).decode()

logistics=read('outputs/flow_review/research/logistics_analysis.json')
people=read('outputs/flow_review/research/people_analysis.json')
SOURCE_SHA=logistics['source_drawing_sha256']

class Diagram:
    def __init__(self,title,subtitle,height=920):
        self.title=title; self.height=height
        self.parts=[f'<svg xmlns="http://www.w3.org/2000/svg" width="1600" height="{height}" viewBox="0 0 1600 {height}" role="img" aria-label="{esc(title)}">',
            '<defs><marker id="arrow" markerWidth="10" markerHeight="10" refX="8" refY="4" orient="auto"><path d="M0 0 L8 4 L0 8" fill="#000"/></marker></defs>',
            f'<metadata>{esc(json.dumps({"revision":REV,"status":"functional_concept","coordinate_system":"page_px_only","position_world":None,"actual_quantities":None,"production_release":False,"source_drawing_sha256":SOURCE_SHA},ensure_ascii=False))}</metadata>',
            f'<rect width="1600" height="{height}" fill="white"/>',
            '<rect x="0" y="0" width="1600" height="122" fill="#000"/>',
            '<rect x="0" y="122" width="1600" height="8" fill="#FF6600"/>']
        self.text(48,53,title,34,'#fff',True)
        self.text(48,99,subtitle,22,'#fff')
    def text(self,x,y,s,size=24,color='#000',bold=False):
        self.parts.append(f'<text x="{x}" y="{y}" style="font-family:PingFang SC,Arial,sans-serif;font-size:{size}px;fill:{color};font-weight:{700 if bold else 400}">{esc(s)}</text>')
    def box(self,x,y,w,h,title,lines=(),kind='normal'):
        fill='#F4F3F1' if kind=='soft' else '#fff'
        dash=' stroke-dasharray="10 6"' if kind=='conditional' else ''
        self.parts.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{fill}" stroke="#000" stroke-width="2"{dash}/>')
        self.text(x+16,y+37,title,27,'#000',True)
        for i,s in enumerate(lines): self.text(x+16,y+75+i*31,s,22)
    def line(self,points,dashed=False,label=None,lx=None,ly=None):
        pts=' '.join(f'{x},{y}' for x,y in points)
        dash=' stroke-dasharray="10 6"' if dashed else ''
        self.parts.append(f'<polyline points="{pts}" fill="none" stroke="#000" stroke-width="3"{dash} marker-end="url(#arrow)"/>')
        if label: self.text(lx,ly,label,21)
    def footer(self,notes):
        self.parts.append(f'<line x1="40" y1="{self.height-102}" x2="1560" y2="{self.height-102}" stroke="#000"/>')
        for i,s in enumerate(notes):self.text(48,self.height-69+i*31,s,21)
    def save(self,name):
        self.parts.append('</svg>'); path=OUT/(name+'.svg');path.write_text('\n'.join(self.parts))
        write_json(f'outputs/flow_review/{name}.json',{'revision':REV,'status':'functional_concept','description':self.title,'layout_unit':'px','position_world':None,'actual_quantity':None,'source_drawing_sha256':SOURCE_SHA,'production_release':False,'sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
        return 'outputs/flow_review/'+name+'.svg'

diagrams=[]
d=Diagram('全厂物流接口｜按工单选路','楼层文字来自V1基线；线条表示业务关系，箭头不代表现场方向',1020)
d.box(50,190,290,148,'来料收货 / IQC',('登记批与样关联','放行后按BOM分流'))
d.box(430,190,290,148,'1F 金工 / 2F 注塑',('上道检验与放行','按工单选择下道'))
d.box(850,190,290,148,'5F 半成品仓',('适用时入仓 R-STOCK','固定库位 + 批次卡'))
d.box(1250,190,300,148,'4F / 8F 装配',('对应实际BOM / 工艺','直送条件 R-DIRECT'))
d.line([(340,263),(430,263)],True)
d.text(345,245,'仅需加工',20)
d.line([(720,263),(850,263)],label='入仓',lx=752,ly=248)
d.line([(1140,263),(1250,263)],label='配套',lx=1171,ly=248)
d.line([(580,190),(580,158),(1390,158),(1390,190)],True,'允许直送时',930,151)
d.box(430,410,290,148,'9F 喷漆（条件）',('仅适用路线卡启用','专项转运先确认'),kind='conditional')
d.line([(575,338),(575,410)],True)
d.line([(720,485),(796,485),(796,365),(980,365),(980,338)],True,'完成后按工单返回',810,468)
d.line([(720,518),(1190,518),(1190,365),(1400,365),(1400,338)],True)
d.box(50,410,290,148,'外采成品电池包',('专用暂存 / 发料待核','不以电子仓替代'))
d.line([(195,410),(195,373),(1210,373),(1210,309),(1250,309)],True,'仅对应获准工单',368,393)
d.box(1250,625,300,148,'适用测试 / 包装',('老化仅工艺适用时','检验 / 包装分别核对'))
d.line([(1400,338),(1558,338),(1558,585),(1400,585),(1400,625)])
d.box(850,625,290,148,'3F 成品仓',('成品条件与入仓收讫','订单 / 库位 / 批次'))
d.line([(1250,699),(1140,699)])
d.box(430,625,290,148,'1F 出货（基线）',('客户 / 包装 / 箱件复核','装运接口与人员分开'))
d.line([(850,699),(720,699)])
d.box(50,625,290,148,'空容器 / 返修 / 废料',('按分类支线交接','不占正常通道'),kind='soft')
d.text(50,818,'放行外购物料亦可按BOM直接到储位或供料点；金工/注塑仅在工艺适用时进入。',24)
d.text(50,858,'6F / 7F：功能未知。实际储存、包装、运输设施与服务楼层均待核。',24)
d.footer(['实线：一般业务关系；虚线：条件路线。接口编号L01–L14是分析记录，不是实际安装点或标牌数量。','普通返修、冻结与电池安全异常分别受控；专项异常不并入普通返修/废料路线。'])
diagrams.append(d.save('01_全厂物流功能拓扑'))

d=Diagram('8F试点｜补料、作业、上岗与观摩关系','功能泳道示意；非建筑平面，不对应8F-A至H或真实电梯/门/柱',1080)
xs=[50,310,570,830,1090,1350]; w=200
labels=[('接料',('核批次 / 版本','发收双方准备')),('线边供料',('固定地址不变','状态卡随对象')),('装配',('有效SOP','工单 / 批次')),('适用测试',('真实方法 / 结果','老化仅适用时')),('包装核对',('附件 / 标签版本','防混订单')),('成品交接',('放行及收讫','接3F基线'))]
for x,(title,lines) in zip(xs,labels):d.box(x,190,w,153,title,lines)
for x in xs[:-1]:d.line([(x+w,268),(x+260,268)])
d.text(50,164,'材料流（L06–L10）：每一段先核接收端，再搬运',23,'#000',True)
d.box(50,430,460,138,'空容器 / 退料',('分类清点、回收与重新供料','与正向补料分别登记'),kind='soft')
d.box(570,430,460,138,'一般不良 / 冻结',('品质处置指令 → 获准返修 → 复验','未放行不回正常可用队列'),kind='soft')
d.box(1090,430,460,138,'疑似安全异常（专项）',('停止普通流转；授权人员接手','按现场批准专项流程'),kind='conditional')
d.line([(409,343),(409,430)],True)
d.line([(930,343),(930,430)],True)
d.text(50,634,'员工：获准进入 → 当班确认 → 人行路径 → 工位SOP。更衣、风淋、EPA仅实际适用时。',24,'#000',True)
for x,title,lines in [(50,'人员到达',('与货物等待分别评审',)),(440,'班组管理面',('站位及更新退出通行',)),(830,'员工人行路径',('按自然路径核可见性',)),(1220,'对应工位',('投料与员工领料分开',))]:
    d.box(x,665,330,112,title,lines)
for x in [50,440,830]:d.line([(x+330,721),(x+390,721)],True)
d.text(50,830,'访客：接待 / 入场说明 → 获准独立停留面 → 退出；不借员工通路默认穿线。',24,'#000',True)
d.box(50,855,1500,105,'交叉核查：接料口 / 线边补料 / 测试返修 / 包装待运 / 日会站位 / 观摩停留',('优先空间分离；保护、视线、等候面与接手可执行后，才评审有明确起止条件的错峰。',),kind='soft')
d.footer(['图纸已有“原料仓 / 电子仓 / PCBA / 老化房”等字样仅作核查线索，不证明功能、流程或授权已确定。','实际线路、宽度、容器量、读面位置及安装高度待现场确认；品牌橙色仅在牌面，不作地面标线。'])
diagrams.append(d.save('02_8F功能泳道'))

d=Diagram('共享垂直运输｜先确认，再发运','不指定某部EVTR为货梯；信息排队与实物等候分别管理',920)
for x,title,lines in [(50,'任务请求',('工单 / 批次 / 状态','容器 / 数量 / 单位','目的接口 / 接手人')),(440,'发运门槛',('品质及工艺放行','接收准备 + 可用位置','设施与窗口有效')),(830,'搬运与到达',('发 / 到 / 收讫分记','变更需重新协调','无记录不自动插队')),(1220,'接收与差异',('核对象 / 数量 / 状态','收讫≠品质放行','差异保持批次追溯'))]:d.box(x,230,330,202,title,lines)
for x in [50,440,830]:d.line([(x+330,330),(x+390,330)])
d.box(50,550,700,195,'门槛未满足',('货物留在源端获准待运位；请求在信息队列','没有核定等候位：不把前室或门前作为缓存','满位 / 失约 / 设施停用：通知接手人并重新排程'),kind='soft')
d.box(830,550,720,195,'窗口成立的条件',('实际装卸、门动作、运行和交接占用均计入','顺路合载及回程空器具先核相容性和接收能力','不同人员侧与物流侧共同确认暂停、恢复与接手'),kind='soft')
d.line([(605,432),(605,550)],True)
d.line([(985,432),(985,550)],True)
d.footer(['优先原因：真实欠料风险、出货约束、任务准备与可用窗口。所有实际时段、容量、设备ID与载荷条件均待核。','消防/疏散/救援开口、门扇、配电与消防设备前不设默认等候；设施权限由工程与安全确认。'])
diagrams.append(d.save('03_共享运输交接逻辑'))

d=Diagram('回流规则｜分类、授权、复核','正向补料和反向回收分别登记；示意线不表示现场行进方向',920)
rows=[(190,'空容器','清点 / 状态检查','适用清洁与包装条件','重新供料','WH-03 / WH-05'),(350,'冻结 / 普通不良','品质判定及处置指令','获准返修 / 复验','仅新放行范围回流','QC-03 / QC-04'),(510,'批准报废 / 废料','有真实决定记录','分类收集与责任交接','受控移交','L14接口'),(670,'疑似安全异常','停止普通流转','授权专业人员接手','批准专项流程','不默认送普通维修')]
for y,a,b,c,e,f in rows:
    for x,w,title in [(50,280,a),(390,330,b),(780,370,c),(1210,340,e)]:d.box(x,y,w,110,title,(),kind='conditional' if y==670 else 'normal')
    for x1,x2 in [(330,390),(720,780),(1150,1210)]:d.line([(x1,y+55),(x2,y+55)],y==670)
    d.text(65,y+90,f,21)
d.footer(['样件、混批、分批与退料均保持母批/子批、状态和数量关联；质量色不承担交通优先权。','本图不制定电池搬运、灭火、隔离或喷漆工艺操作；相关动作沿用现场批准专项文件。'])
diagrams.append(d.save('04_分类回流逻辑'))

adjacency=[
 ('AD01','收货与人员到达','须分离','在既有获准空间选各自交接面；核自然行走路径、装卸活动与视线。'),
 ('AD02','人员候梯与货物待运','须分离','分别核等待与推出接手面；共享条件有控制、视线及可执行窗口。'),
 ('AD03','收料与线边','受控接口','核定容器、可接收量和接手，避免操作员跨搬运轨迹领料。'),
 ('AD04','库位地址与批次状态','建议邻接','固定地址、随对象状态分开；接手者在停运后一次核清。'),
 ('AD05','装配与测试','工艺条件邻接','仅真实工艺需要时连接；测试授权、待测/已测对象明确。'),
 ('AD06','普通返修与复验','受控接口','返修后回指定复验；不得自行恢复可用或直接进包装。'),
 ('AD07','专项异常与普通回流','须分离','不混入普通返修/废料，由已批准专项流程接手。'),
 ('AD08','包装核对与成品接走','受控接口','包装操作面和物流接走面分别评审，待运量有核定上限。'),
 ('AD09','日会站位与通行','须分离','完整站位退出通行；墙面组合效果不能证明站位成立。'),
 ('AD10','看板读面与更新面','建议邻接','固定标题远读、可换字段近更新；更新无需跨物流/运动设备。'),
 ('AD11','访客停留与运输作业','须分离','先选独立停留，必要时远观或展示替代穿线。'),
 ('AD12','工位SOP与操作视线','受控接口','按真实操作姿态1:1核阅读、换页、照明、防护及撤旧。')]
write_json('outputs/flow_review/adjacency_rules.json',[dict(id=a,relation=b,proposal=c,review_rule=e,position_world=None,approved=False) for a,b,c,e in adjacency])
csv_file('邻接与分离建议.csv',read('outputs/flow_review/adjacency_rules.json'),['id','relation','proposal','review_rule','position_world','approved'])
csv_file('物流接口台账.csv',logistics['interfaces'],['id','name','from','to','route_condition','release_prerequisites','update_fields','unknown_site_facts','owner_roles','template_codes','unresolved'])
csv_file('人员功能路线.csv',people['routes'],['id','name','sequence','design_rule','authorization_gate','handoff','owner_roles','template_codes','actual_route_id','position_world','approved_operating_window'])
csv_file('交叉点核查台账.csv',people['crossings'],['id','name','risk','layout_first','operating_rule','verification','owner_roles','template_codes','position_world','acceptance_status'])

sign_rules=[
 ('C01','到层导览','WF-01 / WF-03','进入分岔前读目的地，转向后能确认去向','实际方向和区域确认后制作；导览读面与货物推出/扫码分开','路线或授权变化由行政/生产复核'),
 ('C02/C03','区域吊牌与柱牌','WF-02 / WF-04','沿真实主要进路看区域；柱号作为稳定定位','从两个实际接近方向核遮挡；柱号不随批次或客户变化','生产/工程核固定面、牌面朝向与安装'),
 ('C04/C05','当班与SQDCP管理墙','PM-01 / PM-02 / PM-03','当班任务、异常接手；指标周期、单位和行动责任','日会全体站位与更新动作退出通行；无数据待填不填0','当班事件与指标周期分别更新，撤回旧信息'),
 ('C06/C07','库位、WIP与FIFO','WH-01 / FL-01 / FL-02 / WH-03','投料前核地址、品质、当前量/上限和先后规则','补料停放、接手与更新同面可达；满位源端等待','生产/PMC定量；品质定状态；物流接手后更新'),
 ('IF-HANDOFF','跨层交接','WH-05 / WH-03','搬运前后核发收接口、工单批次、准备和收讫','在获准停放/接手面读，不在门前推出轨迹扫码','仓库/物流/接收方记录出发、到达、收讫与差异'),
 ('IF-SHIP','包装与出货','SW-02 / WH-04','包装核对与出货复核有各自证据','面向核对岗位；订单代号保护客户信息，物流停止后读卡','包装/品质/仓库分别确认自身字段，勿以看板替代放行'),
 ('IF-VISIT','访客停留','VT-01（T03仅示例）','看什么、真实证据、客户价值与授权范围','独立停留面/远观；不以参观牌为自由进入凭据','销售/行政审内容，生产/安全审停留与窗口')]
write_json('outputs/flow_review/sign_reading_rules.json',[dict(group=a,purpose=b,template_codes=c,reading_task=e,relative_siting=f,update_rule=g,actual_point_id=None,position_world=None,quantity=None,installation_height_mm=None) for a,b,c,e,f,g in sign_rules])
csv_file('标识读面与更新规则.csv',read('outputs/flow_review/sign_reading_rules.json'),['group','purpose','template_codes','reading_task','relative_siting','update_rule','actual_point_id','position_world','quantity','installation_height_mm'])

sources=[
 {'path':'data/floors.json','use':'V1楼层基线；6F/7F未知；不是现场批准楼层分配'},
 {'path':'outputs/drawings/8F_drawing_observations.json','use':'DWG文本、图签、单位和预览限制'},
 {'path':'outputs/installation_review/安装选址评审台账.json','use':'V2.2相对选址；C/S编号不是实测点'},
 {'path':'outputs/flow_review/research/logistics_analysis.json','use':'14物流接口及变量模型'},
 {'path':'outputs/flow_review/research/people_analysis.json','use':'5人员路线、10交叉核查与职责'},
 {'url':'https://www.hse.gov.uk/workplacetransport/separating.htm','title':'HSE — Separating pedestrians and vehicles','read_date':DATE,'use':'仅定性参考空间分离、可见交叉、换班和访客说明；不是中国法规/尺寸/批准依据'},
 {'url':'https://www.hse.gov.uk/workplacetransport/trafficroutes.htm','title':'HSE — Traffic routes','read_date':DATE,'use':'仅定性参考转弯、门口、视线与路径风险；不采用页面数值'},
 {'url':'https://www.hse.gov.uk/workplacetransport/loading.htm','title':'HSE — Loading and unloading','read_date':DATE,'use':'仅定性参考装卸授权与无关人员退出作业界面；不采用页面数值'}]
write_json('outputs/flow_review/sources.json',sources)
write_json('outputs/flow_review/review_manifest.json',{'revision':REV,'date':DATE,'status':'review_draft','diagrams':diagrams,'actual_coordinate_data':False,'actual_point_count':None,'production_release':False,'source_drawing_sha256':SOURCE_SHA,'scope':{'logistics_interfaces':len(logistics['interfaces']),'people_route_types':len(people['routes']),'crossing_review_types':len(people['crossings']),'adjacency_rules':len(adjacency)},'note':'上述数字是分析记录条目数，不是现场点位、标牌、容器或交叉口数量。'})

def bullets(items): return '<ul>'+''.join('<li>'+esc(i)+'</li>' for i in items)+'</ul>'
def card(title,body,cls=''):return '<article class="card '+cls+'"><h3>'+esc(title)+'</h3>'+body+'</article>'
def p(s):return '<p>'+esc(s)+'</p>'
def table(headers,rows):return '<table><thead><tr>'+''.join('<th>'+esc(i)+'</th>' for i in headers)+'</tr></thead><tbody>'+''.join('<tr>'+''.join('<td>'+str(i)+'</td>' for i in r)+'</tr>' for r in rows)+'</tbody></table>'
def image(path,cls='diagram'):return '<img class="'+cls+'" alt="'+esc(Path(path).stem)+'" src="'+data_url(path)+'">'
pages=[]
def page(title,subtitle,body): pages.append((title,subtitle,body))
page('BeePump 工厂目视化｜物流与人的动线深化','V2.3-FLOW-DRAFT · 2026-10-05 · 审阅稿',
 '<div class="cover"><div class="huge">让物料有交接<br>让人员有去向</div><p class="lead">补齐全厂流转、8F试点、人货交叉、看板读面与异常回流。</p><div class="grid three">'+
 card('14个物流接口',p('每个接口有前提、记录、责任角色和待测事实。'))+
 card('5类人员路线',p('员工、补料、品质、工程、访客分别评审。'))+
 card('10类交叉核查',p('优先空间分离；共享活动须有可执行控制。'))+
 '</div><p class="notice">功能方案已细化。实际点位、通道宽度、标牌数量与制作放行仍待图纸和现场核验。</p></div>')
page('来源、楼层与当前可确认的边界','设计提案不能替代图纸身份、单位与现场功能确认',
 '<div class="grid two">'+card('楼层采用V1基线',table(['楼层','讨论功能'],[[esc(a),esc(b)] for a,b in [('1F','金工 / 出货 / 主入口'),('2F','注塑'),('3F','成品仓'),('4F','手打气筒装配'),('5F','半成品仓 / IQC'),('6F / 7F','用途未知'),('8F','锂电充气泵装配试点'),('9F','喷漆专项接口')]]))+
 card('原图的已知冲突',bullets(['候选图身F0FBF写“八层平面图”，同框F10B1图签写“三层平面图”。','INSUNITS=1（inch），MEASUREMENT=0。8700/6000是图中数值一致性证据，尚未成为毫米尺寸。','已导出DXF并生成部分实体预览；原生Plot失败，存在缺字/字体替代及未绘制实体。','原料仓、电子仓、PCBA、老化房等文字是核查线索，不等于工序、权限或容量批准。']))+'</div>'+p('保留墙柱、电梯、楼梯、前室、消防门及救援口等固定结构。所有路线图均为功能关系；未把预览像素转换为安装坐标。原DWG SHA-256：'+SOURCE_SHA))
page('全厂物流拓扑与路线分支','收货—工序—装配—成品—出货；按产品工单选择中间路径',image(diagrams[0])+p('不强制全部来料整批上5F，也不让所有金工/注塑件先入半成品仓。送批/送样、入仓/直送、喷漆及老化均按真实工艺和授权条件选择。'))
page('8F试点功能泳道','先安排接手关系，再核实实际平面和读面',image(diagrams[1]))
page('物流路线选择与空间邻接','减少无必要中转，同时保持状态、批次与接收能力',
 '<div class="grid three">'+card('R-STOCK 入仓',p('适用于需要库存管理、工序等待或跨工单共享的物料。工序放行 → 5F基线接收 → 固定库位 → 按需求配套。'))+
 card('R-DIRECT 直送',p('适用路线卡允许，上道放行、下道准备和受控接收量均成立时。跳过实物中转仍保留批次、数量、品质和交接记录。'))+
 card('R-PAINT 专项',p('仅技术路线需要且9F专项存运/接收条件获确认时。完成后依路线卡返回仓储或下道，不强制回5F。'))+
 '</div>'+table(['邻接/分离对象','建议','核查'],[[esc(b),esc(c),esc(e)] for a,b,c,e in adjacency[:7]])+p('外采完整电池包按实际工单、批次与专项存运条件供料；不增加电芯制造，不把电子仓直接认定为电池仓。'))
page('共享货梯与跨层交接','任务准备、信息排队与实际搬运保持一致',image(diagrams[2]))
for i in range(0,14,2):
    blocks=[]
    for x in logistics['interfaces'][i:i+2]:
        blocks.append(card(x['id']+' '+x['name'],p('从：'+x['from'])+p('到：'+x['to'])+p('选路：'+x['route_condition'])+
            '<h4>发运 / 接手前提</h4>'+bullets(x['release_prerequisites'])+
            '<h4>记录与追溯</h4>'+p('；'.join(x['update_fields']))+
            '<h4>现场须核</h4>'+p('；'.join(x['unknown_site_facts']))+
            '<div class="owner">责任：'+esc(' / '.join(x['owner_roles']))+'<br>模板：'+esc(' / '.join(x['template_codes']))+'</div>'))
    page('物流接口 '+logistics['interfaces'][i]['id']+'–'+logistics['interfaces'][i+1]['id'],'L编号是功能交接记录编号；数量、位置、真实设备与窗口未确定','<div class="grid two interface">'+''.join(blocks)+'</div>')
page('五类人员路线与接手','人员到达、任务移动、停留和返回分别考虑',
 table(['角色','候选功能顺序 / 任务分支','控制与接手','责任'],[[esc(x['name']),esc(' → '.join(x['sequence'])),esc(x['logic']+' '+x['handoff']),esc(' / '.join(x['owner_roles']))] for x in people['routes']])+
 p('品质路线按来料、过程或样件任务选支，图表中的功能列表不是每次必经完整链。风淋、EPA、更衣与跨层节点只在现场规则实际适用时加入。'))
for start,end in [(0,3),(3,6),(6,8),(8,10)]:
    rows=[]
    for x in people['crossings'][start:end]:
        rows.append([esc(x['id']+' '+x['name']),esc(x['risk']),bullets(x['layout_first']),bullets(x['operating_rule']),esc(' / '.join(x['template_codes']))+'<br><small>'+esc(' / '.join(x['owner_roles']))+'</small>'])
    page('人货交叉核查 '+people['crossings'][start]['id']+'–'+people['crossings'][end-1]['id'],'先核自然路径、视线与独立停留，再评审共享活动控制',table(['核查对象','冲突','优先布局','运营规则','标识 / 责任'],rows)+p('这些是核查类型，尚不证明现场存在相同数量的交叉点。每类的现场演练与证据要求已列在《交叉点核查台账.csv》。'))
visitor_options=[
 ('A 制造能力','获准接待 → 1F金工远观 → 2F注塑远观 → 4F手泵装配 → 退出','工序身份、受控作业、批次与检验证据','不随出货车辆流转；实际跨层方式和生产窗口先确认。'),
 ('B 锂电泵控制','获准接待 → 8F独立观摩 → 测试/包装证据展示 → 退出','外采电池包追溯、有效工艺、适用验证、包装防错','不默认进入EPA/风淋/测试/电池暂存；受控区必要时远观。'),
 ('C 交付与追溯','获准接待 → 5F品质/库存证据展示 → 3F成品追溯展示 → 出货证明 → 退出','固定库位、真实批次、订单包装版本及出货复核','出货证明可在展示面讲解；不在实际装卸期间停留。')]
write_json('outputs/flow_review/visitor_options.json',[dict(id=a,sequence=b,evidence=c,conditions=e,actual_route_id=None,approved=False) for a,b,c,e in visitor_options])
page('客户参观：提供可选择的故事顺序','参观价值来自真实证据；获准停留优先于穿过完整生产链',
 '<div class="grid three">'+''.join(card(a,p(b)+'<h4>看什么</h4>'+p(c)+'<h4>进入条件</h4>'+p(e)) for a,b,c,e in visitor_options)+'</div>'+
 '<div class="grid two">'+card('进入之前',bullets(['销售/行政确认身份、拍摄和客户信息范围。','生产/物流确认运行影响与停留面，适用受控区由品质/工程确认。','陪同人核路线、退出与临时变更。讲解人不同时承担运动中的运输任务。']))+
 card('每个VT-01节点',bullets(['T03是示例访客编号，与楼层、区域、安装点不同。','看什么 → 可展示真实证据 → 对客户有什么价值。','未获内容及区域授权时，用远观、离线证据或跳过该节点。']))+'</div>')
page('反向流与异常分流','退料、空容器、一般不良、报废与专项安全异常分别交接',image(diagrams[3]))
page('补料节奏与缓冲：先实测，再定参数','可按物料族选定时小批或触发补料；当前参数均待测',
 '<div class="grid two">'+card('A 定时小批',p('适用于用量较可预测、窗口能协调且接收端能准备的物料。')+
 '<div class="formula">H = T + L<br>Q = ceil_to_pack(max(0, D̂(H) + S − IP))</div>'+p('T是实际补料间隔。L从请求建立到物料在供料点可用，涵盖备齐、预约、装卸、运输、接收及必要入位，不只货梯运行。'))+
 card('B 触发补料',p('适用于换型/消耗波动，取空或再订点信号可靠且响应时间可测的物料。')+
 '<div class="formula">H = L + δ<br>R = D̂(H) + S</div>'+p('δ从达到触发条件到请求建立；L从请求建立到供料点可用，二者不重叠。触发后补量按目标库存、标准补料包及未结请求决定；去重，不自动插队。'))+
 '</div>'+p('IP = 接收端可支配已放行现存 + 已确认在途 − 尚未供给欠供。其他工单预留、冻结、不合格不算可支配；新增需求D̂不能再重复包含已扣欠供。')+
 '<div class="grid two">'+card('容量门槛',p('需要量 B = ceil_to_pack(D̂(H)+S)；容器数 = ceil(B / 实际合格装量)。需不超过专业确认的接收容量，超出时调整响应、批量或窗口，不能扩大到通道。'))+
 card('数据口径',p('数量单位与包装量一致。S由需求和延误分布、责任人选择的服务水平决定，不填固定百分比。Little定律只诊断平均WIP，不能替代峰值或安全容量。'))+'</div>')
page('标牌与动线：读面、更新与驻足面','从“挂在哪里”细化到“何时读、谁更新、在哪里站”',
 table(['功能组','模板','读取任务','相对选址 / 可达','更新规则'],[[esc(a+' '+b),esc(c),esc(e),esc(f),esc(g)] for a,b,c,e,f,g in sign_rules]))

manifest_path=OUT/'template_variant_manifest.json'
variants=json.loads(manifest_path.read_text()) if manifest_path.exists() else []
if isinstance(variants,dict):variants=variants.get('templates',variants.get('variants',[]))
for i in range(0,len(variants),2):
    rows=[]
    for v in variants[i:i+2]:
        path=v.get('path') or v.get('svg_path'); name=v.get('name',v.get('code',''))
        rows.append(card(v['code']+' '+name,image(path,'template')+p('；'.join(v.get('change_reasons',[])) or '功能字段、品质及接手保持可核验；实际参数待填。')))
    page('可编辑模板深化 '+str(i//2+1),'V2.3-FLOW-DRAFT · 复用名义尺寸，保留原SVG；不是已放行印刷稿','<div class="grid two">'+''.join(rows)+'</div>')

field=OUT/'fieldwork'
if (field/'scenario_checks.json').exists():
    sc=json.loads((field/'scenario_checks.json').read_text()); sc=sc.get('scenarios',[]) if isinstance(sc,dict) else sc
    for i in range(0,len(sc),5):
        page('试点功能演练 '+str(i//5+1),'桌面规则核对及授权后的非危险演练；现场结果和验收状态仍待填',
            table(['场景','预期动作','责任 / 证据'],[[esc(x['id']+' '+x['name']),bullets(x['expected_action']),esc(' / '.join(x.get('owner_roles',x['owner'])))+'<br>'+esc('；'.join(x['evidence_needed']))] for x in sc[i:i+5]])+
            p('电池疑似安全异常只核信息、授权和已批准专项接口；不得人为制造异常，不在本册定义搬运或处置操作。'))
page('现场采集与分期门槛','先锁定证据，再样牌与交接，最后获准观察和展开',
 '<div class="grid two">'+card('① 图纸与真实流程',bullets(['工程选有效图框并核楼层、物理单位、两向校核长度、固定结构及现场版本。','核真实入口、工具及载荷外形、设施权限与服务层、等候/接收面。','逐物料记录需求、换型、容器装量、品质范围与真实路线卡。']))+
 card('② 1:1样牌与交接演练',bullets(['在拟定读面检查正常姿态、视线、照明、反光、遮挡与更新可达。','按批次/工单演练正常补料、满位、冻结、空容器、访客与检修接手。','生产、品质、物流、工程及适用安全角色各自记录问题与修改。']))+
 card('③ 授权运行观察',bullets(['获准后记录请求、备齐、预约、出发、到达、收讫和消耗事件。','观察真实人员高峰和载具活动，记录冲突/停等与视线，不先设假目标。','对需要量、容量、窗口和更新角色复核；结果用真实证据填。']))+
 card('④ 复核与逐层展开',bullets(['修订读面、接手、路线与参数，撤旧并保留版次。','逐层确认用途后再登记实际点位与数量；6F/7F继续待确认。','内容、位置、安装及适用专项证据齐备后，另行办理制作/安装放行。']))+'</div>')
page('可直接使用的空白表与待确认事项','采集表为空是未测量；不是现场需求或风险为零',
 table(['文件','用途','待填关键数据'],[['物流接口台账.csv','14条交接逐项评审','真实接口、路线卡、责任和准备条件'],['人员功能路线.csv / 交叉点核查台账.csv','人员与共享活动现场核查','自然路径、载具、视线、停等、保护与控制'],['fieldwork/blank_trip_log.csv','逐次记录真实运输事件','各事件时刻、物料、容器、数量单位、发收与差异'],['fieldwork/blank_crossing_log.csv','观察真实交叉情景','角色/载具、门扇和遮挡、等候、冲突及证据'],['fieldwork/survey_fields.csv','跨部门采集字段与责任','单位、容量、入场与专项证据'],['fieldwork/scenario_checks.csv / pilot_gates.json','试点演练与复核','实际观察、问题、修订和负责人结论']])+
 '<div class="grid two">'+card('业主 / 生产需确认',bullets(['8F/3F冲突图框与真实楼层功能。','主要搬运方式：推车/地牛、叉车或混合，以及实际运输设施。','补料现状与可试点物料族；包装/测试/返修接口适用性。']))+
 card('现场与专业需确认',bullets(['真实几何、净空、保护/视线、等候及核定接收能力。','标牌固定面、朝向、安装与1:1可读性。','访客授权、客户信息范围与专项流程。']))+'</div>')
page('资料引用与交付说明','原始输入不覆盖；V2.1、V2.2及既有概念图保留',
 table(['来源','本册采用范围'],[[esc(x.get('path',x.get('title',''))),esc(x['use'])] for x in sources])+
 p('HSE资料仅用于定性辨认交通与停留风险，不采纳其数值为本厂尺寸，不替代当地法规或专业确认。')+
 '<div class="references">'+''.join('<p><a href="'+esc(x['url'])+'">'+esc(x['title'])+'</a></p>' for x in sources if 'url' in x)+'</div>'+
 p('新输出：功能SVG图、CSV/JSON台账、6款V2.3编辑模板、采集与试点记录、离线审阅页和本PDF。实际点位文件data/points.json保持未勘测。正式Logo、物理色板、工程量与制作放行继续待核。'))

CSS='''
*{box-sizing:border-box}body{margin:0;background:#eee;font-family:"PingFang SC","Arial",sans-serif;color:#000}a{color:inherit;text-underline-offset:4px}
@page{size:420mm 297mm;margin:0}.page{width:420mm;height:297mm;background:white;padding:15mm 16mm;position:relative;page-break-after:always;overflow:hidden}.page:last-child{page-break-after:auto}
header{border-bottom:4px solid #FF6600;padding-bottom:16px;margin-bottom:22px}header .tag{font-size:16px;color:#3E3A39;letter-spacing:1px}h1{font-size:37px;line-height:1.2;margin:8px 0 12px}header p{font-size:21px;margin:0;color:#3E3A39}
.body{font-size:22px;line-height:1.5}p{margin:10px 0 14px}h3{font-size:27px;line-height:1.3;margin:0 0 12px}h4{font-size:21px;margin:14px 0 5px}.grid{display:grid;gap:20px}.two{grid-template-columns:1fr 1fr}.three{grid-template-columns:1fr 1fr 1fr}.card{padding:19px;border:1.5px solid #000;margin-bottom:16px;min-width:0}.card p:last-child{margin-bottom:0}.card ul{margin:8px 0 12px;padding-left:25px}li{margin-bottom:7px}.owner{font-size:18px;color:#3E3A39;border-top:1px solid #ccc;padding-top:10px;margin-top:12px}.interface{font-size:20px}.interface .card{padding:17px}.interface h4{font-size:20px;margin:10px 0 5px}.interface p{margin:7px 0}.interface li{margin:3px 0}
table{border-collapse:collapse;width:100%;font-size:19px;line-height:1.45;margin-bottom:16px}th{background:#000;color:white;text-align:left;font-size:19px}td,th{border:1px solid #bbb;padding:11px 12px;vertical-align:top}td ul{margin:0;padding-left:21px}td li{margin:0 0 7px}td small{font-size:16px;color:#3E3A39}.diagram{display:block;width:100%;max-height:760px;object-fit:contain}.template{width:100%;height:480px;object-fit:contain}.cover{padding-top:45px}.huge{font-size:80px;font-weight:700;line-height:1.15;margin-bottom:40px}.lead{font-size:31px}.notice{border-left:6px solid #FF6600;padding:14px 22px;margin-top:38px;background:#f5f4f2}.formula{background:#f5f4f2;padding:17px;font:24px/1.5 Arial;margin:18px 0}footer{position:absolute;bottom:12mm;left:16mm;right:16mm;border-top:1px solid #888;padding-top:9px;display:flex;justify-content:space-between;font-size:16px;color:#3E3A39}.references{font-size:18px}
'''
html_pages=[]
for n,(title,sub,body) in enumerate(pages,1):
    html_pages.append(f'<section class="page" id="p{n}"><header><div class="tag">BEEPUMP FACTORY VISUAL · {REV}</div><h1>{esc(title)}</h1><p>{esc(sub)}</p></header><div class="body">{body}</div><footer><span>审阅稿 · 功能关系非平面坐标 · 参数/现场审批待核</span><span>{n:02d} / {len(pages):02d}</span></footer></section>')
(OUT/'flow_print.html').write_text('<!doctype html><html lang="zh-CN"><meta charset="utf-8"><title>BeePump物流与人的动线深化</title><style>'+CSS+'</style><body>'+''.join(html_pages)+'</body></html>')
write_json('outputs/flow_review/page_index.json',[{'page':i+1,'title':x[0]} for i,x in enumerate(pages)])

# Offline index embeds all visual content; only document downloads need the folder.
calculator='''<section id="calculator"><h2>补料假设计算</h2><p>先填你的假设，再比较两种保护期。输出只是规划算例，不是核定容量或实际排程。L从请求建立到物料在供料点可用；δ从达到触发条件到请求建立，二者不重叠。新增消耗不含已扣欠供；所有数量用同一单位。触发补料的实际补量需另定目标库存并核对未结请求。</p><div class="inputs">
'''
fields=[('rate','新增消耗率','数量/分钟'),('lead','端到端响应L','分钟'),('interval','定时补料间隔T','分钟'),('delay','信号发现延迟δ','分钟'),('buffer','安全缓冲S','数量'),('available','可支配已放行现存','数量'),('transit','已确认在途','数量'),('backlog','尚未供给欠供','数量'),('pack','实际合格装量 / 标准补料包','数量/容器')]
for key,name,unit in fields:calculator+=f'<label>{esc(name)}<span>{unit}</span><input id="{key}" type="number" min="0" step="any" inputmode="decimal" autocomplete="off"></label>'
calculator+='</div><button id="calculate">计算假设</button><button id="clear" class="secondary">清空</button><div id="calc-result" aria-live="polite">待输入：所有字段留空，未采用现场数值。</div></section>'
calc_js='''
const keys=['rate','lead','interval','delay','buffer','available','transit','backlog','pack'];
document.querySelector('#calculate').onclick=()=>{
 const values=keys.map(k=>document.getElementById(k).value.trim());const r=document.getElementById('calc-result');
 if(values.some(x=>x==='')){r.textContent='请填齐字段；未知不能自动按0计算。';return;}
 const [d,L,T,delta,S,A,I,U,k]=values.map(Number);
 if([d,L,T,delta,S,A,I,U,k].some(x=>!Number.isFinite(x)||x<0)||L<=0||T<=0||k<=0){r.textContent='请输入有限非负值；响应、间隔与装量需大于0。';return;}
 const ip=A+I-U, Ha=T+L, Hb=L+delta;
 const needA=Math.ceil((d*Ha+S)/k)*k, qa=Math.ceil(Math.max(0,d*Ha+S-ip)/k)*k, R=d*Hb+S;
 const raw=[ip,Ha,Hb,needA,qa,R,needA/k];
 if(raw.some(x=>!Number.isFinite(x))||Math.abs(ip)>Number.MAX_SAFE_INTEGER||raw.some(x=>Math.abs(x)>Number.MAX_SAFE_INTEGER)){r.textContent='数值超出可靠计算范围，请缩小假设值。';return;}
 const fmt=x=>Number(x.toFixed(6)).toLocaleString('zh-CN');
 r.innerHTML='<strong>假设结果，待负责人核对</strong><br>库存位置IP：'+fmt(ip)+' 数量<br>A定时：保护期 '+fmt(Ha)+' 分钟；本次补量Q '+fmt(qa)+' 数量 / '+fmt(qa/k)+' 容器<br>A保护期需要量B：'+fmt(needA)+' 数量 / '+fmt(needA/k)+' 容器<br>B触发：保护期 '+fmt(Hb)+' 分钟；再订点R '+fmt(R)+' 数量；'+(ip<=R?'达到该假设触发条件':'尚未达到该假设触发条件')+'<br>触发后的实际补量另按目标库存、未结请求与核定容量决定。所有结果仍需与核定接收量、工单、品质、窗口和容器条件复核。';
};
document.getElementById('clear').onclick=()=>{keys.forEach(k=>document.getElementById(k).value='');document.getElementById('calc-result').textContent='待输入：所有字段留空，未采用现场数值。'};
document.querySelectorAll('img').forEach(x=>{x.tabIndex=0;x.onclick=()=>{document.querySelector('#zoom-image').src=x.src;document.querySelector('#zoom').showModal()};x.onkeydown=e=>{if(e.key==='Enter'){e.preventDefault();x.click()}}});
document.querySelector('#close').onclick=()=>document.querySelector('#zoom').close();
'''
download_rows=[('output/pdf/BeePump_Flow_People_Review_V2.3.pdf','完整PDF图册'),('BeePump_Flow_Review_V2.3_Source.zip','V2.3可编辑源文件包'),('INSTALLATION_REVIEW.html','V2.2安装与既有效果图'),('outputs/flow_review/物流接口台账.csv','物流接口台账'),('outputs/flow_review/人员功能路线.csv','人员功能路线'),('outputs/flow_review/交叉点核查台账.csv','交叉点核查台账'),('outputs/flow_review/标识读面与更新规则.csv','标识读面与更新规则'),('outputs/flow_review/fieldwork/survey_fields.csv','现场采集字段'),('outputs/flow_review/fieldwork/blank_trip_log.csv','空白运输事件表'),('outputs/flow_review/fieldwork/blank_crossing_log.csv','空白交叉观察表')]
web_css='''*{box-sizing:border-box}html{scroll-behavior:smooth}body{margin:0;color:#000;background:#f4f3f1;font:18px/1.65 "PingFang SC",Arial,sans-serif}a{color:#000;text-underline-offset:5px}header{background:#000;color:white;border-bottom:8px solid #FF6600;padding:42px max(24px,calc((100% - 1200px)/2))}header h1{font-size:42px;line-height:1.2;margin:10px 0 22px}header p{max-width:1050px}main{max-width:1248px;margin:auto;padding:30px 24px}nav{display:flex;flex-wrap:wrap;gap:12px;padding:22px 0}nav a{background:white;border:1px solid #000;padding:8px 15px;text-decoration:none}section{background:white;padding:30px;border:1px solid #ccc;margin:0 0 24px;scroll-margin-top:15px}h2{font-size:28px;line-height:1.35;margin:0 0 16px}h3{font-size:22px}.grid{display:grid;grid-template-columns:1fr 1fr;gap:22px}.card{min-width:0;padding:20px;border:1px solid #aaa;margin-bottom:10px}.card h3{margin:0 0 10px}img{max-width:100%;display:block;cursor:zoom-in;outline-offset:5px}.diagram{width:100%}.template{height:370px;width:100%;object-fit:contain}details{border-top:1px solid #ccc;padding:16px 0}summary{cursor:pointer;font-weight:700;font-size:21px}.record-grid{display:grid;grid-template-columns:1fr 1fr;gap:16px;margin-top:20px}.record-grid h4{margin-bottom:4px}.owner{font-size:16px;color:#3E3A39}ul{padding-left:25px}.inputs{display:grid;grid-template-columns:repeat(3,1fr);gap:20px}label{display:block;font-weight:600}label span{display:block;font-size:14px;font-weight:400;color:#3E3A39}input{display:block;width:100%;min-width:0;margin-top:8px;font:inherit;padding:10px;border:1px solid #000;border-radius:0}button{font:inherit;font-weight:600;background:#000;color:white;border:1px solid #000;padding:10px 20px;margin:22px 12px 14px 0;cursor:pointer}.secondary{background:white;color:#000}#calc-result{padding:18px;background:#f4f3f1;min-height:65px}table{width:100%;border-collapse:collapse}td,th{text-align:left;vertical-align:top;border:1px solid #aaa;padding:12px}th{background:#000;color:white}.notice{border-left:5px solid #FF6600;padding-left:18px}.pill{font-size:14px;letter-spacing:1px}.downloads{display:flex;flex-wrap:wrap;gap:14px}.downloads a{padding:12px;border:1px solid #000}dialog{width:min(96vw,1600px);height:94vh;max-width:none;padding:14px;background:#fff;border:2px solid black}dialog::backdrop{background:#000b}dialog img{height:calc(100% - 72px);max-width:100%;width:100%;object-fit:contain;cursor:default}dialog button{margin:0 0 10px}footer{padding:15px 0 40px;color:#3E3A39;font-size:16px}.concept{max-height:460px;width:100%;object-fit:contain}@media(max-width:650px){body{font-size:16px}header{padding:26px 20px}header h1{font-size:29px}main{padding:20px 12px}section{padding:20px 15px}.grid,.record-grid,.inputs{grid-template-columns:1fr}.template{height:300px}h2{font-size:24px}nav{gap:8px}nav a{font-size:15px}table{font-size:14px}td,th{padding:8px;overflow-wrap:anywhere}}
'''
sections=[]
sections.append('<section id="flows"><h2>功能关系图</h2><p>点击图片可放大。所有箭头表示交接逻辑，图中坐标仅用于排版；楼层名称沿用待核基线。</p>'+''.join(image(path) for path in diagrams)+'</section>')
records=[]
for x in logistics['interfaces']:
    records.append('<details><summary>'+esc(x['id']+' '+x['name'])+'</summary><div class="record-grid">'+card('功能路径',p(x['from']+' → '+x['to'])+p(x['route_condition']))+card('发运前提',bullets(x['release_prerequisites']))+card('记录与责任',bullets(x['update_fields'])+p(' / '.join(x['owner_roles'])))+card('待核事实',bullets(x['unknown_site_facts'])+p('模板：'+' / '.join(x['template_codes'])))+'</div></details>')
sections.append('<section id="interfaces"><h2>14个物流接口</h2>'+''.join(records)+'</section>')
sections.append('<section id="people"><h2>五类人员路线</h2>'+''.join('<details><summary>'+esc(x['name'])+'</summary>'+p(' → '.join(x['sequence']))+p(x['design_rule'])+p('授权与接手：'+x['authorization_gate']+' '+x['handoff'])+'</details>' for x in people['routes'])+'</section>')
sections.append('<section id="crossings"><h2>10类交叉核查</h2><p>优先在已获准空间分离。实际必须共享时，先核保护、视线和接手条件，再评审明确起止的运营窗口。</p>'+''.join('<details><summary>'+esc(x['id']+' '+x['name'])+'</summary><div class="record-grid">'+card('风险',p(x['risk']))+card('布局优先',bullets(x['layout_first']))+card('运营与模板',bullets(x['operating_rule'])+p(' / '.join(x['template_codes'])))+card('现场核验',bullets(x['verification'])+p(' / '.join(x['owner_roles'])))+'</div></details>' for x in people['crossings'])+'</section>')
sections.append('<section id="visitors"><h2>参观顺序候选</h2>'+''.join(card(a,p(b)+p('真实证据：'+c)+p('条件：'+e)) for a,b,c,e in visitor_options)+'</section>')
sections.append(calculator)
if variants:
    sections.append('<section id="templates"><h2>6款可编辑模板深化</h2><div class="grid">'+''.join(card(v['code']+' '+v.get('name',''),image(v.get('path',v.get('svg_path')),'template')+f'<a href="{esc(v.get("path",v.get("svg_path")))}">查看SVG源文件</a>') for v in variants)+'</div></section>')
concepts=['outputs/installation_review/C04_C05_生产与班组管理墙.png','outputs/installation_review/C06_C07_库位与WIP牌.png']
sections.append('<section id="concepts"><h2>既有效果图与这轮细化的对应</h2><p>沿用V2.2概念效果图；它们不反映真实建筑尺寸、车位数量或已确认安装面。这轮补充日会站位、看板更新、补料接手与满位源端等待规则。</p><div class="grid">'+''.join(image(path,'concept') for path in concepts)+'</div></section>')
sections.append('<section id="downloads"><h2>图册、源文件与现场表</h2><div class="downloads">'+''.join(f'<a href="{esc(path)}">{esc(name)}</a>' for path,name in download_rows)+'</div><p>原输入与V2.1/V2.2保留。实际点位、数量、材料定额和安装高度待核后另行登记。</p></section>')
sections.append('<section id="sources"><h2>来源与待确认</h2><p class="notice">候选图身8F、同框图签3F；物理单位与现场用途未核验。功能方案已细化，实际安装坐标仍未生成。</p>'+''.join('<p><a href="'+esc(x['url'])+'">'+esc(x['title'])+'</a>：'+esc(x['use'])+'</p>' for x in sources if 'url' in x)+'</section>')
nav=[('flows','功能图'),('interfaces','物流接口'),('people','人员路线'),('crossings','交叉核查'),('visitors','客户参观'),('calculator','补料假设'),('templates','编辑模板'),('downloads','文件与表单')]
web='<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>BeePump物流与人的动线深化</title><style>'+web_css+'</style><body><header><div class="pill">BEEPUMP FACTORY VISUAL · '+REV+'</div><h1>物流与人的动线深化</h1><p>把“做标牌”推进到“交接如何发生”：发运前提、员工上岗、访客停留、异常回流、共享运输和看板更新。</p><p>审阅稿 · 2026-10-05 · 功能关系非现场平面 · 实际参数与审批待核</p></header><main><nav>'+''.join(f'<a href="#{a}">{b}</a>' for a,b in nav)+'</nav>'+''.join(sections)+'<footer>独立BeePump项目 · 输入保留 · 未对外发布或采购 · 离线内容无需网络加载</footer></main><dialog id="zoom"><button id="close">关闭大图</button><img id="zoom-image" alt="放大预览"></dialog><script>'+calc_js+'</script></body></html>'
(ROOT/'FLOW_REVIEW.html').write_text(web)
print(json.dumps({'pages':len(pages),'diagrams':len(diagrams),'variants':len(variants),'outputs':['FLOW_REVIEW.html','outputs/flow_review/flow_print.html']},ensure_ascii=False))

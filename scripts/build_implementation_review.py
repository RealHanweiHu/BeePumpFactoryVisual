#!/usr/bin/env python3
"""Build the 1F/8F contractor review pack. Page geometry is never site geometry."""
from pathlib import Path
import base64,csv,hashlib,html,json

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'outputs/implementation_v2.4'
OUT.mkdir(parents=True,exist_ok=True)
REV='V2.4-IMPLEMENTATION-DRAFT';DATE='2026-10-07'
SOURCE_SHA='d368c39f3f5c9fdd2b783c8fc2949b6d1a744b03d5e9cafd172b17bc60a76918'
def esc(s):return html.escape(str(s))
def load(rel,default=None):
 p=ROOT/rel
 return json.loads(p.read_text()) if p.exists() else default
def write(rel,data):
 p=ROOT/rel;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
def paragraph(s):return '<p>'+esc(s)+'</p>'
def ul(items):return '<ul>'+''.join('<li>'+esc(x)+'</li>' for x in items)+'</ul>'
def card(title,body):return '<article class="card"><h3>'+esc(title)+'</h3>'+body+'</article>'
def table(headers,rows):return '<table><thead><tr>'+''.join('<th>'+esc(x)+'</th>' for x in headers)+'</tr></thead><tbody>'+''.join('<tr>'+''.join('<td>'+str(x)+'</td>' for x in row)+'</tr>' for row in rows)+'</tbody></table>'
def string(x):return '；'.join(map(str,x)) if isinstance(x,list) else json.dumps(x,ensure_ascii=False) if isinstance(x,dict) else '待核' if x is None else str(x)
def uri(rel):
 p=ROOT/rel;ext=p.suffix.lower();mime={'.svg':'image/svg+xml','.png':'image/png','.jpg':'image/jpeg'}.get(ext,'application/octet-stream')
 return 'data:'+mime+';base64,'+base64.b64encode(p.read_bytes()).decode()
def img(rel,kind='diagram'):return '<img class="'+kind+'" src="'+uri(rel)+'" alt="'+esc(Path(rel).stem)+'">'

class Figure:
 def __init__(self,title,sub,height=1040):
  self.height=height;self.title=title
  self.parts=[f'<svg xmlns="http://www.w3.org/2000/svg" width="1600" height="{height}" viewBox="0 0 1600 {height}" role="img" aria-label="{esc(title)}">',
   '<defs><marker id="a" markerWidth="9" markerHeight="9" refX="7" refY="4" orient="auto"><path d="M0 0 L7 4 L0 8" fill="#000"/></marker></defs>',
   '<metadata>'+esc(json.dumps({'revision':REV,'status':'relative_functional_design','coordinate_system':'page_px_only','position_world':None,'quantity':None,'production_release':False,'source_drawing_sha256':SOURCE_SHA},ensure_ascii=False))+'</metadata>',
   f'<rect width="1600" height="{height}" fill="white"/><rect width="1600" height="116" fill="#000"/><rect y="116" width="1600" height="8" fill="#FF6600"/>']
  self.text( forty:=40,49,title,34,'#fff',True);self.text(40,92,sub,22,'#fff')
 def text(self,x,y,s,size=23,color='#000',bold=False):
  self.parts.append(f'<text x="{x}" y="{y}" style="font-family:PingFang SC,Arial,sans-serif;font-size:{size}px;fill:{color};font-weight:{700 if bold else 400}">{esc(s)}</text>')
 def box(self,x,y,w,h,title,lines=(),conditional=False):
  dash=' stroke-dasharray="9 5"' if conditional else ''
  self.parts.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="#fff" stroke="#000" stroke-width="2"{dash}/>')
  self.text(x+16,y+36,title,26,'#000',True)
  for i,s in enumerate(lines):self.text(x+16,y+73+i*29,s,22)
 def line(self,points,dashed=False):
  dash=' stroke-dasharray="9 5"' if dashed else ''
  self.parts.append('<polyline points="'+' '.join(f'{x},{y}' for x,y in points)+f'" fill="none" stroke="#000" stroke-width="3"{dash} marker-end="url(#a)"/>')
 def rule(self,y):self.parts.append(f'<line x1="40" y1="{y}" x2="1560" y2="{y}" stroke="#999"/>')
 def save(self,name,notes):
  self.rule(self.height-101)
  for i,s in enumerate(notes):self.text(40,self.height-65+i*29,s,20)
  self.parts.append('</svg>');p=OUT/(name+'.svg');p.write_text('\n'.join(self.parts))
  write('outputs/implementation_v2.4/'+name+'.json',{'revision':REV,'drawing_type':'functional_adjacency_not_site_plan','description':self.title,'page_unit':'px','position_world':None,'actual_dimensions':None,'production_release':False,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
  return 'outputs/implementation_v2.4/'+name+'.svg'

figures=[]
f=Figure('1F｜主入口、金工与出货的分工','人流、生产物料与出货三条功能链；方框不是真实建筑分区',1130)
f.text(40,165,'人员 / 访客：先接待，再获准观察；员工到岗与装卸活动分别评审',24,'#000',True)
for x,title,lines in [(40,'人员到达',('入口品牌 / 楼层导览','BE-01 / WF-01')),(440,'接待与入场说明',('陪同 / 权限 / 保密','BE-02附属说明')),(840,'获准观察与管理',('独立停留 / 日会站位','VT-01 / PM-02')),(1240,'员工工位 / 离场',('工位SOP / 有效版本','SW-01 / WF-03'))]:
 f.box(x,195,320,142,title,lines)
for x in [40,440,840]:f.line([(x+320,265),(x+400,265)],True)
f.rule(370);f.text(40,415,'金工物料：来料按检验计划与工单选择；不是所有外购物料都需进入金工',24,'#000',True)
for x,title,lines in [(40,'收料 / 状态',('批与样关联 / 去向','WH-03 / QC状态卡')),(440,'金工工序',('设备身份 / 工装量具','EQ-01 / EQ-02 / SOP')),(840,'工序交接 / 检验',('批次 / 放行范围 / WIP','WH-03 / FL-01 / QC')),(1240,'工单下道接口',('入仓 / 直送 / 专项','WH-05 / FL-02'))]:
 f.box(x,445,320,142,title,lines)
for x in [40,440,840]:f.line([(x+320,515),(x+400,515)],x==40)
f.text(45,630,'金工输出可选：5F入仓；获准直送4F/8F；适用时9F喷漆后按路线卡返回。',22)
f.rule(665);f.text(40,710,'出货：来自真实成品备货接口，出货复核与装运接手分别记录',24,'#000',True)
for x,title,lines in [(40,'成品任务接入',('3F仅V1功能基线','订单 / 批次 / 箱件')),(440,'出货复核',('品质 / 包装 / 任务','WH-04分别核对')),(840,'获准待运与接手',('窗口 / 可接收量','WH-05 / FL-01')),(1240,'装运接口',('接手 / 差异 / 留档','无关人员退出作业面'))]:
 f.box(x,740,320,142,title,lines)
for x in [40,440,840]:f.line([(x+320,810),(x+400,810)])
f.text(40,960,'空容器、普通不良/返修及废料分别交接；未核定的门前、前室和通道不作溢出位。',24,'#000',True)
figures.append(f.save('1F_功能分区与相对选址',['实线表示一般交接，虚线表示条件或授权关系；不表示实际箭头朝向、路宽、距离或物理位置。','选址依据：真实自然人行路径、载具及载荷外形、门扇/转弯视线、独立等待与更新可达。']))

f=Figure('8F｜装配、补料、检验与客户观察','锂电充气泵装配为V1基线；外采完整电池包，不引入电芯制造',1130)
xs=[40,300,560,820,1080,1340]
for x,title,lines in zip(xs,['跨层接料','线边供料','装配作业','适用测试','包装核对','成品交接'],[('准备 / 批次','WH-05 / WH-03'),('地址 / 上限','WH-01 / FL-01'),('工单 / SOP','EQ / SW-01'),('方法 / 结果','QC / 条件老化'),('版本 / 首件','SW-02 / QC'),('放行 / 收讫','WH-03 / WH-05')]):
 f.box(x,205,220,142,title,lines)
for x in xs[:-1]:f.line([(x+220,276),(x+260,276)])
f.text(40,166,'正向物料：每段先确认接收准备与品质范围，再转运',24,'#000',True)
f.box(40,420,460,142,'空容器 / 退料',('分类清点，记录返回与再发','不与正向批次混记录'))
f.box(570,420,460,142,'普通不良 / 复验',('处置指令 → 获准返修 → 复验','未放行不回普通取料队列'))
f.box(1100,420,460,142,'电池安全异常（专项）',('停止普通流转；授权人员接手','按现场已批准专项流程'),True)
f.line([(410,347),(410,420)],True);f.line([(930,347),(930,420)],True)
f.rule(600);f.text(40,645,'员工到层：更衣、风淋或EPA进入只在现场适用且获准时加入',24,'#000',True)
for x,title,lines in [(40,'到层 / 获准进入',('WF-01 / BE-02','ES-01仅适用时')),(440,'当班 / 日会管理',('PM-01进度与异常','PM-02指标与行动')),(840,'员工自然路径',('保持视线与独立通行','避开补料运动界面')),(1240,'对应工位',('有效SOP / 设备状态','更新不跨物流路径'))]:f.box(x,675,320,142,title,lines)
for x in [40,440,840]:f.line([(x+320,744),(x+400,744)],True)
f.text(40,895,'访客：获准接待 → 独立观察面 / 真实证据展示 → 退出；不默认穿过生产或测试/暂存区。',24,'#000',True)
f.text(40,954,'满位先停止继续投入并协调源端等待；现场批准容量、路径、窗口与安装面另行放样。',24,'#000',True)
figures.append(f.save('8F_功能分区与相对选址',['原图“原料仓、电子仓、PCBA、老化房”等文字是核查线索，不证明工序/电池储存或进入权限已确定。','图中方框、节点、容器与箭头不是实际数量或现场坐标；品牌橙色仅在牌面，不用于地面。']))

f=Figure('安装关系｜固定面、吊挂、柱面与可更新模块','连接关系示意，不是锚固设计、构件尺寸或紧固件数量',1040)
details=[(40,180,'D01 墙面 / 品牌模块',['确认基材、隐蔽管线与固定条件','面板 + 经复核背架 / 固定体系','字标 / 展品的承载另核','保留消防、门扇与设备访问']),
 (830,180,'D02 区域吊牌',['只用工程确认的结构与专用支架','固定、防坠、净空和维护分别核','禁止把未核管线或线槽当吊点','按进路决定单/双面，实物只算一件']),
 (40,570,'D03 柱牌 / 货架端',['保留永久柱号和原设备载荷铭牌','不擅钻柱或破坏防火保护','夹具 / 标签轨依现场许可选择','避开叉臂、撞击和检修操作面']),
 (830,570,'D04 白板 / 文件框',['固定表头与可换内容分开','实际使用者1:1核可读和可更新','SOP由授权文件流程发新撤旧','卡槽在核准站位可接近'])]
for x,y,title,lines in details:
 f.box(x,y,730,305,title,lines)
 f.text(x+16,y+238,'施工方提交：材料、固定节点、样牌、适用检验资料',21)
 f.text(x+16,y+272,'业主记录：内容 / 位置 / 安装 / 适用专项结论',21)
figures.append(f.save('安装关系与可更新模块',['名义牌面尺寸见SVG/catalog；安装高度、朝向、固定节点、结构承载与现场间距均未造填。','现场替换材料、改变尺寸/位置或涉及电气、消防、结构时，按变更记录重新复核，不口头代替。']))

# Latest floor variants and operational artboards remain linked to their source metadata.
registry=load('data/templates.json',[])
new=[]
for rel in ['outputs/implementation_v2.4/template_manifest.json','outputs/implementation_v2.4/operations_template_manifest.json']:
 rows=load(rel,[])
 if isinstance(rows,dict):rows=rows.get('templates',rows.get('variants',[]))
 new.extend(rows)
current=[]
for code in ['WF-04','WH-01','PM-01','PM-02','FL-01']:
 row=next(t for t in registry if t['code']==code and t['revision']=='V2.1-DRAFT');current.append(row)
for code in ['WH-05','WH-03','FL-02','WH-04','WF-03','VT-01']:
 row=next(t for t in registry if t['code']==code and t['revision']=='V2.3-FLOW-DRAFT');current.append(row)
catalog=[]
for row in new+current:
 v=dict(row);v['physical_size_mm']=[row['w'],row['h']];v['actual_quantity']=None;v['actual_point_id']=None;v['production_release']=False
 v['use_boundary']='模板/内容提案；变量、正式Logo、真实方向/ID与现场条件确认后另发制作稿'
 catalog.append(v)
catalog.sort(key=lambda x:(x['code'],x['revision']))
write('outputs/implementation_v2.4/artboard_catalog.json',catalog)
with (OUT/'版面与名义尺寸索引.csv').open('w',newline='',encoding='utf-8-sig') as h:
 w=csv.writer(h);w.writerow(['模板代码','名称','版本','名义宽mm','名义高mm','SVG路径','实际数量','实际安装点','制作状态'])
 for x in catalog:w.writerow([x['code'],x['name'],x['revision'],x['w'],x['h'],x['path'],'待核','未放样','未制作放行'])

spec=load('outputs/implementation_v2.4/specs/floor_work_packages.json',[])
def normalize_requirements(obj):
 if isinstance(obj,list):
  if obj and 'requirements' in obj[0]:return [dict(x,floor_id=x.get('floor_id',floor.get('floor_id'))) for floor in obj for x in floor['requirements']]
  return obj
 if isinstance(obj,dict):
  if 'requirements' in obj:return obj['requirements']
  if 'floor_packages' in obj:return [dict(x,floor_id=x.get('floor_scope',floor.get('floor_id'))) for floor in obj['floor_packages'] for x in floor['requirements']]
  if 'floors' in obj:return normalize_requirements(obj['floors'])
  if 'work_packages' in obj:return normalize_requirements(obj['work_packages'])
 return []
requirements=normalize_requirements(spec)
for floor in ['1F','8F']:
 with (OUT/(floor+'_安装需求与实施接口.csv')).open('w',newline='',encoding='utf-8-sig') as handle:
  cw=csv.writer(handle);cw.writerow(['设计需求编号','拟定楼层范围','需求名称','相对安装面','阅读者','阅读后动作','更新规则','模板与名义尺寸','材料与固定候选','物流/品质接口','现场核对','责任角色','实际点位ID','实际安装数量','实际朝向','实际安装高度','制作安装记录'])
  for row in requirements:
   if row['floor_id']==floor:cw.writerow([row['requirement_id'],floor,row['name'],row['relative_installation_face'],string(row['reading_actor']),row['reading_decision'],row['update_logic'],row.get('template_summary',''),row.get('material_and_fixing_summary',''),row['quality_logistics_handoff'],string(row['pending_survey_and_authorization']),string(row['owner_roles']),'','','','',''])
def value(r,*names,default='待核'):
 for k in names:
  if k in r:return r[k]
 return default
def template_summary(r):
 return '；'.join(x['code']+' '+x.get('name','')+' '+str(x.get('nominal_size_mm',[])[0])+'×'+str(x.get('nominal_size_mm',[])[1])+'mm' for x in r.get('template_references',[]))
def material_summary(r):
 return '；'.join(x['family_id']+'：'+' / '.join(x.get('candidates',[])) for x in r.get('candidate_materials',[]))
materials=load('outputs/implementation_v2.4/specs/material_families.json',[])
if isinstance(materials,dict):materials=materials.get('families',materials.get('material_families',[]))

release_gates=[
 {'id':'G01','name':'现场与图纸锁定','contractor_action':'选有效图框，校单位/两向尺度/结构，核实际用途与自然路径，建立现场照片索引','owner_roles':['业主','工程','生产','仓库','物流','适用安全角色'],'required_records':['有效图框/版次','两向单位校核','现场用途/照片','工具与载荷/设施许可'],'status':'pending','authorization_evidence':None},
 {'id':'G02','name':'点位与工程量','contractor_action':'按REQ核实际安装面和进路；多个需求可合并为一个实物；记录点位ID、尺寸/面数/数量/固定条件','owner_roles':['工程','生产','仓库','品质','行政/销售'],'required_records':['真实点位图与台账','朝向/高度/更新站位','分项工程量','人货界面与等候条件'],'status':'pending','authorization_evidence':None},
 {'id':'G03','name':'1:1样牌与制作确认','contractor_action':'提交正式内容、字标/字体、材料色板、实物样牌及固定节点；核可读、更新、反光和真实扫码','owner_roles':['业主/设计','生产','品质','工程','适用安全角色'],'required_records':['内容签样及有效版次','1:1阅读记录','材料/色板/固定资料','各项专业结论'],'status':'pending','authorization_evidence':None},
 {'id':'G04','name':'按获准内容制作安装','contractor_action':'以具名记录发制作稿；确认作业窗口、设备/人员授权和保护；变更重新复核','owner_roles':['实施方','工程','生产','适用安全角色'],'required_records':['制作/安装放行记录','作业授权与方案','出厂/到货核对','变更记录'],'status':'pending','authorization_evidence':None},
 {'id':'G05','name':'逐点验收与移交','contractor_action':'核版本、位置、固定、可读、更新、撤旧与状态/二维码对应；移交维护与保修记录','owner_roles':['实施方','工程','生产','品质','仓库','行政/销售'],'required_records':['实际逐点验收','照片与竣工台账','有效源文件','更新/撤旧/维护交接'],'status':'pending','authorization_evidence':None}]
write('outputs/implementation_v2.4/release_gates.json',release_gates)
sources=[{'path':'inputs/cad/新厂房平面图（改）.dwg','sha256':SOURCE_SHA,'use':'原始CAD，实施方必须由业主/工程选有效图框与单位'},
 {'path':'outputs/implementation_v2.4/cad/','use':'1F三候选与8F冲突/限制证据，不作施工底图'},
 {'path':'outputs/flow_review/research/','use':'物流、人流交接及满位/异常规则'},
 {'url':'https://www.hse.gov.uk/workplacetransport/separating.htm','title':'HSE — Separating pedestrians and vehicles','read_date':DATE,'use':'仅定性参考自然人行路径、人员/车辆分离及访客入场说明'},
 {'url':'https://www.hse.gov.uk/workplacetransport/trafficroutes.htm','title':'HSE — Traffic routes','read_date':DATE,'use':'仅定性参考转弯、门口、视线与障碍物'},
 {'url':'https://www.hse.gov.uk/workplacetransport/loading.htm','title':'HSE — Loading areas','read_date':DATE,'use':'仅定性参考装卸授权与无关人员退出作业面'}]
write('outputs/implementation_v2.4/sources.json',sources)

pages=[]
def page(title,sub,body):pages.append((title,sub,body))
page('BeePump 1F + 8F｜实施交接设计','先完成主入口/金工/出货与锂电充气泵装配 · '+REV+' · '+DATE,
 '<div class="cover"><div class="huge">两层统一设计<br>逐项实施交接</div><p class="lead">功能分区 · 标牌版面 · 物流人流 · 材料固定 · 放样定量 · 样牌验收</p><div class="grid three">'+
 card('交给实施方做什么',paragraph('核图与踏勘、对应安装面、测量核量、分项报价、1:1打样及提交固定方案。'))+
 card('已完成的设计',paragraph('两层功能选址关系、可编辑SVG版面、字段与更新规则、规格台账和实施表单。'))+
 card('制作安装怎样发出',paragraph('将真实位置、正式内容和专业结论关联到版次，取得具名记录后发制作/安装稿。'))+
 '</div><p class="notice">本包可直接作为实施方的设计交接与深化任务书。实际点位/工程量及专业条件待现场锁定，当前未标为签字施工图。</p></div>')
page('实施方先读：文件与执行顺序','设计稿、现场证据、报价与验收使用同一编号和版本',
 table(['步骤','现在提供','实施方提交'],[['1 核图/踏勘','原DWG/DXF副本、候选预览、冲突与限制表','有效现场图框、物理单位、现场用途/固定面与照片'],['2 放样定量','两层功能图、REQ需求台账、模板目录和空白点位表','真实安装点、方向/高度/面数、测量来源与工程量'],['3 内容/材料打样','SVG源稿、材料家族、字号/更新规则与样牌检查表','正式字标与内容、1:1样牌、色板、固定/适用材料证据'],['4 制作安装','分阶段交接门槛、异常/变更记录表','与版次绑定的具名制作/安装记录及作业窗口'],['5 验收移交','逐点验收、照片及维护表','实际验收结果、竣工点位/源稿、撤旧/更新/保修交接']])+
 paragraph('REQ编号是设计需求，不是实际点位ID；模板数量不是标牌数量。多个需求可以由同一实物承接；双面牌按一件实物及两个阅读面登记。没有现场量的项目不能自动按每类1件报价。'))
page('原图与现场：必须锁定的三个接口','明确资料冲突，避免实施方按预览像素或旧文字直接施工',
 '<div class="grid three">'+card('1F：三组候选',paragraph('原图同层存在左、中、右三组图身/图签。右组文字较丰富，含仓储/模具/卷料/板料等字样，仅为评审优先候选，不是已确认版本。'))+
 card('8F：同框标题冲突',paragraph('图身F0FBF“八层平面图”，同框图签F10B1“三层平面图”。工程须选定有效框，不自动改标题或把房间字样当工艺批准。'))+
 card('单位与预览限制',paragraph('INSUNITS=1，物理单位未核验。两向标注只能证明图内数值一致。部分预览有缺字/未绘实体/弦近似等限制，不能按像素量毫米。'))+'</div>'+
 paragraph('原DWG SHA-256：'+SOURCE_SHA)+
 paragraph('楼层功能按用户任务及V1基线深化：1F主入口/金工/出货，8F锂电充气泵装配。实际用途、入口、设备、墙柱、电梯和固定结构以现场及有效版本为准；固定结构不为版式移动。'))

cad=OUT/'cad'
cad_svgs=sorted(cad.glob('*.svg')) if cad.exists() else []
for pth in cad_svgs:
 page('原图证据｜'+pth.stem,'源图部分实体预览，仅帮助工程选框；本页没有标注真实安装点',img(str(pth.relative_to(ROOT)),'source')+paragraph('保持源实体相对关系及可追溯窗口/变换。范围、文字、尺寸、用途与现场须由工程核定，图中源文字数字不作为本设计的容量/面积/安装量。'))
page('1F功能分区与相对选址','入口识别、金工作业与出货三种读面各有任务',img(figures[0]))
page('1F实施重点｜让金工与出货都有明确接手','不要让日会、检验和访客讲解占用装卸或搬运面',
 '<div class="grid two">'+card('入口与访客',ul(['BE-01品牌墙只用正式批准字标，入口标题不替代消防/交通指示。','WF-01在进入分岔前读目的地；箭头经真实路径核定后实例化。','BE-02到层形象与入场说明面对人行到达；观摩、文化/能力墙停留退出运输活动。']))+
 card('金工与设备',ul(['WF-02区域识别与WF-04永久柱号分开；不把区域码写成柱号。','EQ-01保留设备身份，EQ-03表示真实状态；不遮原厂铭牌、防护、按钮、散热或检修盖。','EQ-02工装量具身份与检验引用就近，SW-01由授权文件流程管理有效工单/版本。']))+
 card('出货与状态',ul(['WH-04品质、包装与出货任务各自核对，不相互替代。','正式待运/装运接口核接手、批次、箱件及客户包装版次；看板客见版用经授权代号。','发出、到达、收讫分别留记录；品质状态不因运输完成而变更。']))+
 card('回流与满位',ul(['FL-01写当前量/批准上限/单位；满位停止继续投入并协调源端等待。','空容器、退料、普通不良/返修、批准报废分类移交并保持批次历史。','不借前室、门口或人行通路作临时溢出位；真实等候与载具进路由现场核定。']))+'</div>')
page('8F功能分区与相对选址','补料、员工上岗、品质任务与访客停留分别评审',img(figures[1]))
page('8F实施重点｜接料—线边—工位—验证—包装','用真实BOM/工艺与质量范围决定路径；不统一套老化或EPA',
 '<div class="grid two">'+card('跨层接料与供料',ul(['WH-05发出准备与接收准备分别确认，目的端未就绪留在获准源端。','WH-01固定库位ID不随批次改；WH-03随对象，拆分保持母批/子批/容器关联。','FL-01/FL-02先核真实放行范围，再评FIFO；有期限适用时另评FEFO，冻结退出普通队列。']))+
 card('工位与班组',ul(['PM-01当班进度/异常，PM-02指标周期与行动，PM-03记录异常接手。','管理墙完整日会站位和更新动作退出通行；1:1核可读、可达、反光。','SW-01/SW-02保持有效版次；旧版撤回，客户包装资料不面向公开参观通路。']))+
 card('品质、测试与电池包',ul(['QC蓝待检、绿已放行、红不合格、黄暂缓与完整词义一致；不当交通优先权。','QC-05保持样件提交—受理—验证—反馈队列，并链接真实口径/报告。','BT-01/BT-02/ES-01仅在专项存运、适用测试或实际EPA条件确认后实例化；不自造工艺参数。']))+
 card('返修与对客展示',ul(['普通不良经品质处置和获准返修后回指定复验，不能直接标绿进包装。','疑似安全异常停止普通流转，由授权角色按已批准专项流程接手。','访客在独立获准停留面看真实证据；不默认穿过生产、测试、暂存或异常接口。']))+'</div>')

for floor in ['1F','8F']:
 rows=[x for x in requirements if value(x,'floor_id','floor')==floor]
 for i in range(0,len(rows),2):
  blocks=[]
  for r in rows[i:i+2]:
   name=string(value(r,'name','title','purpose'));rid=string(value(r,'requirement_id','id'))
   blocks.append(card(rid+' '+name,
    '<h4>选面与阅读</h4>'+paragraph(string(value(r,'relative_installation_face','relative_surface','siting')))+paragraph(string(value(r,'reading_actor','reading_roles')))+
    '<h4>动作与更新</h4>'+paragraph(string(value(r,'reading_decision','decision','reading_task')))+paragraph(string(value(r,'update_logic','update','update_rule','update_trigger')))+
    '<h4>模板 / 材料</h4>'+paragraph(template_summary(r))+paragraph(material_summary(r))+
    '<h4>物流 / 品质接口</h4>'+paragraph(string(value(r,'quality_logistics_handoff')))+
    '<h4>待核与责任</h4>'+paragraph(string(value(r,'pending_survey_and_authorization','site_checks','unknown_site_facts','pending_checks')))+paragraph('责任：'+string(value(r,'owner_roles','owners')))))
  page(floor+'安装需求 '+str(i//2+1),'功能需求要对应真实安装面；未填实际坐标、高度、朝向或数量','<div class="grid two requirements">'+''.join(blocks)+'</div>')

page('标牌系统：固定身份、对象状态与可换内容','编号、楼层、区域、柱号、库位、批次、参观节点各自独立',
 table(['信息层','模板','现场阅读任务','更新/内容责任'],[['入口/导览','BE-01/02 · WF-01/02/03/04/05','在到达和转向前读；区域与永久柱号不同','行政/生产确认用途和方向，工程核固定与净空'],['生产/管理','PM-01/02/03 · VS-01','当班异常、周期指标、行动接手及6S真实标准','生产/PMC/品质等按事件与周期更新，未知不写0'],['对象/物流','WH-01/02/03/04/05 · FL-01/02','投料/接手前核地址、批次、品质范围、当前量和上限','仓库/物流/生产记录，品质授权改质量状态'],['设备/工位','EQ-01/02/03 · SW-01/02 · MD-01条件','真实设备、工装、工艺版本、状态与换型核对','工程管理身份，技术/品质/生产按受控文件确认'],['质量/专项','QC-01/02/03/04/05 · BT-01/02 · ES-01条件','质量对象与动作；专项内容和进入资格有真实依据','品质授权；相关专项由现场专业角色确认'],['访客/证据','VT-01 · BE-03/04','授权看什么、真实证据及客户价值；保密/拍摄范围','销售/行政审内容，生产/物流/适用安全角色审停留']])+
 paragraph('SVG名义尺寸是设计模块，不是现场尺寸。中文为主，英文辅助；字高为名义em毫米，字形实际墨迹与材料成品需1:1核。正式Logo、QR真实映射、方向及可换字段应在制作稿中核定，草案占位不得混入成品。'))

for i in range(0,len(catalog),2):
 blocks=[]
 for x in catalog[i:i+2]:
  body=img(x['path'],'template')+paragraph(f"{x['w']} × {x['h']} mm 名义模块 · {x['revision']}")
  body+=paragraph('；'.join(x.get('change_reasons',[])) or x.get('note','保留已审结构，实际ID、工单、容量与内容按具名样牌记录填写。'))
  blocks.append(card(x['code']+' '+x['name'],body))
 page('可编辑版面 '+str(i//2+1),'两层专版与操作卡统一；尺寸可追溯，源SVG保留文字可编辑','<div class="grid two">'+''.join(blocks)+'</div>')

page('材料与工艺：按使用环境提交样品','品牌色值保持一致，材料的反光、清洁、耐油/磨损和适用专项逐项核',
 '<div class="grid two">'+card('大牌 / 品牌模块',ul(['优先采用V1材料系统中的哑光金属或获准墙面模块；厚度、背架、重量与固定节点由实施方深化。','字标、样件盒和展品支撑独立核承载、防坠与清洁，不从效果图量构件。','不同材料分别提交#FF6600/#000000/#FFFFFF/#3E3A39物理色板，实物签样。']))+
 card('白板 / 卡槽 / 文件框',ul(['固定印刷层与可擦写/可换字段分开，供日常更新；耐清洁与擦写残影以样品核。','卡槽/磁性件须适合实际设备、货架及作业环境，不妨碍操作/检修。','EPA、温度、油污或其他特殊环境依企业实际要求验证材料，不默认普通塑料或金属适用。']))+
 card('小卡 / 库位标签',ul(['状态卡跟唯一受控对象，旧卡撤回；耗材数量按真实容器和替换策略定。','标签轨、码区与读面面对真实扫描/存取方向；QR真实ID绑定后再生成并实扫。','尺寸/附着、磨损、反光和手套操作以实际样牌和容器测试。']))+
 card('地面 / 专项接口',ul(['FM-01是图例评审，不能当地坪施工图；线宽、颜色、线长和作业窗口由实际专项方案核定。','品牌橙色不用于地面。受控交通、消防、疏散和其他标准安全图形独立，不套VI。','结构、消防、承载、电气、ESD及电池/喷漆适用专项由责任专业确认并留证。']))+'</div>')
if materials:
 for i in range(0,len(materials),3):
  page('材料家族与样品提交 '+str(i//3+1),'选用条件和适用资料须与具体点位、环境及模板版次关联',table(['家族 / 模板','候选材料与条件','固定与提交'],[[esc(x['id']+' '+x['name'])+'<br>'+esc(' / '.join(x['codes'])),esc(' / '.join(x['candidates']))+'<br><br>'+esc('；'.join(x['conditions'])),esc(x['fix'])+'<br><br>逐项制作、样品、安装、移交核查见材料台账及对应安装需求。'] for x in materials[i:i+3]]))
page('安装与可更新结构关系','墙面/吊挂/柱面/文件框采用不同固定与维护逻辑',img(figures[2]))
page('工程量与报价口径','先有真实安装点，再汇总实物、面、线长和面积',
 '<div class="grid two">'+card('工程量规则',ul(['按已放样点位统计实物件数，另列面数。双面牌一件实物两面，不作为两个安装点。','模块化墙面、独立字标、展柜/样件盒等按合同确定唯一计价边界，避免整套与部件重复。','地面线按现场批准线长/面积计，不用模板示意长或源图未核数值。','未定数量/单价/税费/运输/安装费用留空；未知不是0，无总价结论。']))+
 card('实施方报价需回答',ul(['采用哪个材料家族、名义尺寸和单/双面；是否含背架、固定、印刷/表面与安装。','现场改尺寸、工况材质、防坠或结构深化等如何列差异项。','样牌、核图/踏勘、安装、拆旧、成品保护、清洁、维护/保修和资料是否包含。','计价单位、含税口径、运输、作业窗口与实际交付承诺，由双方记录。']))+'</div>'+
 paragraph('报价范围CSV提供分类与空白参数。REQ需求行不自动生成数量；库位/状态卡/设备标识须以真实资产、容器、储位或工位清单核量。'))
for gate_offset in [0,3]:
 page('制作与安装的发出条件 '+str(gate_offset//3+1),'按五个证据门槛执行；模型不替任何角色签字',table(['门槛','实施方动作','记录 / 责任'],[[esc(x['id']+' '+x['name']),esc(x['contractor_action']),ul(x['required_records'])+paragraph(' / '.join(x['owner_roles']))] for x in release_gates[gate_offset:gate_offset+3]]))
page('1:1样牌、安装验收与维护移交','先可读、可更新，再核实际位置/固定和状态对象',
 '<div class="grid two">'+card('内容与样牌',ul(['正式字标/中文/英文/编号/方向一致；物料、对象状态、SOP和QR映射核真实记录。','实际主要接近方向与使用姿态读得清，不横向压缩字形；核照明、反光和遮挡。','可更新字段在获准站位可接近，手套/卡夹/擦写/换页可操作，旧版完整撤回。']))+
 card('到货与安装',ul(['材料、尺寸、工艺、色板和固定体系与具名样牌/专业记录一致，差异建变更单。','与实际点位ID、朝向、安装高度/固定面对应；不遮挡设施、防护、操作或检修。','检查安装保护、连接、防坠/防倾倒适用情况及清洁，专业验收使用真实证据。']))+
 card('物流与人员演练',ul(['在获准范围观察接收准备、满位源端等待、冻结拦截、空容器与普通返修复验。','核换班、日会、检验、扫码、装卸和访客停留是否进入运输活动/受控作业。','不制造设备故障、危险冲突或电池异常；专项异常只做信息和授权桌面核对。']))+
 card('竣工与维护',ul(['交实际点位/照片/有效SVG及打印版次、材料与安装记录、验收及变更证据。','指定日常更新与旧版撤回角色；区域、工艺、班组或运输变化触发复核。','记录保修范围、维护方法和备件/耗材口径；未验收事项列未结清单。']))+'</div>')

scene=load('outputs/implementation_v2.4/scenes/manifest.json',[])
if isinstance(scene,dict):scene=scene.get('scenes',[])
for s in scene:
 page(string(value(s,'title','name')),'概念效果示意；不是本厂实景、建筑/位置/尺寸或施工数量证明',img(s['path'],'scene')+paragraph(string(value(s,'description')))+paragraph(string(value(s,'note',default='安装构件、样件数量及生成小字不作实施参数，制作按SVG及具名样牌记录。'))))
page('交付索引与待闭合项目','设计交接可开始；现场证据与制作/安装放行按记录完成',
 table(['文件','实施用途'],[['1F/8F功能SVG与原图候选','核自然路径与相对选面；有效底图锁定后另做真实点位叠加'],['可编辑版面及侧车','保留源代码/文字/名义尺寸和改动理由；确认后实例化制作稿'],['两层需求与材料/报价CSV/JSON','逐项核面、量、单价、固定与责任；未知保持待核'],['现场放样与验收表PDF/CSV','记录图框、测量、内容/材料样牌、实际点位及逐点结果'],['原DWG和原生DXF副本','实施方使用已有授权CAD校核，补字体/依赖；不经陌生在线转换'],['文件HASH与验证报告','核对版本及原输入字节，确保交付和施工方收到同一文件']])+
 paragraph('尚需闭合：有效1F/8F图框、毫米换算与现场用途；实际运输工具/设施权限和接收空间；正式Logo、真实ID/方向及工艺/专项范围；按内容、位置、安装和适用专业分别留具名记录。')+
 '<div class="references">'+''.join('<p><a href="'+x['url']+'">'+esc(x['title'])+'</a>：'+esc(x['use'])+'。仅定性参考，不作中国法规、尺寸或批准依据。</p>' for x in sources if 'url' in x)+'</div>')

CSS='''*{box-sizing:border-box}body{margin:0;background:#eee;color:#000;font-family:"PingFang SC",Arial,sans-serif}@page{size:420mm 297mm;margin:0}.page{width:420mm;height:297mm;background:#fff;padding:14mm 16mm;position:relative;page-break-after:always;overflow:hidden}.page:last-child{page-break-after:auto}header{border-bottom:4px solid #FF6600;padding-bottom:13px;margin-bottom:20px}header .tag{font-size:15px;color:#3E3A39}h1{font-size:36px;line-height:1.22;margin:8px 0 10px}header p{font-size:20px;color:#3E3A39;margin:0}.body{font-size:21px;line-height:1.5}p{margin:9px 0 13px}h3{font-size:26px;line-height:1.25;margin:0 0 12px}h4{font-size:19px;margin:12px 0 4px}ul{padding-left:24px;margin:8px 0 12px}li{margin-bottom:7px}.grid{display:grid;gap:20px}.two{grid-template-columns:1fr 1fr}.three{grid-template-columns:1fr 1fr 1fr}.card{border:1.2px solid #000;padding:18px;margin-bottom:14px;min-width:0}.requirements{font-size:18px;line-height:1.45}.requirements .card{padding:15px}.requirements h3{font-size:22px}.requirements p{overflow-wrap:anywhere}table{border-collapse:collapse;width:100%;font-size:19px;line-height:1.42;margin-bottom:16px}td,th{border:1px solid #aaa;padding:11px 12px;vertical-align:top}th{background:#000;color:white;text-align:left}td ul{padding-left:21px;margin:0}td li{margin-bottom:5px}td p{margin:7px 0 0}.diagram,.source,.scene{width:100%;height:770px;display:block;object-fit:contain}.template{width:100%;height:510px;object-fit:contain}.cover{padding-top:35px}.huge{font-size:76px;line-height:1.15;font-weight:700;margin-bottom:35px}.lead{font-size:29px}.notice{padding:15px 20px;border-left:6px solid #FF6600;background:#f5f4f2;margin-top:25px}.references{font-size:17px}a{color:black;text-underline-offset:4px}footer{position:absolute;bottom:12mm;left:16mm;right:16mm;border-top:1px solid #888;padding-top:8px;display:flex;justify-content:space-between;font-size:15px;color:#3E3A39}'''
CSS+=' .scene{height:680px}'
def doc_html(pages,css,title):
 parts=[]
 for i,(name,sub,body) in enumerate(pages,1):parts.append(f'<section class="page"><header><div class="tag">BEEPUMP FACTORY VISUAL · {REV}</div><h1>{esc(name)}</h1><p>{esc(sub)}</p></header><div class="body">{body}</div><footer><span>设计交接 · 现场放样/专业记录待完成 · 未制作安装放行</span><span>{i:02d} / {len(pages):02d}</span></footer></section>')
 return '<!doctype html><html lang="zh-CN"><meta charset="utf-8"><title>'+esc(title)+'</title><style>'+css+'</style><body>'+''.join(parts)+'</body></html>'
(OUT/'implementation_print.html').write_text(doc_html(pages,CSS,'BeePump1F8F实施交接设计'))
write('outputs/implementation_v2.4/page_index.json',[{'page':i+1,'title':x[0]} for i,x in enumerate(pages)])

# Printable forms contain empty evidence/decision cells; they are not synthesized approvals.
def blank_fields(labels):return '<div class="fields">'+''.join('<div><b>'+esc(x)+'</b><span class="line"></span></div>' for x in labels)+'</div>'
def blank_rows(headers,count=6):return table(headers,[['&nbsp;' for _ in headers] for _ in range(count)])
forms=[]
def form(title,sub,body):forms.append((title,sub,body))
form('F01 图纸与现场锁定','1F / 8F填写对应楼层；有效版本、单位与现场依据逐项保留',blank_fields(['楼层 / 图框 / 版次','现场用途 / 日期','图身标题与图签结论','源文件SHA / 记录引用'])+
 paragraph('封存DWG SHA：'+SOURCE_SHA)+blank_rows(['方向','源标注 / CAD长度','实测 / 单位换算','证据引用'],2)+
 blank_fields(['固定结构 / 门 / 电梯 / 消防边界','主要人行与载具 / 载荷外形','接收 / 等候 / 管理停留面','照片与依赖 / 缺字清单'])+paragraph('核验结论、具名角色及证据（未记录不视为通过）：')+blank_rows(['事项','责任角色','结论 / 未结项','日期 / 记录'],3))
form('F02 单个点位放样记录','REQ需求可以合并或拆分；实际点位ID由现场确定',blank_fields(['实际point_id / floor_id','关联REQ / 模板code + revision','有效底图/源SHA','区域 / 固定面 / 照片引用'])+blank_fields(['CAD世界XY / 单位 / 校核','测量基准 / 两向定位依据','主阅读进路 / 朝向','实际宽高 / 名义模块差异','安装高度 / 固定条件','实物数量 / 单双面 / 单位','可读站位 / 更新可达','门扇 / 载具 / 检修 / 专项影响'])+blank_rows(['复核项','角色','结论 / 证据'],4)+paragraph('现场简图、坐标与固定节点另附。图册排版坐标不能作为CAD世界坐标。'))
form('F03 内容与1:1样牌核对','正式字标、ID、方向、字体与可换字段核清后另发制作稿',blank_fields(['点位 / 模板 / 本次版本','正式Logo与字体授权来源','固定中文 / 英文 / 编号','方向 / 去向 / 楼层用途依据','可换字段 / 更新角色','QR真实目的 / 对象 / 扫码证据'])+blank_rows(['检查','使用者 / 条件','实际结果 / 问题','证据'],7)+paragraph('检查包括：正常姿态/进路可读，光照/反光/遮挡，墨迹字高与转曲，手套换卡/擦写，SOP有效版次与旧版撤回，真实状态对象和QR。')+blank_fields(['内容记录 / 具名角色','样牌结果 / 制作稿引用']))
form('F04 材料与固定深化','固定节点及适用专项由责任专业复核；不从概念图取尺寸',blank_fields(['点位 / 材料家族 / 版本','材料构成 / 厚度 / 表面 / 批次','名义与实际成品尺寸','物理色板 / 清洁与反光样品','实际基材 / 背架 / 固定节点','结构 / 防坠 / 防倾倒适用证据','EPA / 温度 / 油污等适用条件','施工保护 / 作业窗口 / 维护方式'])+blank_rows(['提交资料 / 样品','实施方来源','责任专业结论 / 未结项','记录'],4)+blank_fields(['替代或变更内容','具名记录与版次绑定']))
form('F05 工程量与分项报价','不得把需求/模板条数当件数；报价单位与包含范围唯一',blank_fields(['清单版本 / 点位统计依据','报价方 / 日期 / 有效条件','含税口径 / 运输 / 安装','拆旧 / 打样 / 保护 / 保修范围'])+blank_rows(['项目 / 点位','唯一计价单位','实物量 / 面数','单价 / 合价'],8)+blank_fields(['地面长度/面积测量依据','差异项 / 替代材料 / 未定量项','作业窗口与交付承诺','双方记录引用'])+paragraph('双面牌一件实物两面；整套模块与部件避免重复计价。未知留空，不填0，不生成假总价。'))
form('F06 逐点安装验收','结论由真实验收填写；本表没有预填合格或批准',blank_fields(['点位ID / 模板版本 / 位置','安装日期 / 实施方 / 验收角色','放行记录 / 实际材料 / 固定','实际朝向 / 高度 / 面数 / 数量'])+blank_rows(['验收项目','实际观察 / 测量','结论 / 待整改','照片/记录'],8)+paragraph('核内容版次与ID、位置/朝向、实际固定和专业条件、设施/操作检修保持、正常阅读与更新可达、颜色/表面、对象状态/QR、旧版撤回及清洁。')+blank_fields(['未结项 / 整改责任 / 复验','具名验收记录引用']))
form('F07 变更与维护移交','用途、工艺、物流、材料、版次或安装条件变化要关联重审',blank_fields(['变更ID / 点位 / 模板前后版本','变更原因与关联图纸/工艺','影响内容 / 数量 / 固定 / 专项','重新复核角色 / 记录','旧版撤回 / 替换生效依据','竣工点位图 / 有效SVG / 照片','更新角色 / 触发时机 / 维护方法','保修 / 耗材 / 备件 / 未结清单'])+blank_rows(['交接内容','发出角色','接手角色','实际记录'],4))
form('F08 现场照片与人员/物流核查','只观察获准业务；不制造冲突、故障、满位或电池异常',blank_fields(['楼层 / 日期 / 获准观察范围','自然人行路径 / 实际运输工具','门扇 / 转弯 / 遮挡状态','日会 / 检验 / 扫码 / 观摩站位'])+blank_rows(['照片ID / 位置','接近方向 / 任务','观察事实','关联REQ/点位'],7)+blank_fields(['等待 / 接收与满位规则核查','疑似问题 / 责任角色 / 记录'])+paragraph('电池专项异常仅信息与授权桌面核对，不执行处置或搬运演练；未观察/未确认保持空值。'))
FORMCSS=CSS+'''@page{size:A4;margin:0}.page{width:210mm;height:297mm;padding:12mm 13mm}h1{font-size:25px}header{padding-bottom:9px;margin-bottom:16px}header p{font-size:14px}.tag{font-size:11px!important}.body{font-size:14px;line-height:1.45}p{margin:8px 0 12px}table{font-size:12px}td,th{padding:9px 7px}td{height:40px}footer{left:13mm;right:13mm;bottom:9mm;font-size:10px}.fields{display:grid;grid-template-columns:1fr 1fr;gap:15px 20px;margin:15px 0 20px}.fields b{display:block;font-weight:600}.line{display:block;border-bottom:1px solid #888;height:32px}.page:nth-child(1) .line{height:25px}'''
(OUT/'forms_print.html').write_text(doc_html(forms,FORMCSS,'BeePump1F8F现场放样与验收表'))
write('outputs/implementation_v2.4/forms_index.json',[{'page':i+1,'title':x[0]} for i,x in enumerate(forms)])

webcss='''*{box-sizing:border-box}body{margin:0;background:#f4f3f1;color:#000;font:18px/1.65 "PingFang SC",Arial,sans-serif}a{color:black;text-underline-offset:4px}header{background:#000;color:white;border-bottom:8px solid #FF6600;padding:35px max(22px,calc((100% - 1200px)/2))}header h1{font-size:40px;line-height:1.3;margin:10px 0 18px}header p{max-width:1050px}main{max-width:1248px;margin:auto;padding:25px 24px}nav{display:flex;gap:12px;flex-wrap:wrap;padding:18px 0 25px}nav a{background:white;border:1px solid black;padding:8px 14px;text-decoration:none;font-weight:600}section{background:white;padding:28px;border:1px solid #bbb;margin-bottom:24px;scroll-margin-top:20px}h2{font-size:29px;margin:0 0 14px}h3{font-size:23px}.grid{display:grid;grid-template-columns:1fr 1fr;gap:18px}.card{border:1px solid #999;padding:18px;margin-bottom:14px;min-width:0}img{max-width:100%;cursor:zoom-in;display:block;outline-offset:5px}.diagram,.source,.scene{width:100%;max-height:800px;object-fit:contain}.template{width:100%;height:370px;object-fit:contain}.downloads{display:flex;gap:12px;flex-wrap:wrap}.downloads a{display:block;padding:12px;border:1px solid black}details{border-top:1px solid #bbb;padding:15px 0}summary{font-weight:700;cursor:pointer}.notice{border-left:5px solid #FF6600;padding-left:18px}table{width:100%;border-collapse:collapse}td,th{border:1px solid #aaa;padding:10px;vertical-align:top;text-align:left}th{background:#000;color:white}button,input,select{font:inherit;padding:8px 12px;border:1px solid #000;background:#fff;color:black}label{display:block}.filter{display:flex;gap:15px;flex-wrap:wrap;margin:20px 0}a:focus-visible,button:focus-visible,summary:focus-visible{outline:3px solid black;outline-offset:4px}dialog{width:min(96vw,1600px);height:94vh;padding:14px;border:2px solid black;max-width:none}dialog::backdrop{background:#000b}dialog img{width:100%;height:calc(100% - 65px);object-fit:contain;cursor:default}dialog button{margin:0 0 10px;background:#000;color:white;cursor:pointer}footer{font-size:15px;color:#3E3A39;padding:18px 0 35px}@media(max-width:650px){body{font-size:16px}header{padding:25px 20px}header h1{font-size:28px}main{padding:18px 12px}section{padding:18px 14px}.grid{grid-template-columns:1fr}.template{height:300px}h2{font-size:24px}.filter{gap:10px}}
'''
sections=[]
sections.append('<section id="handoff"><h2>实施方按什么执行</h2><p class="notice">设计交接包用于核图、踏勘、定量、报价和打样。真实位置、内容和专业记录闭合后另发制作/安装稿。</p>'+''.join('<details><summary>'+esc(x['id']+' '+x['name'])+'</summary>'+paragraph(x['contractor_action'])+ul(x['required_records'])+paragraph('责任：'+' / '.join(x['owner_roles']))+'</details>' for x in release_gates)+'</section>')
sections.append('<section id="floor1"><h2>1F：入口、金工与出货</h2>'+img(figures[0])+'</section>')
sections.append('<section id="floor8"><h2>8F：装配与受控交接</h2>'+img(figures[1])+'</section>')
reqhtml=[]
req_labels={'relative_installation_face':'相对安装面','reading_actor':'阅读者','reading_decision':'阅读后动作','update_logic':'更新规则','template_code':'模板代码','template_revision_proposal':'建议版本','nominal_dimensions_note':'名义尺寸边界','material_family_ids':'材料家族','owner_roles':'责任角色','quality_logistics_handoff':'物流与品质接口','pending_survey_and_authorization':'现场核对','fabrication_qc':'制作核查','full_scale_sample_qc':'1:1样牌核查','installation_qc':'安装核查','handover_qc':'移交核查','actual_point_id':'实际点位ID','actual_floor_id':'实际楼层（放样）','actual_area_id':'实际区域ID','actual_quantity_piece':'实际件数','actual_faces_per_piece':'每件阅读面数','position_world':'真实CAD坐标','facing_degrees':'真实朝向','installation_height_mm':'安装高度mm','confirmed_installed_size_mm':'确认成品宽高mm','approved_material_spec':'确认材料','approved_fixing_detail_ref':'确认固定节点'}
for r in requirements:
 floor=string(value(r,'floor_id','floor'));rid=string(value(r,'requirement_id','id'));name=string(value(r,'name','title','purpose'))
 reqhtml.append('<details class="requirement" data-floor="'+esc(floor)+'"><summary>'+esc(rid+' '+name)+'</summary>'+paragraph('模板：'+template_summary(r))+paragraph('材料候选：'+material_summary(r))+''.join('<p><b>'+esc(label)+'：</b>'+esc(string(r.get(k)))+'</p>' for k,label in req_labels.items() if k in r)+'<p>制作安装状态：待现场与具名记录闭合。</p></details>')
sections.append('<section id="requirements"><h2>两层安装需求与读面</h2><p>功能需求编号与实际点位分开；对应面、进路、可达和记录逐项核。</p><div class="filter"><label>筛选楼层 <select id="floor-filter"><option value="all">全部</option><option value="1F">1F</option><option value="8F">8F</option></select></label><span id="req-count"></span></div>'+''.join(reqhtml)+'</section>')
sections.append('<section id="templates"><h2>可编辑SVG版面</h2><p>'+str(len(catalog))+'份选用版面，覆盖'+str(len({x['code'] for x in catalog}))+'种模板代码。这里的条数不是施工数量；名义尺寸可追溯。</p><div class="grid">'+''.join(card(x['code']+' '+x['name'],img(x['path'],'template')+paragraph(str(x['w'])+' × '+str(x['h'])+' mm · '+x['revision'])+'<a href="'+esc(x['path'])+'">SVG源文件</a>') for x in catalog)+'</div></section>')
sections.append('<section id="installation"><h2>材料、固定与更新模块</h2>'+img(figures[2])+paragraph('哑光材料与实际环境匹配；固定节点、可读/更新、内容版次和适用专项分别留证。')+'</section>')
if scene:sections.append('<section id="scenes"><h2>效果示意</h2><p>图像为概念，不能用于量尺寸、计数或证明本厂现状。制作按SVG及具名样牌记录。</p>'+''.join(img(x['path'],'scene') for x in scene)+'</section>')
if cad_svgs:sections.append('<section id="cad"><h2>原图候选与核查证据</h2><p>1F三候选保持；8F图签冲突与物理单位待核，部分实体预览不作施工底图。</p>'+''.join(img(str(x.relative_to(ROOT)),'source') for x in cad_svgs)+'</section>')
downloads=[('output/pdf/BeePump_1F_8F_Implementation_Design_V2.4.pdf','实施交接设计图册'),('output/pdf/BeePump_1F_8F_SettingOut_Acceptance_Forms_V2.4.pdf','现场放样与验收表'),('BeePump_1F_8F_Implementation_V2.4_Source.zip','交实施方的完整源包'),('outputs/implementation_v2.4/specs/floor_work_packages.json','两层需求台账'),('outputs/implementation_v2.4/specs/quotation_scope.csv','分项报价范围'),('outputs/implementation_v2.4/specs/blank_setting_out.csv','空白点位放样CSV'),('outputs/implementation_v2.4/specs/blank_acceptance.csv','空白验收CSV'),('outputs/implementation_v2.4/版面与名义尺寸索引.csv','版面尺寸索引'),('outputs/implementation_v2.4/specs/contractor_readme.md','实施方先读'),('START_HERE.html','项目总入口')]
downloads[4:4]=[('outputs/implementation_v2.4/1F_安装需求与实施接口.csv','1F实施需求CSV'),('outputs/implementation_v2.4/8F_安装需求与实施接口.csv','8F实施需求CSV')]
sections.append('<section id="downloads"><h2>交接文件</h2><div class="downloads">'+''.join('<a href="'+esc(a)+'">'+esc(b)+'</a>' for a,b in downloads)+'</div></section>')
js='''document.querySelectorAll('main img').forEach(x=>{x.tabIndex=0;x.onclick=()=>{document.querySelector('#zoom-image').src=x.src;document.querySelector('#zoom').showModal()};x.onkeydown=e=>{if(e.key==='Enter'){e.preventDefault();x.click()}}});document.querySelector('#close').onclick=()=>document.querySelector('#zoom').close();const filter=document.querySelector('#floor-filter');function update(){let count=0;document.querySelectorAll('.requirement').forEach(x=>{x.hidden=filter.value!=='all'&&x.dataset.floor!==filter.value;if(!x.hidden)count++});document.querySelector('#req-count').textContent=count+'条设计需求（不是实际标牌量）'}filter.onchange=update;update();'''
nav=[('handoff','实施顺序'),('floor1','1F设计'),('floor8','8F设计'),('requirements','安装需求'),('templates','编辑版面'),('installation','固定更新'),('cad','核图证据'),('downloads','交接文件')]
web='<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>BeePump1F8F实施交接设计</title><style>'+webcss+'</style><body><header><div>'+REV+' · '+DATE+'</div><h1>1F + 8F 实施交接设计</h1><p>把两层版面、选面、物流/人流、材料、放样、核量和验收交给同一套记录。输入原件保留，固定结构不移动。</p><p>可开始现场深化与打样 · 实际点位/工程量及制作安装记录待闭合</p></header><main><nav>'+''.join('<a href="#'+a+'">'+b+'</a>' for a,b in nav)+'</nav>'+''.join(sections)+'<footer>BeePump · 1F/8F设计交接 · V2.4 · 现场放样记录与源稿按版本保存</footer></main><dialog id="zoom"><button id="close">关闭大图</button><img id="zoom-image" alt="放大查看"></dialog><script>'+js+'</script></body></html>'
(ROOT/'IMPLEMENTATION_1F_8F.html').write_text(web)
write('outputs/implementation_v2.4/review_manifest.json',{'revision':REV,'date':DATE,'floors':['1F','8F'],'figures':figures,'catalog_count':len(catalog),'template_types':len({x['code'] for x in catalog}),'new_variant_count':len(new),'requirements_count':len(requirements),'design_pages':len(pages),'forms_pages':len(forms),'actual_point_count':None,'actual_coordinates_created':False,'production_release':False,'source_drawing_sha256':SOURCE_SHA})
print(json.dumps({'design_pages':len(pages),'forms_pages':len(forms),'artboards':len(catalog),'requirements':len(requirements),'new_variants':len(new)},ensure_ascii=False))

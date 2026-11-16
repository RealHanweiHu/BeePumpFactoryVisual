#!/usr/bin/env python3
"""Author 15 traceable draft operation template variants; inputs remain immutable."""
from pathlib import Path
import hashlib
import html
import json
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
REV = 'V2.4-IMPLEMENTATION-DRAFT'
DEST = ROOT / 'design/v2/implementation_ops_v2.4'
OUT = ROOT / 'outputs/implementation_v2.4'
DEST.mkdir(parents=True, exist_ok=True)
OUT.mkdir(parents=True, exist_ok=True)
CODES = ['QC-01', 'QC-02', 'QC-03', 'QC-04', 'WF-05', 'WH-02', 'VS-01', 'BT-01', 'BT-02', 'ES-01', 'PM-03', 'FM-01', 'EQ-02', 'BE-03', 'MD-01']
COLORS = {'black':'#000000', 'orange':'#FF6600', 'white':'#FFFFFF', 'gray':'#3E3A39', 'blue':'#005EB8', 'green':'#00864A', 'red':'#D81920', 'yellow':'#F4C400', 'rule':'#C9C9C9', 'light':'#F2F2F2'}
rows = json.loads((ROOT/'data/templates.json').read_text())
if isinstance(rows, dict): rows = rows['templates']
sources = {r['code']:r for r in rows if r['code'] in CODES and r['revision']=='V1.0'}

def esc(s): return html.escape(str(s), quote=True)
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def num(v): return f'{v:.3f}'.rstrip('0').rstrip('.')

class Board:
    def __init__(self, record):
        self.r=record; self.w=record['w']; self.h=record['h']; self.parts=[]
        self.rect(0,0,self.w,self.h,'white')
    def rect(self,x,y,w,h,fill='white',stroke=None,sw=1):
        fill=COLORS.get(fill,fill)
        extra=f' stroke="{COLORS.get(stroke,stroke)}" stroke-width="{num(sw)}"' if stroke else ''
        self.parts.append(f'<rect x="{num(x)}" y="{num(y)}" width="{num(w)}" height="{num(h)}" fill="{fill}"{extra}/>')
    def line(self,x1,y1,x2,y2,color='rule',sw=1):
        self.parts.append(f'<line x1="{num(x1)}" y1="{num(y1)}" x2="{num(x2)}" y2="{num(y2)}" stroke="{COLORS.get(color,color)}" stroke-width="{num(sw)}"/>')
    def text(self,x,y,s,size,fill='black',weight=400,anchor='start'):
        self.parts.append(f'<text x="{num(x)}" y="{num(y)}" font-size="{num(size)}" fill="{COLORS.get(fill,fill)}" font-weight="{weight}" text-anchor="{anchor}">{esc(s)}</text>')
    def header(self,title,en):
        w,h=self.w,self.h; bar=h*.15; m=w*.045
        self.rect(0,0,w,bar,'black'); self.rect(0,0,w*.011,bar,'orange')
        self.text(m,bar*.47,title,bar*.27,'white',700)
        self.text(m,bar*.80,en,bar*.12,'white',500)
        self.text(w-m,bar*.47,self.r['code'],bar*.16,'orange',700,'end')
        return bar,m
    def fields(self,labels,start,gap,m,value_x=None,size=None):
        value_x=value_x if value_x is not None else self.w*.53
        size=size if size is not None else min(self.w*.032,gap*.37)
        for i,(label,value) in enumerate(labels):
            y=start+i*gap
            self.text(m,y,label,size,'gray'); self.text(value_x,y,value,size)
            self.line(m,y+gap*.22,self.w-m,y+gap*.22,sw=max(self.w*.001,0.25))
    def note(self,lines,y,height,m,size):
        self.rect(m,y,self.w-2*m,height,'light')
        for i,s in enumerate(lines): self.text(m+self.w*.018,y+size*1.6+i*size*1.55,s,size,'black',700 if i==0 else 400)
    def footer(self,text='评审稿 · 内容、适用范围与安装待批准'):
        size=min(self.w*.014,self.h*.022)
        self.text(self.w*.045,self.h-size*.5,text,size,'gray')

reasons={}
boards={}
for code in CODES:
    b=Board(sources[code]); w,h=b.w,b.h
    if code.startswith('QC-'):
        states={
            'QC-01':('待检','PENDING INSPECTION','blue','white',['禁止默认投入下一工序。','转序检验须有批准任务。']),
            'QC-02':('已放行','RELEASED','green','white',['仅在放行记录范围内流转。','状态变化须重新确认。']),
            'QC-03':('不合格','NONCONFORMING','red','white',['退出正常流转，联系品质。','返工 / 退货 / 报废分别审批。']),
            'QC-04':('冻结 / 待处理','HOLD','yellow','black',['暂停正常流转，核实冻结原因。','解除须有授权记录。'])}
        title,en,color,ink,actions=states[code]
        b.rect(0,0,w,19,color); b.text(5,9,title,5.3,ink,700); b.text(5,15,en,2.6,ink,700)
        b.text(95,15,code,2.5,ink,700,'end')
        b.fields([('容器ID / 批次','待填'),('数量 / 单位','待填'),('物料版本 / 工序','待填'),('授权人 / 时间','待填')],24,5.7,5,54,2.45)
        b.note(actions,46,12,5,2.35)
        b.text(5,62,'依据 / 记录ID：待填',2.4)
        b.text(5,67,'评审稿 · 质量状态不赋予通行优先',1.8,'gray')
        reasons[code]=['保持原蓝/绿/红/黄质量语义及中文/英文识别','用明确动作和放行适用范围替代可否流转自由填空','卡物一致；批次、数量、授权及记录留真实待填，不合成批准','状态不等于车辆或人员通行优先']
    elif code=='WF-05':
        b.header('支持房间门牌','ROOM IDENTITY')
        b.text(18,74,'房间名称待填',26,'black',700)
        b.fields([('楼层 / 区域','待核'),('责任人 / 联系','待填'),('使用 / 准入要求','按批准文件填写')],104,22,18,188,9)
        b.footer(); reasons[code]=['保留支持房间身份、区域与责任功能','移除未经确认的治具室、8F及示例区域码','房名、准入与联系方式按真实台账填写，无方向箭头']
    elif code=='WH-02':
        b.rect(0,0,w,h,'black'); m=42
        b.text(m,78,'楼层 / 区域待核',35,'orange',700)
        b.text(m,205,'排号待填',105,'white',700)
        b.line(m,251,w-m,251,'orange',4)
        b.text(m,325,'货架用途待填',57,'white',700)
        b.text(m,373,'RACK IDENTITY / PENDING',20,'white')
        b.text(m,475,'列 / 层范围：待填',38,'white',700)
        b.text(m,558,'精确库位：查 WH-01',28,'white')
        b.text(m,690,'方向待现场核验',44,'white',700)
        b.text(m,758,'方向核验记录 / 责任人：待填',23,'white')
        b.text(m,848,'评审稿 · 未核方向不得制作安装',18,'white')
        reasons[code]=['移除5F、B-03、01-04列和未核方向箭头','排号远读，精确库位转查WH-01，保留端头查找层级','货架用途、范围和方向记录依现场台账填写']
    elif code=='VS-01':
        bar,m=b.header('6S责任区','6S OWNERSHIP')
        b.fields([('区域 / 边界','待核'),('责任人 / 代理','待填'),('检查频次 / 依据','待批准'),('本次检查 / 记录','待填')],bar+25,27,m,157,9)
        b.rect(m,188,w-2*m,99,'light','rule',0.5)
        b.text(w/2,224,'经批准的现场标准照片',10,'gray',700,'middle')
        b.text(w/2,245,'照片 / 定置图编号待填',8,'gray',400,'middle')
        b.text(w/2,266,'不以概念效果图代替现场标准',7.5,'gray',400,'middle')
        b.fields([('未关闭问题 / 记录ID','待填'),('接手人 / 下次确认','待填')],316,27,m,174,8)
        b.note(['清扫发现异常也要登记。','安全危险按批准预案立即报告。'],365,33,m,7.5)
        b.footer(); reasons[code]=['移除8F-A实例与虚构检查日期','标准照片仅用批准的现场照片，保留责任/检查/未关闭问题','增加问题接手与下一次确认，评分不能替代闭环']
    elif code=='BT-01':
        bar,m=b.header('电池暂存管理信息','BATTERY PACK STAGING INFORMATION')
        b.text(m,bar+43,'完整外采电池包 · 专项适用范围待批准',21,'black',700)
        b.fields([('型号 / 规格 / 来源','待填'),('允许状态 / 用途','待专项批准'),('实际区域 / 边界','待专项核定'),('批准数量 / 能量上限','待批准，未填不构成许可'),('实际数量 / 能量 / 时间','待现场记录'),('适用存运条件 / 文件','待填批准文件编号'),('专项批准文件 / 版本','待填'),('负责人 / 联系 / 代理','待填')],bar+93,49,m,298,16)
        b.note(['本牌仅展示已批准的存运条件。','型号、状态、设施或数量条件改变须复审。','未知状态停止投入，联系专项责任人。'],645,103,m,17)
        b.text(m,787,'异常仅按现场批准预案及责任体系处理。',17,'black',700)
        b.footer('评审稿 · 不确定储存地点、容量、消防配置或异常电池搬运方法')
        reasons[code]=['明确完整外采电池包，不假设电芯制造或电池上楼获批','不填虚构数量、能量、温度、SOC、时长或存运许可','专项文件与负责人为独立审批接口','不提供水桶、浸泡、异常搬运或灭火步骤；仅引用现场批准预案']
    elif code=='BT-02':
        bar,m=b.header('老化格位卡','AGING SLOT RECORD')
        b.text(m,bar+11,'仅适用已批准的真实老化工艺',3.8,'black',700)
        b.fields([('实际格位 / 设备ID','待填'),('产品版本 / 容器批次','待填'),('批准程序 / 版本','待填'),('开始 / 预计完成','按程序记录'),('周期状态 / 异常记录','待填'),('质量结论 / 放行记录','由授权品质填写')],bar+26,13.4,m,110,3.6)
        b.note(['周期完成不等于质量放行。','暂停 / 断电 / 异常 / 复测保留原记录。'],122,17,m,3.4)
        b.footer(); reasons[code]=['移除8F-C-R01-01假格位及假测试时间','适用工艺、设备与程序须先批准；格位为真实身份','周期状态与质量结论分开，异常和复测保留完整记录']
    elif code=='ES-01':
        bar,m=b.header('电子装配区进入确认','EPA ENTRY INFORMATION')
        b.text(m,bar+43,'仅适用经企业确认的 EPA 受控区域',23,'black',700)
        labels=[('适用依据','EPA边界 / 敏感器件 / 方案版本待批准'),('人员确认','按适用方案核验真实人员测试与授权'),('物料确认','按适用方案核验包装与器件状态'),('工位确认','按适用方案核验设施、工具和点检记录'),('异常接手','确认失败暂停受控作业，联系责任人')]
        for i,(title,desc) in enumerate(labels):
            y=231+i*90
            b.text(m,y,title,24,'orange',700); b.text(m,y+34,desc,16)
            b.line(m,y+49,w-m,y+49,sw=0.8)
        b.fields([('负责人 / 联系方式','待填'),('确认记录 / 文件','待填')],707,42,m,318,17)
        b.footer('评审稿 · 不证明 EPA 已建成，不要求所有人风淋，不代替 ESD 工程设计')
        reasons[code]=['移除8F/SMT实例和假定两条线','先有真实EPA适用授权，再列人员/物料/工位进入确认','不证明EPA设施合格，不默认要求所有员工或访客风淋','仅管理信息，安全图形与设施测试依据由专业方案确定']
    elif code=='PM-03':
        bar,m=b.header('异常响应看板','ABNORMALITY RESPONSE / TASK HANDOFF')
        b.text(m,bar+52,'异常发现、任务接手与恢复确认',34,'black',700)
        titles=[('发现 / 登记','记录对象、时间、影响与问题ID'),('确认接单','记录接手角色、联系与下一次确认'),('受控措施','引用已批准措施、范围及效果记录'),('恢复确认','按职责核条件、质量影响和批准记录')]
        cw=(w-2*m)/4
        for i,(title,desc) in enumerate(titles):
            x=m+i*cw
            b.text(x,233,title,26,'orange',700)
            parts=[desc[:11],desc[11:]]
            for j,part in enumerate(parts):
                if part: b.text(x,274+j*27,part,19)
        b.fields([('对象 / 区域 / 问题ID','待填'),('首次发现 / 记录人','待填'),('接手人 / 下一次确认','待填'),('措施 / 条件 / 依据','待填批准文件或记录'),('恢复决定 / 授权记录','待真实授权记录')],382,48,m,570,22)
        b.note(['电池安全异常不进入普通返修/补料路线。','即时风险按现场批准预案报告；本板不定义处置动作。'],608,48,m,17)
        b.footer('评审稿 · 不改设备按钮、灯态、电气控制或停机保护逻辑')
        reasons[code]=['删除L01假生产线身份以及绿黄红灯态施工暗示','异常任务接手、下一次确认与恢复依据可追溯','保留授权职责，不能通过看板合成复机/放行批准','即时风险与电池安全异常按现场专项预案处理，不提供操作处置']
    elif code=='FM-01':
        bar,m=b.header('地面定置规则评审','FLOOR MARKING RULE REVIEW')
        b.text(m,bar+48,'本页是规则评审牌面，不是地面放样施工图',28,'black',700)
        data=[('通行与交叉','人车路径、入口、转弯、候行条件待现场专项确认'),('物料定位','真实容器外廓、取放、满位停止与接收接口待核'),('固定设备边界','检修、开门、散热、吊装与操作范围待工程确认'),('质量状态','蓝待检 / 绿放行 / 红不合格 / 黄冻结；词义须保留'),('批准地面施工','颜色 / 线型 / 线宽 / 坐标 / 材料按批准专项图执行')]
        for i,(title,desc) in enumerate(data):
            y=243+i*84
            b.text(m,y,title,26,'black',700); b.text(m,y+37,desc,23)
            b.line(m,y+51,w-m,y+51,sw=1)
        b.note(['品牌橙仅用于本牌面，绝不用于地面线。','质量颜色不赋予通行优先；安全图形使用专项批准资源。'],667,63,m,22)
        b.footer('评审稿 · 现有结构和安全出口不改；实测、专项审查后另发地面图')
        reasons[code]=['保留通行、定位及质量语义评审，取消可被误当施工图的色线示例','增加黄色冻结词义，不让质量色指定行车优先','无橙色地面线、无新安全图形，无假路宽/线宽/放样坐标','施工颜色、材料及真实边界待现场专项批准图确定']
    elif code=='EQ-02':
        bar,m=b.header('工装 / 量具','TOOL & GAUGE IDENTITY')
        b.fields([('永久工具ID / 名称','待填'),('适用机型 / 版本','待确认'),('检验依据 / 记录','待填真实文件'),('适用状态 / 到期','查有效记录'),('管理人 / 联系','待填')],bar+11,11,m,88,3.4)
        b.note(['逾期、状态不明或变更：暂停使用。','联系品质 / 工程；本牌不证明检验合格。'],80,12,m,2.9)
        b.footer(); reasons[code]=['真实工具身份与适用版本独立，不填虚構TG编号','检验、校准/检定依据及有效状态查真实记录','不将未填状态打印为已合格，逾期和不明状态暂停使用']
    elif code=='MD-01':
        bar,m=b.header('模具状态牌','MOLD STATUS')
        b.rect(m,bar+10,w-2*m,22,'light')
        b.text(w/2,bar+24,'状态待确认',7,'black',700,'middle')
        b.fields([('永久模具ID','待填'),('产品 / 版本','待填'),('所在机台 / 库位','待核'),('累计模次 / 依据','待填'),('保养 / 维修记录','待填'),('试模 / 变更记录','待填'),('接手人 / 时间','待填')],bar+47,11.8,m,57,3.1)
        b.note(['仅实际且授权的模具作业适用。','未确认或待修不混入待用。'],155,15,m,2.8)
        b.footer('可选评审稿 · 吊挂点须批准，不妨碍起吊')
        reasons[code]=['保留永久模具身份、可用性、位置和维护交接功能','状态待真实确认；试模、保养、待修与封存按实际制度区分','实际模具作业存在且授权后才实例化，不是必装数量','挂点由现场工程批准，不能挂受力吊环内妨碍起吊']
    elif code=='BE-03':
        b.rect(0,0,w,h,'black'); m=180
        b.text(m,245,'制造文化',170,'white',700)
        b.text(m,405,'用可核验的过程、追溯与改善形成内容',85,'white',500)
        b.text(m,501,'内容编辑提案 · 对客文案与证据待批准',45,'orange',700)
        topics=[('真实工艺','受控工艺 / 版本 / 现场图','真实内容待审核'),('质量追溯','检验依据 / 放行记录','可公开证据待批准'),('6S改善','问题 / 措施 / 复核证据','真实改善案例待审核'),('客户验证','授权需求 / 验证证据','客户授权与披露待批准')]
        cw=(w-2*m)/4
        for i,(title,evidence,blank) in enumerate(topics):
            x=m+i*cw
            b.text(x,730,title,88,'white',700); b.line(x,796,x+cw-65,796,'orange',7)
            b.text(x,927,evidence,42,'white')
            b.text(x,1040,blank,42,'white')
            b.text(x,1161,'真实图 / 记录编号：待填',36,'white')
            b.text(x,1260,'内容责任 / 批准：待填',36,'white')
            b.text(x,1359,'复审条件 / 日期：待填',36,'white')
        b.text(m,1591,'每项内容保留来源、披露许可与复审记录。',51,'white',700)
        b.text(m,1714,'评审稿 · 不展示未经核实的年份、奖项、客户标识、认证或业绩',36,'white')
        reasons[code]=['保留制造文化用途，移除未核Since1994及历史宣称','工艺、质量追溯、6S改善、客户验证形成四类真实内容接口','对客披露、图片许可、内容责任与复审记录独立确认','不合成证书、奖项、客户Logo、生产业绩或员工历史']
    boards[code]=b

manifest=[]
for code in CODES:
    b=boards[code]; r=sources[code]; source=ROOT/r['path']
    orig=[''.join(e.itertext()) for e in ET.parse(source).iter() if e.tag.split('}')[-1]=='text']
    stem=f"{code}_{r['name']}_{REV}"
    svgpath=DEST/(stem+'.svg'); side=DEST/(stem+'.sidecar.json')
    meta={'schema_version':'1.0','code':code,'name':r['name'],'revision':REV,'created_date':'2026-10-07','drawing_status':'template_only','approval_status':'not_for_production','production_release':False,'source_path':r['path'],'source_sha256':sha(source),'original_text_preserved_in_metadata':orig,'physical_size_mm':[b.w,b.h],'physical_size_source':'V1 nominal suggested template size; not an installation measurement','font_sizes_are_nominal_em_mm':True,'printed_font_and_installation_height':'not verified; 1:1 print sample and site approval required','decision':'Refine','change_reasons':reasons[code],'scope':'optional; instantiate only if actual mold operations exist and are authorized' if code=='MD-01' else 'applicability subject to approved actual operational workflow','actual_point_id':None,'actual_floor_id':None,'area_id':None,'world_position':None,'actual_coordinates':None,'facing':None,'installation_height_mm':None,'installed_quantity':None,'approved_quantity':None,'content_approval':None,'installation_approval':None,'specialist_approval':None,'source_render_png':f'reports/implementation_operations_render/v1/{code}.png','render_png':f'reports/implementation_operations_render/{code}.png'}
    xml=(f'<svg xmlns="http://www.w3.org/2000/svg" width="{b.w}mm" height="{b.h}mm" viewBox="0 0 {b.w} {b.h}" role="img" aria-labelledby="title desc">\n<title id="title">{esc(code+" "+r["name"]+" "+REV)}</title>\n<desc id="desc">评审模板，未知资料待填，无安装点或批准；名义牌面尺寸复用V1。</desc>\n<metadata>{esc(json.dumps(meta,ensure_ascii=False))}</metadata>\n<g font-family="PingFang SC, Microsoft YaHei, Noto Sans CJK SC, Arial, sans-serif">\n'+ '\n'.join(b.parts)+'\n</g>\n</svg>\n')
    svgpath.write_text(xml)
    side.write_text(json.dumps(meta,ensure_ascii=False,indent=2)+'\n')
    record={**meta,'w':b.w,'h':b.h,'path':str(svgpath.relative_to(ROOT)),'sidecar_path':str(side.relative_to(ROOT)),'svg_sha256':sha(svgpath),'sidecar_sha256':sha(side)}
    manifest.append(record)
(OUT/'operations_template_manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
lines=['# V2.4 操作类牌面逐项审查','',f'版本：{REV}。创建日期：2026-10-07。15 款变体保留 V1 编号、名称、名义尺寸及业务功能；MD-01 是可选模具作业接口。原输入完整保留，TEXT 全文和 SHA-256 存于每张 SVG metadata、侧车与 manifest。','', '## 审查原则','', '先查看原渲染，再按任务改版。品牌橙只用于牌面；质量状态保留原蓝/绿/红/黄及中文动作。所有未知业务值待填/待核/待批准；安装点、坐标、朝向、高度、数量与批准为 null。无二维码、虚构历史、容量或假检验合格。','', '| 代码 | 原目标与保留项 | 定向完善 | 尺寸 mm |', '|---|---|---|---|']
for m in manifest:
    r=sources[m['code']]
    lines.append(f"| {m['code']} | {r['spec']['goal']} | {'；'.join(m['change_reasons'])} | {m['w']} × {m['h']} |")
lines += ['', '## 阅读与实施接口','', '质量卡与工具牌是近距离操作卡，先打印 1:1 小样核字高、耐擦写、卡物一致及单个有效状态；货架牌是排号远读、精确库位近读；门牌支持身份与准入；6S及专项信息牌在各自已批准的功能接口读；异常板用于任务接手；文化墙由真实证据编排。小样印刷字号不等于现场阅读通过，材质、反光、光照与安装位置需现场复核。', '', 'BT-01 仅完整外采电池包已批准存运条件的信息接口；BT-02 仅真实适用老化工艺；ES-01 必须先有企业 EPA 适用授权；PM-03 不改变电气控制；FM-01 仅规则评审，施工地面专项另发；BE-03 不使用未核实年份与认证。', '', '## 渲染证据','', '原图：`reports/implementation_operations_render/v1/`；新版：`reports/implementation_operations_render/`。渲染 QA 记录在 `render_qa.json`，人工像素审阅另记于 `pixel_review.md`。']
(OUT/'operations_template_review.md').write_text('\n'.join(lines)+'\n')
print(json.dumps({'templates':len(manifest),'manifest':'outputs/implementation_v2.4/operations_template_manifest.json','codes':CODES},ensure_ascii=False))

"""Generate editable pilot artboards, preserving immutable V1 inputs."""
from pathlib import Path
import json, html, copy, csv, hashlib
ROOT=Path(__file__).resolve().parents[1]
REV='V2.1-DRAFT'
O='#FF6600';K='#000000';W='#FFFFFF';G='#3E3A39'
FONT='Noto Sans CJK SC, Source Han Sans SC, PingFang SC, Microsoft YaHei, sans-serif'
def esc(s):return html.escape(str(s),quote=True)
def rect(x,y,w,h,fill=W,stroke=None,sw=1,opacity=1):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{fill}"'+(f' stroke="{stroke}" stroke-width="{sw}"' if stroke else '')+f' opacity="{opacity}"/>'
def text(x,y,s,size=20,fill=K,weight=400,anchor='start',field=None):
    return f'<text x="{x}" y="{y}" font-size="{size}" fill="{fill}" font-weight="{weight}" text-anchor="{anchor}"'+(f' data-field="{field}"' if field else '')+f'>{esc(s)}</text>'
def line(x1,y1,x2,y2,fill=G,sw=1,opacity=.3):return f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{fill}" stroke-width="{sw}" opacity="{opacity}"/>'
def header(w,title,en,context,size=72):
    return rect(0,0,w,185,K)+rect(0,0,14,185,O)+text(60,94,title,size,W,700)+text(64,148,en,25,W)+text(w-60,100,context,31,O,600,'end')
def blank(x,y,label,width=280,size=30):return text(x,y,label,size,G)+line(x,y+54,x+width,y+54)+text(x,y+43,'待填',size,G,400,field=label)
registry=json.loads((ROOT/'data/templates.json').read_text())
v1=[t for t in registry if t['revision']=='V1.0']
lookup={t['code']:t for t in v1}
target=['WF-02','WF-04','WH-01','PM-01','PM-02','FL-01']
out=ROOT/'design/v2';out.mkdir(parents=True,exist_ok=True)
art={}
art['WF-02']=rect(0,0,1200,400,K)+text(130,84,'8F',54,W,700,'middle')+'<polygon points="130,115 207,160 207,250 130,295 53,250 53,160" fill="#FF6600"/>'+text(130,239,'A',100,K,700,'middle')+line(250,44,250,330,W,1,.3)+text(300,171,'成品组装区',78,W,700,field='area_name')+text(304,240,'FINAL ASSEMBLY',28,W,500)+line(304,274,1138,274,O,4,1)+text(304,336,'8F-A',35,O,700)+text(1138,335,'正式Logo待确认',16,W,400,'end')+text(60,382,'8F / A区为方案基线，待与图纸映射确认',13,W)
art['WF-04']=rect(0,0,360,1100,W)+rect(0,0,360,272,K)+rect(0,0,10,272,O)+text(180,192,'8F',138,O,700,'middle')+text(30,379,'A区',66,K,700)+text(30,465,'成品组装',45,K,700)+text(32,510,'FINAL ASSEMBLY',16,G,500)+line(30,550,330,550,O,3,1)+text(30,618,'区域 / AREA',18,G)+text(30,694,'8F-A',61,K,700)+text(30,792,'柱号 / COLUMN',18,G)+text(30,846,'P-待填',31,K,600,field='column_id')+text(30,936,'朝向按图纸与现场确认',20,G)+rect(0,980,360,120,K)+text(30,1034,'WF-04 / 位置识别草案',20,W,600)+text(30,1075,'不以区域号替代永久柱号',16,W)
art['WH-01']=rect(0,0,200,100,W,K,.6)+rect(0,0,200,18,K)+rect(0,0,3,18,O)+text(8,12,'库位 / LOCATION',7,W,600)+text(8,42,'8F-A-__-__-__',15,K,700,field='location_id')+text(8,52,'楼层 / 区 / 排 / 列 / 层',5.5,G)+line(8,59,144,59)+text(8,69,'容量 / 载荷：批准后填写',5.6,K)+text(8,82,'物料、批次使用可换卡',5.5,G)+text(8,93,'编码结构示意，非已登记库位',4.5,G)+rect(152,28,38,38,W,G,.4)+text(171,44,'编码待生成',4.3,G,500,'middle')+text(171,54,'非扫码图',4.3,G,400,'middle')+text(171,77,'库位ID一致后',4.3,G,400,'middle')+text(171,86,'再生成并实扫',4.3,G,400,'middle')
a=header(2400,'生产运行看板','PRODUCTION CONTROL','8F-A / 线号待填')
for i,(label,sub) in enumerate([('计划合格产出','锁定计划 / 版次待填'),('实际合格产出','同工序、同时段、同计量单位'),('累计差异','实际 - 计划')]):
    x=60+i*555
    a+=rect(x,225,520,278,G,opacity=.055)+text(x+28,274,label,36,K,600)+text(x+28,407,'待填',104,K,600,field=['planned','actual','variance'][i])+text(x+28,472,sub,25,G)
a+=text(1780,273,'当前工单 / 产品版本',32,K,600)+text(1780,325,'待填 / Rev.待填',34,G,field='work_order')+line(1780,347,2340,347)+text(1780,393,'班次 / 更新人 / 更新时间',28,K)+text(1780,445,'待填 / 待填 / 待填',30,G,field='update_time')
a+=text(60,575,'时段进度',42,K,700)+text(1270,575,'异常接单与下一步',42,K,700)
xs=[60,320,520,720,900,1180];labs=['时段','计划','实际','差异','原因']
a+=rect(60,610,1120,62,G,opacity=.07)
for x,l in zip(xs,labs):a+=text(x+14,652,l,28,K,600)
for row in range(4):
    y=710+row*77
    for x,s in zip(xs,['__:__','待填','待填','待填','待填']):a+=text(x+14,y,s,26,G)
    a+=line(60,y+22,1180,y+22)
a+=rect(1270,610,1070,62,G,opacity=.07)
for x,l in zip([1285,1570,1770,2070],['事件 / 首次时间','接手人','下一步','预计完成']):a+=text(x,652,l,27,K,600)
for row in range(3):
    y=716+row*82
    for x in [1285,1570,1770,2070]:a+=text(x,y,'待填',27,G)
    a+=line(1270,y+24,2340,y+24)
a+=line(60,1030,2340,1030,O,4,1)
for x,l,s in [(60,'首件 / 换型','批准记录：待填'),(635,'一次通过率','首次通过 / 首检总数：待填'),(1210,'WIP / 批准上限','当前 / 上限 / 单位：待填'),(1785,'安全 / 6S','未闭环问题：待填')]:a+=text(x,1087,l,29,K,600)+text(x,1130,s,25,G)
a+=text(60,1180,'无数据保持待填；差异 = 实际 - 计划；更新延迟须显示原因，不显示假正常。',21,G)
art['PM-01']=a
a=header(2400,'班组日常管理','SQDCP / DAILY MANAGEMENT','8F / 班组待填')
cols=[('S','安全','隐患闭环 / 防护点检'),('Q','品质','首次通过 / 缺陷闭环'),('D','交付','锁定计划 / 待交工单'),('C','成本','报废金额 / 返工工时'),('P','人员','关键工位 / 授权覆盖')]
for i,(letter,title,desc) in enumerate(cols):
    x=60+i*466
    a+=text(x,315,letter,105,K,700)+text(x+113,305,title,47,K,700)+line(x,347,x+408,347,O,4,1)+text(x,400,desc,26,G)
    for y,l in [(465,'口径 / 周期'),(555,'目标 / 单位'),(645,'当前 / 趋势'),(735,'更新人 / 时间')]:
        a+=text(x,y,l,24,G)+text(x,y+40,'待填',30,K,500,field=letter+'_'+l)+line(x,y+57,x+408,y+57)
a+=text(60,856,'跨部门行动清单',40,K,700)+text(2340,850,'风险、责任、期限、验证证据一起闭环',24,G,400,'end')+rect(60,884,2280,57,G,opacity=.07)
for x,l in zip([76,620,970,1310,1740],['问题 / 类别','接手人','临时措施','到期 / 下一步','验证证据 / 状态']):a+=text(x,923,l,28,K,600)
for y in [996,1081]:
    for x in [76,620,970,1310,1740]:a+=text(x,y,'待填',27,G)
    a+=line(60,y+27,2340,y+27)
a+=text(60,1176,'阈值经批准后使用颜色提示；报废金额与返工工时分列；个人评价不朝向访客。',22,G)
art['PM-02']=a
a=rect(0,0,600,450,W,K,1)+rect(0,0,600,88,K)+rect(0,0,5,88,O)+text(24,43,'在制品限量',31,W,700)+text(25,70,'WIP LIMIT / FIFO',12,W)+text(576,43,'8F-A → 8F-C',16,O,600,'end')+text(576,70,'工序关系待核',10,W,400,'end')
a+=text(25,126,'当前占用',18,G)+text(316,126,'批准上限',18,G)+text(25,182,'待填',44,K,700,field='wip_current')+text(316,182,'待批准',44,K,700,field='wip_limit')+line(285,111,285,204)+text(25,213,'计量单位：待核（车 / 箱 / 件分开记录）',14,G)
a+=text(25,254,'每容器标准数量：待填',15,K)+text(316,254,'批准依据 / 版次：待填',14,K)+text(25,286,'允许物料 / 版本：待填',15,K)+text(316,286,'更新人 / 时间：待填',14,K)
a+=rect(24,313,552,70,K)+text(40,344,'满位：停止继续投放，通知班组长',20,W,700)+text(40,370,'取料：按已放行批次与先后顺序执行',14,W)
a+=text(25,414,'冻结品退出正常FIFO；未批准上限不作为增加暂存许可。',12,G)+text(25,438,'FL-01 / 上限、容器与现场容量共同复核',10,G)
art['FL-01']=a
changes={
 'WF-02':['楼层与区域独立，主功能字增大，英文退为辅助','保留尖角蜂巢A；取消装饰性背景；Logo保持待确认'],
 'WF-04':['移除未经位置核查的箭头','区域与永久柱号分列，远读8F、近读柱号'],
 'WH-01':['替换5F示例为8F编码结构占位','库位码留完整白区；明确非扫码图，保留容量与可换卡边界'],
 'PM-01':['删除示例1200/1080/-120和固定日期','三项核心产出独立；时段差异与异常队列分开'],
 'PM-02':['保持SQDCP五项职责与行动清单','增加口径/周期/单位，成本金额与工时分列'],
 'FL-01':['删除示例3车/20台','并列当前与批准上限；保留满位停投和放行FIFO动作']}
meta=[]
for code in target:
    t=lookup[code];src=ROOT/t['path'];w=t['w'];h=t['h']
    import xml.etree.ElementTree as ET
    original=list(ET.parse(src).getroot().itertext())
    m={'code':code,'revision':REV,'status':'proposal_pending_review','physical_size_mm':[w,h],'viewbox_units':'1 SVG user unit = 1 mm','source_path':t['path'],'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'original_text_preserved_in_metadata':original,'changes':changes[code],'font_stack':FONT,'font_files_distributed':False,'nominal_font_sizes_are_em_mm':True,'printed_ink_height_and_reading_distance':'Verify at 1:1 under real lighting; not approved by web preview','area_ids':'8F-A and 8F-C are baseline mappings, not confirmed DWG placements','installation_height_mm':None,'quantity_installed':None,'approvals':{'content':None,'location':None,'installation':None},'qr_status':'not_generated' if code=='WH-01' else 'not_applicable'}
    filename=f'{code}_{t["name"]}_{REV}.svg';path=out/filename
    svg=f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}mm" height="{h}mm" viewBox="0 0 {w} {h}" role="img" aria-labelledby="title desc"><title id="title">{esc(code+" "+t["name"]+" "+REV)}</title><desc id="desc">评审草案；不是施工放行稿。{esc("；".join(changes[code]))}</desc><metadata id="beepump-revision">{esc(json.dumps(m,ensure_ascii=False))}</metadata><g font-family="{FONT}" style="font-variant-numeric:tabular-nums">{art[code]}</g></svg>'
    path.write_text(svg);m['path']=path.relative_to(ROOT).as_posix();meta.append(m)
    companion={**m,'template_code':code,'source_v1_sha256':m['source_sha256'],'physical_width_mm':w,'physical_height_mm':h,'authoring_notes':changes[code],'content_review':'pending_owner_and_department_review','render_evidence':[f'reports/v2_render/{code}.png','reports/v2_render_qa.json']}
    path.with_suffix('.meta.json').write_text(json.dumps(companion,ensure_ascii=False,indent=2))
    row=copy.deepcopy(t);row.update(path=m['path'],revision=REV,drawing_status='pilot_draft',approval_status='not_for_production',source='V1 SVG + source audit; V2 pilot refinement',note='；'.join(changes[code]));registry=[r for r in registry if (r['code'],r['revision'])!=(code,REV)];registry.append(row)
(ROOT/'data/templates.json').write_text(json.dumps(registry,ensure_ascii=False,indent=2))
(out/'revision_manifest.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2))
print(f'Generated {len(meta)} editable pilot SVGs; V1 inputs preserved')

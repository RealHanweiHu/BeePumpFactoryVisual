"""Build source-label review and relative mounting decisions, never real sign coordinates."""
from pathlib import Path
import json,csv,html,hashlib,shutil,base64,xml.etree.ElementTree as ET
R=Path(__file__).resolve().parents[1]
O=R/'outputs/installation_review';O.mkdir(parents=True,exist_ok=True)
def esc(s):return html.escape(str(s),quote=True)
def save(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
scenes=[
 {'id':'entry','filename':'C02_C03_区域吊牌与柱牌.png','generated_source':'exec-2238ee53-897b-4a31-a463-5c8cb5793b0b.png','title':'C02 / C03 区域吊牌与柱牌','caption':'吊牌面向主要进入视线；柱牌面向通行进路。吊点、柱面、净空和安装高度由现场选定。','references':['WF-02','WF-04']},
 {'id':'boards','filename':'C04_C05_生产与班组管理墙.png','generated_source':'exec-5a7b660a-9230-41bf-9670-757d3cfad048.png','title':'C04 / C05 生产运行与班组管理墙','caption':'当班更新与日会行动分工明确。墙前停留和可达性须现场核查；图片中桌椅并非确认采购或安装。','references':['PM-01','PM-02']},
 {'id':'logistics','filename':'C06_C07_库位与WIP牌.png','generated_source':'exec-9e065f5c-cae0-446f-bb4e-cd5052c9fe5e.png','title':'C06 / C07 线边库位与段间WIP','caption':'库位标签跟随固定地址；WIP牌须对应待现场核实并获批准的缓冲位。容器仅为道具，上限/数量待核；二维码未生成。','references':['WH-01','FL-01']},
]
for s in scenes:
 src=R.parent/'generated_images'/s['generated_source'];dest=O/s['filename']
 if dest.exists():assert sha(dest)==sha(src),'Existing image differs; preserve it and version the filename'
 else:shutil.copy2(src,dest)
 s.update(path=dest.relative_to(R).as_posix(),sha256=sha(dest),type='AI_generated_concept_not_site_photo',tool='built_in_image_gen',physical_layout_confirmed=False)

rows=[
 ('C01',['BE-02','WF-01'],'到层入口识别与导览','实际人行到层入口之后、进入作业区之前的可用实体墙面','面向主要到达人流；先选真实入口，不默认任何电梯为唯一入口','楼层身份与正式品牌确认后固定；导览可换版，箭头待真实路线确认','入口、门扇、墙体可固定性与正式Logo','行政 / 销售 / 工程',['I-8F-01','I-8F-02']),
 ('C02',['WF-02'],'装配区域吊牌','实际装配区域入口上方的专用支架或经核实吊挂结构','主要进入方向能正面看见；第二进路有需求时再评审双面','固定品牌与识别；区域名/码确认后实例化，工程核固定和防坠','区域边界、进路、吊点承载与净空；不直接以管线/线槽作吊点','生产 / 工程',['I-8F-03']),
 ('C03',['WF-04'],'区域定位柱牌','区域入口附近的实际柱面；永久柱号单独保留','面向实际主进路的柱面；不加未经核实的箭头','按柱面条件选底板/夹具；不私自钻柱，区域与柱号分列','真实柱号、防火保护、柱面固定条件与遮挡','生产 / 工程',['I-8F-04']),
 ('C04',['PM-01'],'生产运行更新点','对应真实产线的班组长更新点墙面或经核查板架','须现场验证全部更新字段可达；操作人员在正常进路可查看','固定表头＋可擦写/可换卡；工单、班次、产出、异常与更新时间更新','产线边界、墙面、更新可达性、设备操作及检修空间','生产 / PMC / 品质',['I-8F-05']),
 ('C05',['PM-02'],'班组日会管理点','可停留讨论的独立管理墙或板架；可与C04相邻','面向真实日会站位；会议不占通行位置','固定SQDCP表头＋可换指标与行动卡；保留口径、责任和验证证据','实际站位、停留条件、指标/行动卡更新可达性、墙面与人员信息展示边界','生产 / 品质 / 工程',['I-8F-06']),
 ('C06',['WH-01'],'线边固定库位','待现场核实并获批准的货架横梁、库格或固定地址面','面向实际存取、盘点及扫描方向','可换标签轨/卡槽；库位ID固定，物料/批次另卡；真实ID绑定后生成QR','货架清单、系统编码、载荷批准、反光与扫码可达性','仓库 / 系统管理员',['I-8F-07']),
 ('C07',['FL-01'],'段间WIP缓冲','待现场核实并获批准的段间缓冲架/位旁独立可读面','先面向上游投料者；取料侧FIFO说明按真实进路复核','固定动作规则＋当前量可更新卡；上限和单位批准后填写','工序关系、缓冲边界、上限单位与批准依据，不能从图片计数','生产 / 物流 / 安全',['I-8F-14']),
]
decisions=[]
for c,codes,n,surface,view,update,check,owner,intents in rows:
 decisions.append({'review_id':c,'template_codes':codes,'name':n,'recommended_relative_surface':surface,'reading_direction_description':view,'mounting_and_update_proposal':update,'site_checks_needed':check,'owner_roles':owner,'linked_intents':intents,'record_type':'relative_selection_review_not_installation_point','status':'pending_site_confirmation','floor_candidate':'8F','floor_identity_confirmed':False,'area_id':None,'point_id':None,'position_world':None,'facing_degrees':None,'quantity':None,'faces':None,'installation_height_mm':None,'approved_material_spec':None,'approvals':{'content':None,'location':None,'installation':None,'safety_when_applicable':None}})
save(O/'安装选址评审台账.json',decisions)
with (O/'安装选址评审台账.csv').open('w',encoding='utf-8-sig',newline='') as f:
 w=csv.writer(f);w.writerow(['评审组合ID','模板','对象','建议相对承载面','观看方向','固定与更新建议','待现场核查','责任角色','真实点位ID','CAD安装坐标','朝向角','安装高度mm','实物件数','状态'])
 for d in decisions:w.writerow([d['review_id'],' / '.join(d['template_codes']),d['name'],d['recommended_relative_surface'],d['reading_direction_description'],d['mounting_and_update_proposal'],d['site_checks_needed'],d['owner_roles'],'','','','','','待现场确认；不是实际点位'])

labels=json.loads((R/'outputs/drawings/cad_texts.json').read_text());byhandle={t['handle']:t for t in labels}
source_specs=[
 ('S01','F0A17','合用前室','到层入口须现场选定；前室不作看板/堆放区',2150,1115),
 ('S02','F10FE','风淋室','门旁固定面可讨论门牌，先核进出方向',2150,185),
 ('S03','F1130','成品区','不能直接认定为8F-A成品组装区',45,210),
 ('S04','F10FF','原料仓','入口识别与真实货架库位需分别选址',2150,405),
 ('S05','F10DB','电子仓','不自动映射电池暂存或8F-B',2150,615),
 ('S06','F10DC','PCBA / 半成品','工序交接与缓冲边界、容量待核',2150,830),
 ('S07','F10EB','老化房','固定门旁面/状态卡条件待核',45,645),
 ('S08','F10EC','维修房','固定门旁面/返修记录条件待核',45,860),
]
lim=json.loads((R/'outputs/drawings/8F_render_limitations.json').read_text());M=lim['world_to_display']
source_records=[]
for code,handle,name,note,bx,by in source_specs:
 t=byhandle[handle];x,y=t['position'][:2];a,b,c,d,tx,ty=M;dx=a*x+c*y+tx;dy=b*x+d*y+ty
 source_records.append({'source_review_id':code,'source_text':t['text'],'display_label':name,'entity_handle':handle,'layer':t['layer'],'original_text_anchor_world_unverified_units':[x,y],'partial_svg_label_anchor_only':[dx,dy],'annotation_box':[bx,by],'review_note':note,'is_sign_position':False,'related_handle':'F10DD' if code=='S06' else None})
save(O/'原图文字核查锚点.json',{'source_sha256':'d368c39f3f5c9fdd2b783c8fc2949b6d1a744b03d5e9cafd172b17bc60a76918','purpose':'Original TEXT label references only; not installation coordinates','source_preview':'outputs/drawings/8F_source_candidate_partial.svg','source_to_display':M,'records':source_records})
def T(x,y,s,size=25,color='#000',weight=400):return f'<text x="{x}" y="{y}" font-size="{size}" fill="{color}" font-weight="{weight}" style="fill:{color};font-size:{size}px;font-weight:{weight}">{esc(s)}</text>'
def rect(x,y,w,h,fill='#fff',stroke='none'):return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{fill}" stroke="{stroke}"/>'
svg=ET.parse(R/'outputs/drawings/8F_source_candidate_partial.svg').getroot();svg.set('x','475');svg.set('y','180');svg.set('width','1640');svg.set('height',str(1525.925925925926*.82));src=ET.tostring(svg,encoding='unicode')
body=rect(0,0,2600,1680)+rect(0,0,2600,135,'#000')+rect(0,0,12,135,'#FF6600')+T(55,65,'8F候选原图 / 文字与固定结构核查',39,'#fff',700)+T(55,108,'S编号只关联原图文字，不是标牌安装点；原图部分实体预览保留原坐标关系。',24,'#fff')+src
for r in source_records:
 x,y=r['partial_svg_label_anchor_only'];sx,sy=475+.82*x,180+.82*y;bx,by=r['annotation_box'];endx=bx+390 if bx<1000 else bx;endy=by+45
 handles=r['entity_handle']+(' / '+r['related_handle'] if r['related_handle'] else '')
 body+=f'<path d="M{sx},{sy} L{endx},{endy}" fill="none" stroke="#FF6600" stroke-width="3"/>'+f'<circle cx="{sx}" cy="{sy}" r="11" fill="#fff" stroke="#FF6600" stroke-width="3"/>'+rect(bx,by,405,120,'#fff','#3E3A39')+rect(bx,by,7,120,'#FF6600')+T(bx+23,by+38,r['source_review_id']+' '+r['display_label'],26,'#000',700)+T(bx+23,by+70,'源文字 / '+handles,20,'#3E3A39')
 note=r['review_note'];parts=[note[:16],note[16:]] if len(note)>17 else [note]
 for i,p in enumerate(parts):body+=T(bx+23,by+97+i*20,p,18,'#3E3A39')
body+=rect(45,1450,2510,185,'#f4f4f4')+T(70,1491,'图签与单位仍待确认：图身 F0FBF「八层平面图」；同框图签 F10B1「三层平面图」；INSUNITS=1。',25,'#000',600)+T(70,1535,'电梯、楼梯、前室、防火门、配电与消防救援口保留；不据局部图确定唯一入口、实际安装坐标或可用承载面。',23,'#3E3A39')+T(70,1578,'HATCH / SPLINE / ELLIPSE未渲染，弧多段线为弦近似，字体替代；本图不可测量、放样或作为施工底图。',23,'#3E3A39')
(O/'8F候选原图_核查引线.svg').write_text('<svg xmlns="http://www.w3.org/2000/svg" width="2600px" height="1680px" viewBox="0 0 2600 1680"><title>原图文字核查，不是安装点位图</title><g font-family="PingFang SC,Microsoft YaHei,sans-serif">'+body+'</g></svg>')

body=rect(0,0,1600,930)+rect(0,0,1600,122,'#000')+rect(0,0,10,122,'#FF6600')+T(40,57,'七组安装选址关系 / 等待现场落点',34,'#fff',700)+T(40,98,'相对功能示意，非平面布局；箭头只表达阅读、更新与物料关系，不是运输路线。',21,'#fff')
groups=[('到层入口',['C01 入口形象与导览'],'待核实墙面','面向到达者'),('装配区域入口',['C02 区域吊牌','C03 区域柱牌'],'待核实吊点 / 柱面','面向主要进入视线'),('生产管理点',['C04 生产运行板','C05 SQDCP班组板'],'可更新管理墙 / 核实板架','可阅读、可更新、可停留'),('线边与段间缓冲',['C06 固定库位标签','C07 WIP限量牌'],'真实库格 / 待批准缓冲位','面向存取、投料与取料')]
for i,(title,cs,surface,view) in enumerate(groups):
 x=40+i*390;body+=rect(x,190,350,400,'#f4f4f4')+rect(x,190,350,68,'#000')+T(x+20,235,title,29,'#fff',600)
 for j,s in enumerate(cs):body+=T(x+20,320+j*53,s,24,'#000',700)
 body+=rect(x+20,403,310,4,'#FF6600')+T(x+20,465,surface,20,'#3E3A39')+T(x+20,518,view,20,'#3E3A39')
 if i<3:body+=T(x+354,380,'→',30,'#3E3A39')
body+=T(40,672,'先定对象与更新方式，再定实际固定面、朝向、高度、数量和安装结构。',27,'#000',600)+T(40,724,'C01-C07是评审组合ID，不是实际点位ID；七组不等于七件标牌。',24,'#3E3A39')+T(40,769,'成品区、电子仓、PCBA等原图名不自动对应8F-A至H；区域映射仍待生产/工程确认。',24,'#3E3A39')+T(40,839,'模板成品尺寸沿用V2.1 SVG；安装高度、吊挂承载、现场净空及审批均未造填。',23,'#3E3A39')
(O/'安装选址_相对关系示意.svg').write_text('<svg xmlns="http://www.w3.org/2000/svg" width="1600px" height="930px" viewBox="0 0 1600 930"><title>安装选址相对关系示意，非测量平面</title><g font-family="PingFang SC,Microsoft YaHei,sans-serif">'+body+'</g></svg>')

save(O/'image_generation_manifest.json',{'date_display':'2026-10-04','timezone':'America/Los_Angeles','tool':'built_in_image_gen','mode':'new_concept_with_existing_sign_artwork_references','site_photos_used':False,'images':scenes,'invariants':['Black/orange identity preserved','No orange floor marking','No fabricated output/limit/date values','No functioning invented QR','No formal logo invented'],'prompt_set_file':'图像生成提示词.md','production_authority':'Original editable SVGs; generated scene text may drift and is not print artwork'})
notes='''# 安装点位核查与效果图 / V2.2-CONCEPT

本轮工作目录仍为BeePumpFactoryVisual。日期按用户America/Los_Angeles时区显示为2026-10-04。

完成七组相对选址建议（含八种模板）、八个原图文字核查锚点、三张Imagegen概念效果图和可编辑SVG示意。S01-S08仅关联原图文字；C01-C07是评审组合ID，两者都不是实际安装点编号，也不代表实物数量。

当前可以评审安装逻辑：到层入口墙面导览；区域入口吊牌与柱牌；生产运行与SQDCP管理墙；固定库位与待核实并获批准的段间缓冲位。每组承载面、观看方向、更新方式、责任角色及现场条件已列入CSV/JSON。

当前不能确认具体安装位置：8F/3F图签冲突和物理单位仍待回复，现场人流/物流、墙柱/吊点、净空、安装高度及真实数量未勘测。data/points.json仍为空，未写入任何图片像素或原TEXT位置作为标牌坐标。八处核查锚点能追溯原实体handle，局部预览仍有实体/字体缺失。

效果图属于全新概念空间，无现场照片或测量建模，不是厂房现状或竣工状态。机器、桌椅、货架、容器仅为背景道具，不能据此统计采购或容量。8F-A只是原方案示例映射，不因生成图片获确认。细字可能由生成模型轻微变形，印刷仍使用design/v2原SVG。

先确认有效8F图框、毫米及现场尺寸；再以主要入口、区域边界、更新/日会点、真实库位和批准缓冲位照片核对固定面与朝向。建筑/消防/承载/电气由相应专业人员复核，正式Logo与1:1样牌未签核。不采购、不发供应商、不公开部署，不改原DWG/固定结构。
'''
(O/'README.md').write_text(notes)

def table(ds):
 return '<table><thead><tr><th>组合 / 模板</th><th>建议安装承载面与阅读</th><th>固定与更新</th><th>待现场核查 / 责任</th></tr></thead><tbody>'+''.join('<tr><td><b>'+d['review_id']+' '+esc(d['name'])+'</b><br>'+esc(' / '.join(d['template_codes']))+'</td><td>'+esc(d['recommended_relative_surface'])+'<br><small>'+esc(d['reading_direction_description'])+'</small></td><td>'+esc(d['mounting_and_update_proposal'])+'</td><td>'+esc(d['site_checks_needed'])+'<br><small>'+esc(d['owner_roles'])+'</small></td></tr>' for d in ds)+'</tbody></table>'
prefix='outputs/installation_review/'
def picture(s):return '<figure><img class="zoomable" tabindex="0" src="'+prefix+s['filename']+'" alt="'+esc(s['title']+'；概念安装示意，非现场照片')+'"><figcaption><b>'+esc(s['title'])+'</b><p>'+esc(s['caption'])+'</p><a href="'+prefix+s['filename']+'" download>保存PNG效果图</a></figcaption></figure>'
css='''*{box-sizing:border-box}body{margin:0;font-family:"PingFang SC",Arial,sans-serif;color:#000;background:#fff;line-height:1.7}a{color:#000;text-underline-offset:4px}header{background:#000;color:#fff;border-left:8px solid #FF6600;padding:20px 4vw;display:flex;justify-content:space-between;gap:20px;align-items:center}header a{color:#fff}main{max-width:1500px;margin:auto;padding:35px 28px}h1{font-size:40px;line-height:1.3;margin:0 0 16px}h2{font-size:26px;margin:0 0 18px}p{margin:12px 0}section{margin:50px 0}.intro{display:grid;grid-template-columns:1fr 1.4fr;gap:32px;align-items:center}.intro img{width:100%;display:block}.draft{border-left:5px solid #FF6600;background:#f3f3f3;padding:17px 22px;margin:25px 0}.summary{display:flex;gap:30px;flex-wrap:wrap}.summary b{font-size:30px;display:block}.summary small{font-size:14px}nav,.links{display:flex;gap:20px;flex-wrap:wrap;margin:25px 0}nav{border-bottom:1px solid #000;padding-bottom:20px}.note,small{color:#3E3A39;font-size:13px}.scroll{overflow:auto}table{width:100%;border-collapse:collapse;text-align:left;font-size:14px}th{background:#000;color:white;padding:12px}td{padding:14px;border-bottom:1px solid #ddd;vertical-align:top;min-width:160px}td:first-child{min-width:170px}.wide{width:100%;display:block;border:1px solid #ddd;max-height:930px;object-fit:contain;cursor:zoom-in}figure{margin:28px 0;background:#f3f3f3}figure img{width:100%;display:block;cursor:zoom-in}figcaption{padding:18px 22px}figcaption p{font-size:14px}.grid{display:grid;grid-template-columns:1fr 1fr;gap:20px}.grid>div{border-left:3px solid #FF6600;padding:14px 20px;background:#f4f4f4}dialog{border:0;width:min(98vw,1700px);padding:16px}dialog img{width:100%;max-height:86vh;object-fit:contain}dialog::backdrop{background:#000b}button{font:inherit;border:1px solid #000;background:white;padding:8px 15px;cursor:pointer;float:right}button:focus-visible,a:focus-visible,img:focus-visible{outline:3px solid #000;outline-offset:4px}footer{border-top:1px solid #000;padding:20px 28px;font-size:12px;color:#3E3A39}@media(max-width:800px){main{padding:24px 18px}.intro,.grid{grid-template-columns:1fr}h1{font-size:29px}header{align-items:flex-start}header a{font-size:13px}.summary{gap:22px}td{min-width:155px}nav{gap:12px}}'''
confirmation='<div class="grid"><div><b>图纸身份与单位</b><p>8F图身 / 3F图签冲突待核；INSUNITS=1；8700与6000仅完成图内数值一致性检查。请先选定有效图框并确认物理单位与现场尺寸。</p></div><div><b>具体安装面与方向</b><p>确认实际主要入口、区域边界、墙柱与专用吊点、更新/日会站位、真实库位和待批准缓冲位置，再勘测坐标与朝向。</p></div><div><b>固定结构与安装专项</b><p>前室、门扇、电梯、楼梯、消防救援口、消火栓和配电不改作展示或堆放位置。固定、承载、防火保护及适用专项由相关人员复核。</p></div><div><b>品牌与制作</b><p>正式Logo、区域映射和物理色板待确认；现场1:1样牌验证阅读与反光；生成图不作为印刷稿，原SVG为编辑依据。</p></div></div>'
page='<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>BeePump | 安装选址与效果图</title><style>'+css+'</style></head><body><header><b>BeePump / 安装评审</b><a href="START_HERE.html">返回六款模板评审</a></header><main><div class="intro"><div><h1>先确认安装关系<br>再勘测实际点位</h1><p>三组空间效果图、七组安装选址建议与可追溯的原图核查引线。</p><div class="summary"><span><b>7组</b><small>相对选址建议</small></span><span><b>3张</b><small>概念效果图</small></span><span><b>8处</b><small>原图文字核查</small></span></div></div><img class="zoomable" tabindex="0" src="'+prefix+scenes[0]['filename']+'" alt="区域吊牌与柱牌概念安装效果图"></div><div class="draft"><b>V2.2-CONCEPT / 待现场确认</b><br>C01-C07是评审组合编号，S01-S08是原图文字核查编号；均不是实际点位ID，不代表标牌数量。图签、单位和现场承载面未确认，真实安装坐标、高度与审批保持空值。</div><nav><a href="#recommend">安装选址建议</a><a href="#source">原图核查引线</a><a href="#relation">相对安装关系</a><a href="#scenes">三张效果图</a><a href="#confirm">待确认项</a></nav><div class="links"><a href="output/pdf/BeePump_Installation_Concept_Review_V2.2.pdf">打开安装评审PDF</a><a href="'+prefix+'安装选址评审台账.csv">可编辑CSV台账</a><a href="'+prefix+'8F候选原图_核查引线.svg">可编辑原图核查SVG</a><a href="'+prefix+'README.md">本轮范围与限制</a></div><section id="recommend"><h2>推荐按这七组安装关系逐一选面</h2><p>可先评审对象、承载面类型、阅读方向和更新方式。具体墙面、柱面、吊点和库格仍需现场核对。</p><div class="scroll">'+table(decisions)+'</div></section><section id="source"><h2>把原图中需要核查的区域指出来</h2><img class="wide zoomable" tabindex="0" src="'+prefix+'8F候选原图_核查引线.svg" alt="八个原图文字核查引线；不是实际安装点"><p class="note">引线端点仅对应原TEXT实体锚点，完整坐标关系记录在JSON中。S03成品区不能直接映射8F-A，S05电子仓不能直接映射电池暂存；S06 PCBA与半成品交接关系待确认。源图左侧存在裁切，不能由此确认唯一入口。</p></section><section id="relation"><h2>位置职责分清，标识才能持续更新</h2><img class="wide zoomable" tabindex="0" src="'+prefix+'安装选址_相对关系示意.svg" alt="七组安装选址相对关系，不是实际平面或路线"></section><section id="scenes"><h2>三个安装组合的空间效果</h2><p class="note">由内置Imagegen生成，参照现有六款图稿；无现场照片或测量建模。图片只展示视觉层级、材质和组合，设备/桌椅/容器是场景道具，不能用来统计数量、容量、安装高度或承载。细字以原SVG为准。</p>'+''.join(picture(s) for s in scenes)+'</section><section id="confirm"><h2>确认这四类条件后再落实际点位</h2>'+confirmation+'</section></main><footer>显示日期 2026-10-04 / America/Los_Angeles。黑橙品牌不用于地面橙色标线；原DWG和固定结构未更改；未制造审批记录或对外采购。原图依据：cad_texts.json、cad_inventory.json、8F_drawing_observations.json。三图完整提示词与参考记录保留在outputs/installation_review。</footer><dialog id="zoom"><button type="button" id="close">关闭</button><img id="zoom-image" alt="安装评审图放大"></dialog><script>const dialog=document.querySelector("#zoom");document.querySelectorAll(".zoomable").forEach(img=>{const open=()=>{document.querySelector("#zoom-image").src=img.src;document.querySelector("#zoom-image").alt=img.alt;dialog.showModal()};img.onclick=open;img.onkeydown=e=>{if(e.key==="Enter"||e.key===" "){e.preventDefault();open()}}});document.querySelector("#close").onclick=()=>dialog.close();dialog.onclick=e=>{if(e.target===dialog)dialog.close()};</script></body></html>'
(R/'INSTALLATION_REVIEW.html').write_text(page)

def datauri(p):
 ext=Path(p).suffix;mime='image/svg+xml' if ext=='.svg' else 'image/png'
 return 'data:'+mime+';base64,'+base64.b64encode((R/p).read_bytes()).decode()
pages=[]
def printpage(title,sub,body):
 n=len(pages)+1;pages.append('<section class="page"><header><b>BeePump</b><span>安装选址 / 概念评审</span><span>V2.2-CONCEPT</span></header><h1>'+title+'</h1><p class="sub">'+sub+'</p><div class="body">'+body+'</div><footer><span>实际点位未确认 / 非施工或现场验收文件 / 2026-10-04</span><span>'+str(n).zfill(2)+'</span></footer></section>')
printpage('先确认安装关系，再落实际点位','七组相对选址建议；实际安装坐标、高度、件数与审批保持未知。','<img class="diagram" src="'+datauri(prefix+'安装选址_相对关系示意.svg')+'"><p class="warn">图签与单位仍待核；原图锚点不作为标牌坐标。三张效果图为全新概念空间，无现场照片或测量建模。</p>')
printpage('8F候选原图：核查区域，不标安装点','S01-S08只关联原文字实体；固定结构、图签和原坐标关系保留。','<img class="source" src="'+datauri(prefix+'8F候选原图_核查引线.svg')+'"><p class="note">未渲染HATCH/SPLINE/ELLIPSE，字体替代；预览不用于测量或施工。八处锚点可回查原图实体handle。</p>')
printpage('入口与区域识别：先选真实承载面','C编号是评审组合编号，不是实际点位编号；这些建议不直接产生工程量。',table(decisions[:3])+'<p class="warn">C01需先确定实际主要入口。C02/C03需先确认装配区域与8F-A映射，源图“成品区”不能替代该确认。</p>')
printpage('管理与物流：让信息跟随更新和对象','生产运行、SQDCP、固定地址和段间容量规则分工明确。',table(decisions[3:])+'<p class="warn">C04/C05尚无现场墙面/站位证据；C06/C07没有实际库格、缓冲边界或批准容量。效果图不能补足这些事实。</p>')
for s in scenes:printpage(s['title'],'概念安装示意 / 非现场照片；尺寸感与背景道具不代表实测条件。','<img class="scene" src="'+datauri(s['path'])+'"><p>'+esc(s['caption'])+'</p><p class="note">细字可能有生成漂移；制作仍使用原SVG，不能从效果图抠图印刷。图片不证明承载、净空或专项合规。</p>')
printpage('确认条件与下一步勘测','先确认有效8F图框、物理单位，再收集真实进路和可安装面。',confirmation+'<p class="note">固定结构证据：南侧EVTR F08A0-F08AE、STAIR F0933-F0935；北侧EVTR F08E3-F08F2、STAIR F094A-F094C；防火门F0CFF/F0D1A/F09C3；消防救援口F0ED2-F0ED6；配电间F0E5E。均为原图实体观察，不是现场验收。</p><p class="note">可编辑记录：outputs/installation_review/安装选址评审台账.csv；原图核查锚点JSON；原SVG位于design/v2；完整提示词为outputs/installation_review/图像生成提示词.md。</p>')
pcss='''@page{size:420mm 297mm;margin:0}*{box-sizing:border-box}body{margin:0;font-family:"PingFang SC",Arial,sans-serif;color:#000}.page{width:420mm;height:297mm;padding:16mm 18mm;position:relative;break-after:page;overflow:hidden}.page:last-child{break-after:auto}header{display:flex;justify-content:space-between;padding-bottom:4mm;border-bottom:1.2mm solid #FF6600;font-size:9pt}header b{font-size:15pt}h1{font-size:24pt;margin:6mm 0 3mm;line-height:1.3}.sub{font-size:11pt;color:#3E3A39;margin:0 0 4mm}.body{font-size:11pt;line-height:1.6}.body p{margin:3mm 0}.diagram{width:100%;height:177mm;object-fit:contain}.source{width:100%;height:180mm;object-fit:contain}.scene{width:100%;height:173mm;object-fit:contain}.warn{padding:3mm 5mm;background:#f3f3f3;border-left:1.3mm solid #FF6600;font-size:10pt}.note,small{color:#3E3A39;font-size:9pt}table{width:100%;border-collapse:collapse;font-size:10pt;line-height:1.5;text-align:left}th{background:#000;color:#fff;padding:3mm}td{border-bottom:.2mm solid #ddd;vertical-align:top;padding:3.5mm}td:first-child{width:19%}td:nth-child(2){width:27%}td:nth-child(3){width:27%}td:nth-child(4){width:27%}footer{position:absolute;bottom:10mm;left:18mm;right:18mm;border-top:.2mm solid #888;padding-top:3mm;display:flex;justify-content:space-between;font-size:8pt;color:#3E3A39}.grid{display:grid;grid-template-columns:1fr 1fr;gap:5mm}.grid>div{background:#f3f3f3;border-left:1mm solid #FF6600;padding:5mm}.grid b{font-size:12pt}.grid p{font-size:10pt}'''
(O/'installation_print.html').write_text('<!doctype html><html lang="zh-CN"><meta charset="utf-8"><title>BeePump installation concept review</title><style>'+pcss+'</style>'+''.join(pages)+'</html>')
save(O/'review_manifest.json',{'revision':'V2.2-CONCEPT','pdf_pages':len(pages),'source_review_labels':len(source_records),'relative_selection_groups':len(decisions),'template_types':8,'mockup_images':len(scenes),'actual_points_generated':0,'actual_sign_quantities':None,'date_display':'2026-10-04','timezone':'America/Los_Angeles','pending_floor_and_unit_user_reply':True})
point_data=json.loads((R/'data/points.json').read_text())
assert (point_data.get('points',[]) if isinstance(point_data,dict) else point_data)==[], 'Do not fabricate installation points'
print('Created installation review: 7 relative groups, 8 source TEXT anchors, 3 concept images,',len(pages),'print pages. Actual points remain empty.')

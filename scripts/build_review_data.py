from pathlib import Path
import json,csv,math,copy,hashlib,xml.etree.ElementTree as ET
R=Path(__file__).resolve().parents[1]
def read(p):return json.loads((R/p).read_text())
def save(p,v):
 f=R/p;f.parent.mkdir(parents=True,exist_ok=True);f.write_text(json.dumps(v,ensure_ascii=False,indent=2))
ts=read('data/templates.json');v1=[t for t in ts if t['revision']=='V1.0'];iv=read('outputs/drawings/cad_inventory.json');texts=read('outputs/drawings/cad_texts.json');dims=read('outputs/drawings/cad_dimensions.json');blocks=read('outputs/drawings/cad_blocks.json')
rev=read('design/v2/revision_manifest.json');target={m['code']:m for m in rev}
notes={
'BE-01':'保留黑橙、工艺类别与简洁品牌层级；正式Logo及1994来源原件未取得，历史文案仍待核证。',
'BE-02':'保留8F与装配/测试/包装分层；SMT导向须依据真实落位，不能直接从基线派生箭头。',
'WF-01':'楼层用途与本层突出清晰；6F/7F仍未赋业务，DWG重名图框需先核对再定导览。',
'WF-02':'区域主名需优先远读；8F与A独立。V2保留蜂巢身份，增强字号与留白，Logo不冒充正式资产。',
'WF-03':'双面箭头不可镜像复制；测试/包装两行结构保留，各进路方向按校核底图实例化。',
'WF-04':'原箭头未经路径核查；V2移除箭头，突出楼层和区域，单列永久柱号。',
'WF-05':'固定房名与可换责任字段明确；不在防火门上默认钻孔，待真实房间清单。',
'VT-01':'保留看什么/证据/价值三段；T03仅节点示例，必须附真实区域及脱敏证据，不虚构本厂能力。',
'PM-01':'原示例产量与日期容易被当现场数据；V2全部改待填，差异公式、同工序单位与异常接单分开。',
'PM-02':'保留SQDCP五项和行动清单；V2增加口径周期与单位，成本金额/工时分列，阈值未获批准不染色。',
'PM-03':'保留呼叫/接单/隔离/恢复四步；既有设备灯态先映射，信号不等于品质放行。',
'EQ-01':'永久资产ID与位置码分开正确；EQ-000123是示例，QR框非码，须接真实台账再生成生产版。',
'EQ-02':'保留逾期/未知即暂停使用；校准日期不得预填，插卡选材按工况试样。',
'WH-01':'稳定地址与物料占用分开；V2增加完整留白与非扫码图说明，8F编码为结构草案，不是现场库位。',
'WH-02':'远读区排与近读列层合理；方向、列范围和货架载荷依赖实测，端头牌不覆盖载荷铭牌。',
'QC-01':'保留蓝待检与批次/工序/责任/流转权限；颜色不能替代放行记录，100×70小卡需1:1试写。',
'QC-02':'保留绿合格/已放行；限定批次、工序与版次，不能只凭绿色认定全流程放行。',
'QC-03':'保留红不合格和追溯字段；不能把不合格自动解释为报废。',
'QC-04':'保留黄待处理/冻结与黑字对比；由品质定义解冻/返工/特采权限。',
'WH-03':'保留实物/容器/批次/工序数量链；工序完成不能替代质量放行，卡号需要真实分配。',
'SW-01':'保留动作/关键点/原因三段与受控照片；图片占位必须换现场照片，SOP版次/批准不能补造。',
'FL-01':'原3车20台虽注示例仍可能误用；V2改当前/批准上限待填，满位停投与放行FIFO动作保留。',
'FL-02':'最早批次靠OUT端逻辑一致；明确非施工图，容器数/转向/入口位置与实际物流条件联核。',
'VS-01':'保留责任人/代理/频次/照片/未闭环问题；标准照片不能用概念渲染代替，最近检查不得假填。',
'BT-01':'保留批准数量/能量/实际库存分列；只作信息框架，安全内容与电池储存位置须专业确认。',
'BT-02':'保留周期完成不等于质量合格；必须映射真实程序/架号，不挡散热或贴导电材料。',
'MD-01':'保留永久模具ID、机台/库位、维护和状态；待用不表示试模/首件已批准。',
'QC-05':'保留首次提交与齐套受理两种时间；不因补资料清除历史，承诺时限和接手权限待确定。',
'SW-02':'保留清线/换版/首件与包规核对；客户专用信息朝内，双人核对与生效批次必须实填。',
'WH-04':'保留3F备货与1F装柜的共同ID；质量放行/齐套/装柜状态分列，敏感订单用代号。',
'BE-03':'保留工程/品质/效率/人才四项；Since1994未有本轮样册原件，历史年份和肖像授权均待核证。',
'BE-04':'保留工艺/控制点/实物/证据ID；手动和锂电路径并行，真实照片/能力/证书缺失时不编造。',
'ES-01':'保留人员/物料/工位/异常四项；EPA范围与SMT落位有图纸线索，控制要求仍以批准ESD方案为准。',
'EQ-03':'保留设备运行/待料/故障/停用语义；与质量卡绿放行含义区分，状态事件须有更新责任。',
'FM-01':'保留地面管理与安全图形分层；品牌橙不上地面，净宽/线宽按专项批准图确认。',
'WH-05':'保留跨层任务、实数与双方交接；不得按电梯两侧划框，合用前室与门前不作为默认待运位。'}
audit=[]
for i,t in enumerate(v1):
 f=R/t['path'];original=[s for s in ET.parse(f).getroot().itertext() if s.strip()]
 audit.append({'code':t['code'],'name':t['name'],'source_path':t['path'],'source_sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'decision':'Refine' if t['code'] in target else 'Preserve','observation':notes[t['code']],'preserve_fields':original,'evidence':f'reports/source_render/svg/contact-{i//12+1}.png','review_level':'Full SVG text plus rendered contact sheet; physical legibility and installation remain untested','v2_path':target.get(t['code'],{}).get('path'),'physical_size_mm':[t['w'],t['h']],'content_approval':None,'specialist_approval':None,'verification_method':t.get('spec',{}).get('checks')})
save('reports/template_audit.json',audit)
with (R/'reports/template_audit.csv').open('w',encoding='utf-8-sig',newline='') as f:
 w=csv.DictWriter(f,fieldnames=['code','name','decision','observation','source_path','evidence','v2_path']);w.writeheader();w.writerows({k:a.get(k) for k in w.fieldnames} for a in audit)
cal=[]
for h,axis in [('F112C','X'),('F1112','Y')]:
 d=next(t for t in dims if t['handle']==h);v=[d['definition_2'][i]-d['definition_1'][i] for i in range(2)];projected=abs(v[0 if axis=='X' else 1]);annotation=[]
 for e in blocks[d['block']]['entities']:
  if any(c==0 and s in ('TEXT','MTEXT') for c,s in e):annotation += [s for c,s in e if c in (1,3)]
 cal.append({'dimension_handle':h,'axis':axis,'source_definition_points':[d['definition_1'],d['definition_2']],'dimension_measurement_world':d['measurement'],'annotation_raw':annotation,'projected_length_world':projected,'error_world':abs(projected-d['measurement']),'coordinate_unit_verified':False,'note':'Numeric agreement in drawing units only; not a site survey or mm approval'})
save('outputs/drawings/8F_candidate_calibration.json',{'status':'numeric_consistency_checked_units_pending','drawing_sha256':iv['source_drawing_sha256'],'two_axes':cal,'unit_header':'INSUNITS=1 (inch); MEASUREMENT=0','mm_factor':None,'floor_title_conflict':{'body':'八层平面图','body_handle':'F0FBF','title_block':'三层平面图','title_block_handle':'F10B1'},'reviewer':None,'approved_at':None})
important=['八层平面图','三层平面图','合用前室','配电间','电子仓','PCBA','半成品','老化房','维修房','更衣室','风淋室','原料仓','成品区','消防救援口']
observed=[t for t in texts if t['text'] in important and 1000000<t['position'][0]<1135000 and 967000<t['position'][1]<1070000]
save('outputs/drawings/8F_drawing_observations.json',{'status':'source_text_observations_only','notes':'Label anchor coordinates are original entities, not sign placement coordinates. Area IDs have not been mapped.','observations':observed})
floorrows=read('data/floors.json')
names={'1F':'一层平面图','2F':'二层平面图','3F':'三层平面图','4F':'四层平面图','5F':'五层平面图','6F':'六层平面图','7F':'七层平面图','8F':'八层平面图','9F':'九层平面图'}
coverage=[]
for f in floorrows:
 candidates=[t for t in iv['title_candidates'] if t['text']==names[f['floor_id']]]
 f['geometry_status']='decoded_pending_verification';f['source_drawing_sha256']=iv['source_drawing_sha256'];f['cad_layout']='Model';f['title_candidate_handles']=[t['handle'] for t in candidates];f['cad_unit_header']=1
 if f['floor_id']=='8F':
  f['model_window']=[1000000,967000,1135000,1070000];f['base_preview']='outputs/drawings/8F_source_candidate_partial.svg';f['title_conflict']='F0FBF 八层平面图 vs F10B1 三层平面图';f['calibration']['evidence']=cal
 coverage.append({'floor_id':f['floor_id'],'baseline_function':f['baseline_function'],'baseline_source':f['function_source'],'cad_title_candidates':[{'text':t['text'],'handle':t['handle'],'position':t['position']} for t in candidates],'identity_status':'title_conflict' if f['floor_id'] in ['3F','4F','5F','6F','7F','8F'] else 'multiple_candidates_pending_selection','next_action':'先选择有效图框，确认单位、图签与现场功能；再生成实际点位和数量','point_coordinates':None,'quantity_installed':None})
save('data/floors.json',floorrows);save('outputs/planning/floor_coverage.json',coverage)
requirements=[('BE-02','楼层入口形象','楼层入口附近可见墙面','行政 / 销售'),('WF-01','楼层导览','入口决策点','行政 / 生产'),('WF-02','区域吊牌','8F-A入口视线','生产 / 工程'),('WF-04','柱牌','8F-A区域定位锚点','生产 / 工程'),('PM-01','生产运行','班组当班更新点','生产 / PMC / 品质'),('PM-02','SQDCP','班组日会点','生产 / 品质 / 工程'),('WH-01','库位','批准的线边物料位','仓库 / 系统管理员'),('WH-05','跨层交接','批准的物流待运区','物流 / 安全'),('EQ-01','设备身份','设备操作可见面','工程'),('EQ-03','设备状态','设备身份牌附近独立卡槽','生产 / 工程'),('QC-01~04','质量状态卡','容器与批次对象','品质'),('SW-01','SOP','对应受控工位','技术 / 品质 / 生产'),('SW-02','换型包装','首件与包装核对点','技术 / 品质 / 销售'),('FL-01','WIP限量','批准的段间缓冲点','生产 / 物流 / 安全'),('FL-02','FIFO逻辑','缓冲区可读说明面','生产 / 物流'),('VS-01','6S责任','责任区入口','区域负责人'),('VT-01','参观节点','批准的客户停留点','销售 / 品质 / 安全'),('BT-01','电池暂存','经专项批准的暂存区','安全 / 工程'),('BT-02','测试周期','实际测试格位外侧','品质 / 工程'),('ES-01','电子装配进入确认','已确认的EPA入口','工程 / 品质')]
intents=[]
for i,(code,name,context,owner) in enumerate(requirements,1):
 intents.append({'intent_id':f'I-8F-{i:02d}','floor_id':'8F','area_id':None,'template_code':code,'name':name,'context_to_survey':context,'owner_role':owner,'status':'unlocated_requirement','source_drawing_sha256':iv['source_drawing_sha256'],'position_world':None,'facing_degrees':None,'quantity':None,'faces':None,'installation_height_mm':None,'material_spec':None,'source':'V1 p.57 + R1 p.19-21','approvals':{},'note':'需求条目不是安装点位；20条不代表20块标牌'})
save('outputs/planning/8F_unlocated_requirements.json',intents)
def export(name,rows,fields):
 p=R/name;p.parent.mkdir(parents=True,exist_ok=True)
 with p.open('w',encoding='utf-8-sig',newline='') as f:
  w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows({k:t.get(k) for k in fields} for t in rows)
export('outputs/planning/8F待定位需求台账.csv',intents,['intent_id','floor_id','area_id','template_code','name','context_to_survey','owner_role','status','quantity','faces','position_world','installation_height_mm','material_spec','note'])
budget=[]
for t in v1:
 budget.append({'template_code':t['code'],'name':t['name'],'width_mm':t['w'],'height_mm':t['h'],'material_candidate_from_v1':t.get('spec',{}).get('material'),'candidate_status':'候选材料，须试样与专项确认','physical_quantity_proposed':None,'physical_quantity_approved':None,'faces_per_piece':None,'unit_price_CNY_per_piece_including_selected_faces':None,'install_price_CNY_per_piece':None,'loss_rate':None,'tax_rate':None,'unit':'piece','formula':'数量×(含选定面数的每件单价+每件安装费)；面数不再次乘单价','quantity_status':'未测量，未知不等于0'})
export('outputs/quantities/预算与数量输入.csv',budget,list(budget[0]))
save('outputs/quantities/budget_contract.json',{'currency_assumption':'CNY','actual_supplier_quote':False,'site_quantity_status':'unknown_not_zero','draft_sign_locations':None,'approved_sign_quantity':None,'formula':'subtotal = SUM(physical_qty * (piece_price_including_faces + install_price)); extras, loss and tax are separate reviewed inputs','production_approval':False,'proofing_proposal':'首批六款可分别做1:1纸样；种类数不是现场安装数量。单双面方向及安装材料不由纸样批准。','floor_marking_length_m':None,'floor_coating_area_m2':None,'safety_facilities':'专项项目另表，不计入VI板面报价'})
tasks=read('data/tasks.json')
for t in tasks:
 if t['id']=='P01':t['status']='partial';t['acceptance']='AutoCAD 2026原生DXF导出成功，82,383实体/188图层/667块/3布局已盘点；缺字与原生plot崩溃未解决。'
 elif t['id']=='P02':t['status']='blocked';t['acceptance']='已取得8F两向8700/6000标注一致性证据；单位字段和8F/3F图签冲突待业主/工程确认。'
 elif t['id'] in ('P03','P04'):t['status']='complete'
 elif t['id']=='P05':t['status']='blocked';t['acceptance']='已编20条8F待定位需求；不是标牌数。单位/图签未解决，未生成实际坐标点位。'
 elif t['id'] in ('P08','P09'):t['status']='partial';t['acceptance']='已提供材料候选、空值预算/数量输入、首批评审PDF与可编辑SVG；全厂BOQ与制作放行未完成。'
save('data/tasks.json',tasks)
intake=read('reports/cad_intake.json');intake.update(read_level='native_DWG_to_DXF_decoded',geometry_decoded=True,floor_count=None,layouts=['Model','布局1','布局2'],drawing_units='INSUNITS=1; physical unit unresolved',reason='Native DXF export succeeded; title conflict, missing fonts, native plot crash and units need review.',next_action='Confirm valid 8F sheet and physical units; resolve missing CAD fonts or provide reliable native vector PDF before coordinate placement.')
save('reports/cad_intake.json',intake)
save('reports/current_intake.json',{'working_directory':str(R),'desktop_target':'/Users/huhanwei/Desktop/BeePumpFactoryVisual','input_zip_sha256':'0e8775bf7782cd523a9ee5636ab31f570a254b014e23a37bb969d110a86fe14f','library_inputs':{'starter':'libfile_4e8c5f3bc28c8191ba01b31b76bb03b3','manual':'libfile_c913748957c08191a874c7f9711bee53','v1_package':'libfile_f34ced64b8a08191ad3dcea38a8561f4','reference':'libfile_ebf381a0654c8191bc1e9f1a237100c2'},'native_cad_plot_status':'failed_exit_254_no_pdf_created','source_pdf_pixels_inspected':['manual pages 7,9,57','reference pages 3,19'],'svg_audit_count':36,'v2_template_count':6,'actual_installed_sign_quantity':None})
print('36 audits; 9 floor baseline/evidence records; 20 unlocated requirements; budget inputs without invented quantities or prices.')

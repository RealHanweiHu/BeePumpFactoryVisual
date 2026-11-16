#!/usr/bin/env python3
"""Create the contractor handoff with verified CAD copies, sources and evidence."""
from pathlib import Path
from html.parser import HTMLParser
import hashlib,json,shutil,zipfile
ROOT=Path(__file__).resolve().parents[1]
STAGE=ROOT.parent/'deliverables/BeePump_1F_8F_Implementation_V2.4'
ZIP=ROOT/'BeePump_1F_8F_Implementation_V2.4_Source.zip'
STAGE.mkdir(parents=True,exist_ok=True)
files={'IMPLEMENTATION_1F_8F.html','AGENTS.md','output/pdf/BeePump_1F_8F_Implementation_Design_V2.4.pdf','output/pdf/BeePump_1F_8F_SettingOut_Acceptance_Forms_V2.4.pdf','outputs/drawings/factory_converted.dxf','reports/implementation_qa.json','reports/implementation_cad_review.md','reports/implementation_pdf_visual_review.md','reports/implementation_pdf_visual_review.json','reports/IMPLEMENTATION_RESULT.md','reports/implementation_content_checks.json','reports/implementation_project_validation.json','reports/implementation_tests.txt'}
for folder in ['inputs','data','design/v2','docs','scripts','tests','outputs/implementation_v2.4']:
 for p in (ROOT/folder).rglob('*'):
  if p.is_file() and '__pycache__' not in p.parts:files.add(str(p.relative_to(ROOT)))
for folder in ['reports/implementation_template_render','reports/implementation_operations_render']:
 for p in (ROOT/folder).rglob('*'):
  if p.is_file() and p.suffix in ['.json','.md']:files.add(str(p.relative_to(ROOT)))
for rel in ['reports/implementation_pdf_render/pages.json','reports/implementation_pdf_render/text.txt','reports/implementation_forms_render/pages.json','reports/implementation_forms_render/text.txt']:
 files.add(rel)
for record in json.loads((ROOT/'data/templates.json').read_text()):files.add(record['path'])
for file in sorted(files):
 source=ROOT/file
 if not source.is_file():raise ValueError('Required source absent: '+file)
 target=STAGE/file;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(source,target)
html=(STAGE/'IMPLEMENTATION_1F_8F.html').read_text().replace('<a href="BeePump_1F_8F_Implementation_V2.4_Source.zip">交实施方的完整源包</a>','')
(STAGE/'IMPLEMENTATION_1F_8F.html').write_text(html)
(STAGE/'START_HERE.html').write_text('''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>BeePump两层实施交接</title><style>body{font:20px/1.7 PingFang SC,Arial;margin:40px;max-width:850px}a{color:black}h1{border-left:7px solid #FF6600;padding-left:18px}</style><h1>BeePump 1F + 8F 实施交接设计</h1><p><a href="IMPLEMENTATION_1F_8F.html">打开离线设计、效果图与安装需求</a></p><p><a href="output/pdf/BeePump_1F_8F_Implementation_Design_V2.4.pdf">64页A3设计交接图册</a></p><p><a href="output/pdf/BeePump_1F_8F_SettingOut_Acceptance_Forms_V2.4.pdf">8页A4放样/打样/报价/验收表</a></p><p><a href="outputs/implementation_v2.4/specs/contractor_readme.md">实施方先读</a></p><p>可用于现场深化、核量、报价与1:1打样。当前真实点位/工程量和专业记录待闭合，未制作安装放行。原DWG/DXF副本见inputs/cad和outputs/drawings，不能把局部预览像素当现场毫米。</p></html>''')
(STAGE/'README.md').write_text('''# BeePump 1F + 8F 实施交接设计 V2.4 / 2026-10-07

双击 START_HERE.html 或 IMPLEMENTATION_1F_8F.html。输出PDF位于output/pdf；40条功能需求、材料家族、报价范围、现场表、CAD核查和效果图位于outputs/implementation_v2.4；38份选用SVG见artboard_catalog.json，其中27份为V2.4新版。1F/8F各自CSV可供逐项深化。REQ不是实际点位，模板条数不是安装件数。

本包可直接交实施方用于设计交接、核图、踏勘、放样核量、报价和1:1打样。现场确认有效1F/8F图框、物理单位、真实安装面与用途，再完成正式内容、材料/固定及适用专业记录，另发制作/安装稿。实际朝向、高度、数量、点位与批准没有造填。全部签样/验收表为空白纸质记录，另有可编辑CSV；PDF不是预填合格或已签施工图。

包含原始DWG、原生DXF副本、48份封存输入和既有/新版模板源，原件字节保留。1F三个候选、8F八层/三层标题冲突、INSUNITS与现场单位未核验；部分源图预览省略实体/字体、弦近似及8F左裁切，不能作最终施工底图。CAD单位必须两向校核并与现场有效版本对应。固定电梯/楼梯/墙柱/消防等不为版式移动。

物流按真实工单/检验计划选择入仓、获准直送、适用9F喷漆；满位先停止投入并协调源端等待。人员自然路径、载具转弯视线、日会更新、检验扫码、装卸和访客停留分别现场核查。完整外购电池包；安全异常停止普通流转，由授权人员按现场已批准专项流程接手，普通返修与之分开。老化、EPA、材料专项只在适用条件核定后启用。

品牌色黑/FF6600橙/白/3E3A39灰；品牌橙色不作地面线。SVG名义模块1用户单位=1mm；图册是缩比评审，正常打印PDF不能替代SVG制作/1:1样牌。字体文件不分发，制作时合法字体/字形转曲与正式Logo另核。效果图为AI生成概念空间，生成小字/设备/墙面/支架和产品外形均不是现场、工程量或构件承载证明；以SVG、放样和具名记录为准。

设计PDF供阅读，当前文字不能可靠搜索/抽取；编辑与检索使用SVG、CSV和离线HTML。

FILE_MANIFEST.json核对包内字节；reports有CAD/内容/结构/像素验证。主项目测试可在完整Mac工作目录运行，部分历史构建脚本需要Mac既有Chrome/Playwright/PDFKit环境，未安装陌生软件。核图/专业确认没有因数字验证自动通过。报价单单位互斥，整套与部件/件与面避免重复。
''')
class Links(HTMLParser):
 def __init__(self):super().__init__();self.links=[]
 def handle_starttag(self,tag,attrs):
  for k,v in attrs:
   if k in ('href','src') and v and not v.startswith(('http:','https:','data:','#')):self.links.append(v)
missing=[]
for file in ['START_HERE.html','IMPLEMENTATION_1F_8F.html']:
 parser=Links();parser.feed((STAGE/file).read_text())
 for link in parser.links:
  if not (STAGE/link).exists():missing.append([file,link])
if missing:raise ValueError('Broken standalone links: '+json.dumps(missing,ensure_ascii=False))
manifest=[]
for p in sorted(STAGE.rglob('*')):
 if p.is_file() and p.name!='FILE_MANIFEST.json':manifest.append({'path':str(p.relative_to(STAGE)),'size':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
(STAGE/'FILE_MANIFEST.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
with zipfile.ZipFile(ZIP,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
 for p in sorted(STAGE.rglob('*')):
  if p.is_file():z.write(p,str(Path(STAGE.name)/p.relative_to(STAGE)))
with zipfile.ZipFile(ZIP) as z:
 assert z.testzip() is None
 for x in manifest:assert hashlib.sha256(z.read(STAGE.name+'/'+x['path'])).hexdigest()==x['sha256']
report={'stage':str(STAGE),'zip':str(ZIP),'zip_size':ZIP.stat().st_size,'zip_sha256':hashlib.sha256(ZIP.read_bytes()).hexdigest(),'files_verified':len(manifest)+1,'crc_passed':True,'all_member_sha256_passed':True,'standalone_links_passed':True,'source_dwg_included':True,'native_dxf_included':True,'frozen_inputs_included':48}
(ROOT/'reports/implementation_package_verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(report,ensure_ascii=False,indent=2))

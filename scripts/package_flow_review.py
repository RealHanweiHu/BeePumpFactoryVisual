#!/usr/bin/env python3
"""Create a standalone review/source subset; preserve the full project separately."""
from pathlib import Path
import hashlib, json, shutil, zipfile
from html.parser import HTMLParser
ROOT=Path(__file__).resolve().parents[1]
STAGE=ROOT.parent/'deliverables/BeePump_Flow_Review_V2.3'
STAGE.mkdir(parents=True,exist_ok=True)
ZIP=ROOT/'BeePump_Flow_Review_V2.3_Source.zip'
files={'FLOW_REVIEW.html','INSTALLATION_REVIEW.html','AGENTS.md','output/pdf/BeePump_Flow_People_Review_V2.3.pdf','output/pdf/BeePump_Installation_Concept_Review_V2.2.pdf','data/templates.json','data/floors.json','data/tasks.json','data/points.json','data/sources.json','scripts/build_flow_review.py','reports/flow_qa.json','reports/flow_fieldwork_qa.json','reports/FLOW_RESULT.md','reports/flow_content_review.md','reports/flow_pdf_render/pages.json','reports/flow_pdf_render/text.txt'}
for folder in ['outputs/flow_review','outputs/installation_review','design/v2/flow_v2.3','reports/flow_template_render','reports/flow_render','docs']:
    for p in (ROOT/folder).rglob('*'):
        if p.is_file():files.add(str(p.relative_to(ROOT)))
for v in json.loads((ROOT/'data/templates.json').read_text()):files.add(v['path'])
for file in sorted(files):
    source=ROOT/file
    if not source.is_file():raise ValueError('Required source absent: '+file)
    target=STAGE/file;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(source,target)
html=(STAGE/'FLOW_REVIEW.html').read_text()
html=html.replace('<a href="BeePump_Flow_Review_V2.3_Source.zip">V2.3可编辑源文件包</a>','')
(STAGE/'FLOW_REVIEW.html').write_text(html)
(STAGE/'START_HERE.html').write_text('<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>BeePump V2.3入口</title><style>body{font:20px/1.7 PingFang SC,Arial;margin:40px;max-width:850px}a{color:black}h1{border-left:7px solid #FF6600;padding-left:18px}</style><h1>BeePump V2.3物流与人的动线深化</h1><p><a href="FLOW_REVIEW.html">打开完整离线审阅页</a></p><p><a href="output/pdf/BeePump_Flow_People_Review_V2.3.pdf">打开30页A3图册</a></p><p><a href="INSTALLATION_REVIEW.html">查看既有V2.2安装与三张概念效果图</a></p><p>本包是可编辑设计及证据子集；原DWG/完整输入及DXF仍保存在主项目。实际点位、数量和施工放行待图纸及现场确认。</p></html>')
(STAGE/'README.md').write_text('''# BeePump V2.3物流与人的动线深化

双击START_HERE.html或FLOW_REVIEW.html。PDF见output/pdf，6新编辑模板见design/v2/flow_v2.3，4功能图/台账/现场表见outputs/flow_review，验证证据见reports。

本包包含V2.3设计源及对应V1/V2.1模板、V2.2安装审阅和概念图。没有原DWG、巨型DXF、全部原PDF/ZIP或字体；data/sources.json用于追溯，不表示输入字节已全部装入本子集。原输入、旧版完整包与完整校验工程仍在Mac主项目中保留。

python3 scripts/build_flow_review.py可重建本包功能图及HTML；浏览器PDF/渲染工具使用作者Mac已有环境，未要求安装陌生软件。全量项目validate/tests须在完整主项目运行。所有楼层是待核基线，功能箭头非实际方向，未知值不填0，制作放行false。

δ从达到触发条件至请求建立；L从请求建立至物料在供料点可用。不能把补料算例或效果图当核定容量/现场坐标。Library身份以实际保存返回为准。
''')

class Links(HTMLParser):
    def __init__(self):super().__init__();self.links=[]
    def handle_starttag(self,tag,attrs):
        for k,v in attrs:
            if k in ('href','src') and v and not v.startswith(('http:','https:','data:','#')):self.links.append(v)
missing=[]
for file in ['START_HERE.html','FLOW_REVIEW.html','INSTALLATION_REVIEW.html']:
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
report={'stage':str(STAGE),'zip':str(ZIP),'zip_size':ZIP.stat().st_size,'zip_sha256':hashlib.sha256(ZIP.read_bytes()).hexdigest(),'files_verified':len(manifest)+1,'crc_passed':True,'all_member_sha256_passed':True,'standalone_links_passed':not missing,'pdf':{'path':'output/pdf/BeePump_Flow_People_Review_V2.3.pdf','size':(ROOT/'output/pdf/BeePump_Flow_People_Review_V2.3.pdf').stat().st_size,'sha256':hashlib.sha256((ROOT/'output/pdf/BeePump_Flow_People_Review_V2.3.pdf').read_bytes()).hexdigest()}}
(ROOT/'reports/flow_package_verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(report,ensure_ascii=False,indent=2))

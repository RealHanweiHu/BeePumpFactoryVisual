"""Package reviewed new files; preserve all prior inputs and delivery versions."""
from pathlib import Path
from html.parser import HTMLParser
import json,hashlib,shutil,zipfile,html,sys
R=Path(__file__).resolve().parents[1]
S=R.parent/'deliverables'/'BeePump_Installation_Review_V2.2'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def put(src,dest,allow_own_update=False):
 dest.parent.mkdir(parents=True,exist_ok=True)
 if dest.exists() and sha(dest)!=sha(src) and not allow_own_update:raise RuntimeError('Preserve existing differing file: '+str(dest))
 shutil.copy2(src,dest)
def dump(p,data):p.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
files=['INSTALLATION_REVIEW.html','output/pdf/BeePump_Installation_Concept_Review_V2.2.pdf','reports/installation_qa.json','reports/installation_project_validation.json','reports/installation_tests.txt','reports/INSTALLATION_RESULT.md']
files += [p.relative_to(R).as_posix() for p in (R/'outputs/installation_review').iterdir() if p.is_file()]
files += [p.relative_to(R).as_posix() for p in (R/'design/v2').glob('*') if p.is_file()]
files += ['reports/v2_render/'+c+'.png' for c in ['WF-02','WF-04','WH-01','PM-01','PM-02','FL-01']]
files += ['.agents/skills/beepump-factory-visual/SKILL.md','docs/DECISIONS.md','docs/TASTE_ADAPTATION.md','data/tasks.json','data/points.json']
S.mkdir(parents=True,exist_ok=True)
for f in files:put(R/f,S/f,allow_own_update=True)
artwork_paths={m['code']:m['path'] for m in json.loads((R/'design/v2/revision_manifest.json').read_text())}
cards=''.join('<article><h2>'+c+'</h2><a href="'+html.escape(artwork_paths[c],quote=True)+'"><img src="reports/v2_render/'+c+'.png" alt="'+c+' 可编辑模板预览">打开原SVG</a></article>' for c in ['WF-02','WF-04','WH-01','PM-01','PM-02','FL-01'])
(S/'START_HERE.html').write_text('<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>BeePump 安装选址评审包</title><style>body{font-family:PingFang SC,Arial,sans-serif;max-width:1300px;margin:30px auto;padding:20px}h1{border-left:6px solid #FF6600;padding-left:18px}a{color:#000}main{display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:28px}article{background:#f3f3f3;padding:20px}img{width:100%;height:280px;object-fit:contain}</style><h1>BeePump 安装选址与效果图</h1><p><a href="INSTALLATION_REVIEW.html">打开七组选址建议、原图核查与三张效果图</a></p><p>八页 PDF、可编辑 CSV/JSON/SVG 和完整提示词均可从评审页面打开。真实点位、数量与安装高度尚未确认。</p><p>这是独立可查看的 V2.2 追加评审包；原DWG/V1完整输入仍保存在主项目和上一版源文件包中。下方为六款既有图稿，生成图不能代替这些印刷源文件。</p><main>'+cards+'</main></html>')
(S/'README.md').write_text('# BeePump 安装选址与效果图 V2.2-CONCEPT\n\n先打开 INSTALLATION_REVIEW.html 或 START_HERE.html。包含三张概念图、七组相对选址、八处原TEXT核查、八页PDF和六款既有原SVG；非现场照片、非施工图，不代表已确认安装点。\n\n此独立包无需联网即可查看；原DWG和完整V1输入位于主项目及上一版源文件包。CAD缺失实体、字体替代、图签/单位冲突仍明确保留。图片完整提示词在 outputs/installation_review。\n\n本轮生成/QA脚本在主项目 scripts，不依赖新安装软件；本包为查看与编辑的成果包，不承诺独立恢复Mac CAD转换或生成模型运行。\n')
manifest=[{'path':p.relative_to(S).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p)} for p in sorted(S.rglob('*')) if p.is_file() and p.name!='FILE_MANIFEST.json']
class References(HTMLParser):
 def __init__(self):super().__init__();self.refs=[]
 def handle_starttag(self,tag,attrs):
  for k,v in attrs:
   if k in ('href','src') and v and not v.startswith(('#','data:')):self.refs.append(v)
for name in ('INSTALLATION_REVIEW.html','START_HERE.html'):
 parser=References();parser.feed((S/name).read_text())
 assert all((S/ref).exists() for ref in parser.refs), 'Portable package links must all resolve'
dump(S/'FILE_MANIFEST.json',{'revision':'V2.2-CONCEPT','files':manifest,'actual_points':0,'purpose':'Portable review and editable artwork, not complete source CAD reconstruction'})
z=R.parent/'deliverables/BeePump_Installation_Review_V2.2_Source.zip'
with zipfile.ZipFile(z,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as f:
 for p in sorted(S.rglob('*')):
  if p.is_file():f.write(p,'BeePump_Installation_Review_V2.2/'+p.relative_to(S).as_posix())
with zipfile.ZipFile(z) as f:assert f.testzip() is None
receipt={'staging':str(S),'portable_archive':str(z),'archive_bytes':z.stat().st_size,'archive_sha256':sha(z),'portable_file_count':len(manifest)+1,'actual_points':0,'pdf_sha256':sha(R/'output/pdf/BeePump_Installation_Concept_Review_V2.2.pdf')}
if '--desktop' in sys.argv:
 D=Path('/Users/huhanwei/Desktop/BeePumpFactoryVisual')
 assert D.is_dir(),'Inspect existing desktop folder before creating or copying'
 old=D/'BeePumpFactoryVisual_V2.1_Draft_Source.zip'
 if not old.is_file():
  original=Path(json.loads((D/'DELIVERY_RECEIPT.json').read_text())['working_directory'])
  old=original.parent/'deliverables'/old.name
 before=sha(old)
 assert before=='07d5bdc52d5e4782af3ddbc28df029e24df09acc666fdc89775655fb72ec2525','Unexpected original archive change'
 for f in files:
  if f.startswith('docs/') or f in ['data/tasks.json','data/points.json','.agents/skills/beepump-factory-visual/SKILL.md'] or f.startswith('design/v2/') or f.startswith('reports/v2_render/'):continue
  put(R/f,D/f)
 for f in ['scripts/build_installation_review.py','scripts/qa_installation_review.cjs']:put(R/f,D/f)
 put(R/'scripts/package_installation_review.py',D/'scripts/package_installation_review.py',allow_own_update=True)
 put(R/'docs/DECISIONS.md',D/'docs/DECISIONS_V2.2.md')
 put(R/'data/tasks.json',D/'data/tasks_V2.2.json')
 for sub in ['reports/installation_render','reports/installation_pdf_render']:
  for p in (R/sub).iterdir():
   if p.is_file():put(p,D/sub/p.name)
 previous=D/'START_HERE.html';backup=D/'START_HERE_V2.1_ARCHIVE.html'
 if sha(previous)=='c27e1e56c97cda553640d51195c5bbd949754f7b0bfa2fd085bb85e70f1cc3ac':
  put(previous,backup);put(R/'START_HERE.html',previous,allow_own_update=True)
 else:assert sha(previous)==sha(R/'START_HERE.html'),'Preserve unexpected existing index edits'
 if (D/z.name).is_file():
  saved=json.loads((D/'INSTALLATION_DELIVERY_V2.2.json').read_text())
  assert sha(D/z.name)==saved['archive_sha256'],'Preserve externally modified archive'
 put(z,D/z.name,allow_own_update=True)
 assert sha(old)==before,'Previous archive must remain intact'
 copied=[p for p in D.rglob('*') if p.is_file() and (p.relative_to(D).as_posix() in files or 'installation' in p.relative_to(D).as_posix().lower())]
 for f in files:
  if (D/f).is_file() and not f.startswith('docs/') and f not in ['data/tasks.json']:assert sha(D/f)==sha(R/f),f
 receipt.update(desktop_root=str(D),desktop_review=str(D/'INSTALLATION_REVIEW.html'),desktop_pdf=str(D/'output/pdf/BeePump_Installation_Concept_Review_V2.2.pdf'),desktop_archive=str(D/z.name),previous_archive_preserved=True)
 dump(D/'INSTALLATION_DELIVERY_V2.2.json',receipt)
 dump(D/'INSTALLATION_FILE_MANIFEST_V2.2.json',{'files':[{'path':p.relative_to(D).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p)} for p in sorted(copied)],'previous_archive_sha256':before,'notes':'V2.1 source archive and immutable inputs preserved; previous index archived; new source archive is standalone review package.'})
dump(R/'reports/installation_delivery_receipt.json',receipt)
print(json.dumps(receipt,ensure_ascii=False,indent=2))

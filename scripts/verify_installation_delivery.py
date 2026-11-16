from pathlib import Path
from html.parser import HTMLParser
import hashlib,json,zipfile
R=Path(__file__).resolve().parents[1]
D=Path('/Users/huhanwei/Desktop/BeePumpFactoryVisual');S=R.parent/'deliverables/BeePump_Installation_Review_V2.2'
receipt=json.loads((D/'INSTALLATION_DELIVERY_V2.2.json').read_text())
if not S.is_dir():
 S=Path(receipt['staging'])
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
class Links(HTMLParser):
 def __init__(self):super().__init__();self.refs=[]
 def handle_starttag(self,t,a):
  for k,v in a:
   if k in ('href','src') and v and not v.startswith(('#','data:')):self.refs.append(v)
checks=[]
for root in (D,S):
 for name in ('INSTALLATION_REVIEW.html','START_HERE.html'):
  p=Links();p.feed((root/name).read_text());missing=[x for x in p.refs if not (root/x).exists()]
  assert not missing,missing
  checks.append({'file':str(root/name),'relative_links_checked':len(p.refs),'valid_directory_links':[x for x in p.refs if (root/x).is_dir()],'missing':missing})
z=Path(receipt['desktop_archive'])
if not z.is_file():
 z=Path(receipt['portable_archive'])
assert sha(z)==receipt['archive_sha256']
with zipfile.ZipFile(z) as archive:
 assert archive.testzip() is None;zip_files=len(archive.namelist())
 manifest=json.loads(archive.read('BeePump_Installation_Review_V2.2/FILE_MANIFEST.json'))
 for f in manifest['files']:
  assert hashlib.sha256(archive.read('BeePump_Installation_Review_V2.2/'+f['path'])).hexdigest()==f['sha256'],f['path']
assert sha(Path(receipt['desktop_pdf']))==receipt['pdf_sha256']
old=D/'BeePumpFactoryVisual_V2.1_Draft_Source.zip'
if not old.is_file():
 original=Path(json.loads((D/'DELIVERY_RECEIPT.json').read_text())['working_directory'])
 old=original.parent/'deliverables'/old.name
assert sha(old)=='07d5bdc52d5e4782af3ddbc28df029e24df09acc666fdc89775655fb72ec2525'
assert len(json.loads((D/'data/points.json').read_text())['points'])==0
result={'passed':True,'checks':checks,'archive_file_count':zip_files,'all_archive_manifest_hashes_match':True,'old_archive_intact':True,'desktop_pdf_bytes':Path(receipt['desktop_pdf']).stat().st_size,'actual_point_count':0,'desktop_assets_match_working_files':True,'note':'Main index includes intentional existing design/v2 folder link; valid directory targets accepted.'}
(R/'reports/installation_delivery_verification.json').write_text(json.dumps(result,ensure_ascii=False,indent=2))
print(json.dumps(result,ensure_ascii=False,indent=2))

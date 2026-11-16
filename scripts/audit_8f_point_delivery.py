"""Audit delivered concepts, immutable sources and local navigation; no engineering approval."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit,unquote
import hashlib
import json
import struct
import xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'design/v2/point_effects_2026-10-26'
REPORT=ROOT/'reports/point_effects_2026-10-26'
def read(p): return json.loads(p.read_text())
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
class Links(HTMLParser):
    def __init__(self): super().__init__();self.refs=[];self.ids=[];self.images=[]
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if a.get('id'):self.ids.append(a['id'])
        for field in ('href','src'):
            if a.get(field): self.refs.append(a[field])
        if tag=='img':self.images.append(a)

def main():
    checks=[]
    def check(ok,msg):
        checks.append({'check':msg,'passed':bool(ok)})
        if not ok: raise AssertionError(msg)
    frozen=read(REPORT/'protected_before.json')
    for path,digest in frozen.items(): check(sha(ROOT/path)==digest,'Protected file unchanged: '+path)
    manifest=read(BASE/'manifest.json');assets=manifest['assets']
    expected={f'D{i:02}' for i in range(1,22)}|{'U01'}
    check({r['key'] for r in assets}==expected and len(assets)==22,'22 distinct required scenes saved')
    check(len({r['sha256'] for r in assets})==22,'22 distinct image payloads')
    specs={r['key']:r for r in read(BASE/'prompts.json')['prompts']}
    for r in assets:
        p=ROOT/r['path'];content=p.read_bytes()
        check(sha(p)==r['sha256'],'Image hash: '+r['key'])
        check(struct.unpack('>II',content[16:24])==(r['width_px'],r['height_px']),'PNG dimensions: '+r['key'])
        check(r['production_release'] is False and r['actual_point_id'] is None and r['actual_quantity'] is None and r['world_coordinates'] is None,'No invented point/quantity/release: '+r['key'])
        check(hashlib.sha256(specs[r['key']]['prompt'].encode()).hexdigest()==r['prompt_sha256'],'Prompt provenance: '+r['key'])
        if specs[r['key']].get('edit_prompt'):
            check(hashlib.sha256(specs[r['key']]['edit_prompt'].encode()).hexdigest()==r['edit_prompt_sha256'],'Edit provenance: '+r['key'])
    templates=read(BASE/'templates/manifest.json')['templates']
    check({t['code'] for t in templates}=={'WF-02','WF-04','WH-01','PM-01','PM-02','FL-01'},'Six core template codes stable')
    for t in templates:
        check(sha(ROOT/t['source_path'])==t['source_sha256'],'Original SVG unchanged: '+t['code'])
        root=ET.parse(ROOT/t['path']).getroot();w,h=t['physical_size_mm']
        check(root.attrib['viewBox']==f'0 0 {w} {h}','Original nominal viewBox: '+t['code'])
        old=ET.parse(ROOT/t['source_path']).getroot()
        strings=[''.join(n.itertext()) for n in old.iter('{http://www.w3.org/2000/svg}text')]
        check(strings==t['original_text_preserved_in_metadata'],'Original text preserved in metadata: '+t['code'])
        meta=json.loads(root.find('{http://www.w3.org/2000/svg}metadata').text)
        check(meta==t and t['production_release'] is False and all(v is None for v in t['approvals'].values()),'Embedded draft metadata consistent: '+t['code'])
        for n in root.iter('{http://www.w3.org/2000/svg}text'):
            x=float(n.attrib.get('x',0));y=float(n.attrib.get('y',0))
            check(0<=x<=w and 0<y<=h,'Text anchor inside canvas: '+t['code']+' '+''.join(n.itertext()))
        for kind in ('before','after'):check((REPORT/'template_render'/f'{t["code"]}_{kind}.png').is_file(),'Actual render exists: '+t['code']+' '+kind)
    proposals=read(ROOT/'data/8F_point_visual_proposals.json')['proposals']
    check(len(proposals)==22 and {r['detail_id'] for r in proposals}==expected,'22 cross-indexed concepts, no missing requirements')
    check(all(r['actual_point_id'] is None and r['position_world'] is None and r['actual_quantity'] is None and r['actual_dimensions_mm'] is None and r['production_release'] is False for r in proposals),'Actual points/dimensions/quantities/release remain unset')
    pages=[ROOT/'交付_8楼/逐点效果与功能优化_2026-10-26/打开这里.html',REPORT/'templates_compare.html',ROOT/'交付_8楼/打开这里.html']
    for p in pages:
        parsed=Links();parsed.feed(p.read_text())
        check(len(parsed.ids)==len(set(parsed.ids)),'Unique HTML IDs: '+p.name)
        check(all(r.get('alt') for r in parsed.images),'Image alt text: '+p.name)
        for value in parsed.refs:
            url=urlsplit(value)
            if url.scheme or url.netloc:continue
            target=(p.parent/unquote(url.path)).resolve() if url.path else p
            check(target.exists(),'Local link exists: '+str(p.relative_to(ROOT))+' -> '+value)
            if url.fragment and target.is_file() and target.suffix=='.html':
                other=Links();other.feed(target.read_text());check(unquote(url.fragment) in other.ids,'Target anchor exists: '+value)
    refs=read(REPORT/'reference_records.json')
    check(sum(r.get('platform')=='xiaohongshu' for r in refs['sources'])==3 and refs['xiaohongshu_access']['note_content_read'] is True,'Three actually read Xiaohongshu case records')
    result={'revision':'8F-POINT-EFFECTS-2026-10-26-DRAFT','status':'passed','check_count':len(checks),
            'images':22,'templates':6,'protected_files':len(frozen),'checks':checks,
            'limits':'Static artifact/source/navigation audit, not a browser interaction test, site survey, engineering or installation approval.'}
    (REPORT/'artifact_audit.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print('Artifact audit passed:',len(checks),'checks; 22 images, 6 template drafts,',len(frozen),'protected files.')

if __name__=='__main__':main()

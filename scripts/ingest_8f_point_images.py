"""Copy generated concepts into the project with per-image provenance, no source uploads."""
from pathlib import Path
import hashlib
import json
import shutil
import struct

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'design/v2/point_effects_2026-10-26'
REPORT=ROOT/'reports/point_effects_2026-10-26'

def read(p): return json.loads(p.read_text())
def save(p,data): p.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')

def main():
    promptdoc=read(BASE/'prompts.json')
    specs={r['key']:r for r in promptdoc['prompts']}
    files=read(BASE/'generated_file_map.json')
    for p in sorted(REPORT.glob('generated_D*.json')):
        row=read(p);files[row['key']]=row['generated_file']
        specs[row['key']]['prompt']=row['prompt']
        if row.get('edit_prompt'):
            specs[row['key']]['edit_prompt']=row['edit_prompt']
            specs[row['key']]['edit_source_generated_image']=row['edit_source_generated_image']
            specs[row['key']]['review_fix']=row['review_fix']
    save(BASE/'generated_file_map.json',files)
    promptdoc['prompts']=[specs[k] for k in sorted(specs)]
    save(BASE/'prompts.json',promptdoc)
    assets=[]
    for key,src in sorted(files.items()):
        s=specs[key];source=Path(src)
        if not source.is_file(): raise FileNotFoundError(source)
        name=key+'_'+s['title'].replace('（','_').replace('）','')+'_DRAFT.png'
        dest=BASE/name
        previous=None
        if dest.exists() and source.read_bytes()!=dest.read_bytes():
            previous=str(dest.relative_to(ROOT))
            name=name.removesuffix('_DRAFT.png')+'_R2_'+hashlib.sha256(source.read_bytes()).hexdigest()[:8]+'_DRAFT.png'
            dest=BASE/name
        if not dest.exists(): shutil.copy2(source,dest)
        if source.read_bytes()!=dest.read_bytes(): raise ValueError('Existing destination differs: '+str(dest))
        content=dest.read_bytes()
        if content[:8]!=b'\x89PNG\r\n\x1a\n': raise ValueError('Not PNG')
        width,height=struct.unpack('>II',content[16:24])
        meta={'key':key,'id':s['id'],'title':s['title'],'revision':'8F-POINT-EFFECTS-2026-10-26-DRAFT',
              'status':'generated_functional_concept','production_release':False,
              'path':str(dest.relative_to(ROOT)),'width_px':width,'height_px':height,
              'sha256':hashlib.sha256(content).hexdigest(),'generation_tool':'image_gen',
              'generation_mode':'generated_concept_edit_no_project_upload' if s.get('edit_prompt') else 'text_only_no_reference_upload','original_generated_file':str(source),
              'prompt_file':str((BASE/'prompts.json').relative_to(ROOT)),'prompt_key':key,
              'prompt_sha256':hashlib.sha256(s['prompt'].encode()).hexdigest(),
              'edit_prompt_sha256':hashlib.sha256(s['edit_prompt'].encode()).hexdigest() if s.get('edit_prompt') else None,
              'edit_source_generated_image':s.get('edit_source_generated_image'),
              'review_fix':s.get('review_fix'),'preserved_earlier_concept':previous,
              'reference_ledger':'reports/point_effects_2026-10-26/reference_records.json',
              'xiaohongshu_in_generation_prompt':'案例适配：' in s['prompt'] or '参考方向（' in s['prompt'],
              'actual_point_id':None,'world_coordinates':None,'actual_size_mm':None,'actual_quantity':None,
              'site_photo':False,'geometry_reconstruction':False,'source_images_uploaded':False,
              'generated_reference_image_used':bool(s.get('edit_prompt')),'project_inputs_uploaded':False,'third_party_images_uploaded':False,
              'note':'Spatial context, equipment, props and prop counts are illustrative. Exact text uses editable SVG/documents.'}
        save(dest.with_suffix('.meta.json'),meta);assets.append(meta)
    save(BASE/'manifest.json',{'revision':'8F-POINT-EFFECTS-2026-10-26-DRAFT','status':'draft',
          'production_release':False,'planned_scenes':22,'generated_images':len(assets),'assets':assets})
    print('Saved',len(assets),'concept images with hashes; originals retained.')

if __name__=='__main__': main()

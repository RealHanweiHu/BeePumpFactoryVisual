#!/usr/bin/env python3
"""Append verified V2.4 files to the independent Desktop project; archive collisions."""
from pathlib import Path
import hashlib,json,shutil
ROOT=Path(__file__).resolve().parents[1];DESKTOP=Path('/Users/huhanwei/Desktop/BeePumpFactoryVisual')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert DESKTOP.is_dir()
index=json.loads((ROOT/'reports/implementation_index_archive.json').read_text())
assert sha(DESKTOP/'START_HERE.html')==index['old_index_sha256'],'Desktop index changed independently; preserve and inspect'
old={str(p.relative_to(DESKTOP)):sha(p) for p in DESKTOP.glob('*V2.*.zip')}
old.update({str(p.relative_to(DESKTOP)):sha(p) for p in (DESKTOP/'output/pdf').glob('*.pdf') if 'V2.4' not in p.name})
for x in json.loads((ROOT/'data/sources.json').read_text())['inputs']:
 p=DESKTOP/x['path'];assert p.is_file() and sha(p)==x['sha256'],'Preserve independently changed original: '+x['path']
files={'IMPLEMENTATION_1F_8F.html','START_HERE.html','BeePump_1F_8F_Implementation_V2.4_Source.zip','data/templates.json','data/tasks.json','docs/EXECUTION_CHECKLIST.md','preview/single_file_review.html','output/pdf/BeePump_1F_8F_Implementation_Design_V2.4.pdf','output/pdf/BeePump_1F_8F_SettingOut_Acceptance_Forms_V2.4.pdf','reports/IMPLEMENTATION_RESULT.md','reports/implementation_qa.json','reports/implementation_content_checks.json','reports/implementation_project_validation.json','reports/implementation_tests.txt','reports/implementation_pdf_visual_review.json','reports/implementation_pdf_visual_review.md','reports/implementation_cad_review.md','reports/implementation_package_verification.json','reports/implementation_index_archive.json'}
for folder in ['outputs/implementation_v2.4','design/v2/implementation_v2.4','design/v2/implementation_ops_v2.4','reports/implementation_template_render','reports/implementation_operations_render','reports/implementation_render','reports/implementation_pdf_render','reports/implementation_forms_render','reports/implementation_pdf_contacts','reports/implementation_forms_contacts']:
 for p in (ROOT/folder).rglob('*'):
  if p.is_file():files.add(str(p.relative_to(ROOT)))
for p in (ROOT/'scripts').glob('*implementation*'):
 if p.is_file():files.add(str(p.relative_to(ROOT)))
files.add('scripts/merge_review_pdf.swift');files.add('scripts/merge_vector_pdf.swift')
archive=DESKTOP/'archives/pre_V2.4';archived=[]
for rel in sorted(files):
 source=ROOT/rel;target=DESKTOP/rel
 assert source.is_file(),rel
 if target.exists() and sha(target)!=sha(source):
  saved=archive/rel;saved.parent.mkdir(parents=True,exist_ok=True)
  if saved.exists():assert sha(saved)==sha(target),'Previous archive differs: '+rel
  else:shutil.copy2(target,saved)
  archived.append({'path':rel,'previous_sha256':sha(target),'archive':str(saved.relative_to(DESKTOP))})
 target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(source,target);assert sha(target)==sha(source),rel
for rel,digest in old.items():assert sha(DESKTOP/rel)==digest,'Old deliverable overwritten: '+rel
for x in json.loads((ROOT/'data/sources.json').read_text())['inputs']:assert sha(DESKTOP/x['path'])==x['sha256']
report={'desktop':str(DESKTOP),'copied_file_count':len(files),'all_copied_hashes_match':True,'copied_paths':sorted(files),'archived_previous_files':archived,'old_zip_and_pdf_hashes_preserved':old,'original_inputs_preserved':48,'actual_point_coordinates_created':False,'opened_visible_apps':False,'production_release':False}
(ROOT/'reports/implementation_desktop_delivery.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
shutil.copy2(ROOT/'reports/implementation_desktop_delivery.json',DESKTOP/'reports/implementation_desktop_delivery.json')
print(json.dumps({k:v for k,v in report.items() if k not in ['copied_paths','old_zip_and_pdf_hashes_preserved']},ensure_ascii=False,indent=2))

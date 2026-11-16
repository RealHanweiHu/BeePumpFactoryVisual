"""Create a fresh, verified local delivery; never replace an existing directory."""
from pathlib import Path
import hashlib, json, shutil, subprocess, sys, zipfile

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT.parent/'deliverables'
STAGE=OUT/'BeePumpFactoryVisual'
ZIP=OUT/'BeePumpFactoryVisual_V2.1_Draft_Source.zip'
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,data): p.write_text(json.dumps(data,ensure_ascii=False,indent=2))
if STAGE.exists() or ZIP.exists(): raise SystemExit('Delivery target already exists; choose a fresh output path, preserve existing files.')
frozen=json.loads((ROOT/'data/sources.json').read_text())['inputs']
assert all(sha(ROOT/x['path'])==x['sha256'] for x in frozen), 'Immutable input mismatch'
qa=json.loads((ROOT/'reports/v2_render_qa.json').read_text())
assert qa['passed'] and qa['pdf']['pages']==18
OUT.mkdir(parents=True,exist_ok=True)
STAGE.mkdir()
omit=[]
keep_source_pages={'manual':{'page-007.png','page-009.png','page-057.png'},'reference':{'page-003.png','page-019.png'}}
for source in sorted(ROOT.rglob('*')):
    if not source.is_file(): continue
    if source.is_symlink(): raise SystemExit(f'Unexpected symlink: {source}')
    rel=source.relative_to(ROOT);s=rel.as_posix();reason=None
    if any(x in rel.parts for x in ['__pycache__','.git']): reason='Regenerable runtime cache / local Git metadata'
    elif source.name=='.DS_Store' or s=='acad.err': reason='Native runtime housekeeping; plot/export evidence is in reports'
    elif s in ['outputs/drawings/cad_entities.json','outputs/drawings/cad_blocks.json']: reason='Large parsed cache, regenerate with scripts/dxf_inventory_stdlib.py from included DXF'
    elif s.startswith('outputs/drawings/') and source.suffix.lower()=='.dwg': reason='Native working/recovery copy; immutable original DWG included'
    elif s.startswith('reports/final_pdf_render/'): reason='Earlier duplicate render; final CoreGraphics page PNGs included'
    elif s.startswith('reports/source_render/') and source.name.startswith('page-') and source.suffix=='.png':
        group=rel.parts[2]
        if group in keep_source_pages and source.name not in keep_source_pages[group]: reason='Additional rendered input page; full source PDF/text/page metadata and inspected key pages included'
    if reason:
        omit.append({'path':s,'reason':reason});continue
    dest=STAGE/rel;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(source,dest)
archives=[]
for filename in ['BeePump_Factory_Visual_Codex_Starter.zip','BeePump_Factory_Visual_Design_Package_V1.0.zip']:
    source=ROOT.parent/'inputs/library'/filename
    dest=STAGE/'source_archives'/filename;dest.parent.mkdir(exist_ok=True);shutil.copy2(source,dest)
    archives.append({'path':dest.relative_to(STAGE).as_posix(),'bytes':dest.stat().st_size,'sha256':sha(dest)})
save(STAGE/'reports/package_policy.json',{'original_inputs_preserved':len(frozen),'source_archives':archives,'excluded':omit,'cache_regeneration':'python3 scripts/dxf_inventory_stdlib.py','original_archive_policy':'Raw starter and V1 ZIP byte copies preserved; source PDFs and DWG also preserved separately.'})
r=subprocess.run([sys.executable,str(STAGE/'scripts/project.py'),'validate'],cwd=STAGE,text=True,capture_output=True,check=True)
v=json.loads(r.stdout);assert v['passed'];save(STAGE/'reports/delivery_validation.json',v)
assert all(sha(STAGE/x['path'])==x['sha256'] for x in frozen)
save(STAGE/'reports/handoff_scope.json',{'revision':'V2.1-DRAFT','frozen_inputs':len(frozen),'v1_templates_preserved':36,'new_svg_variants':6,'pdf_pages':18,'unlocated_intents':20,'actual_coordinates':'not_generated','physical_sign_quantities':None,'unit_tests':{'passed':17,'skipped_optional_ezdxf':2},'digital_qa_passed':True,'pdf_visual_check':'Rendered and visually inspected; not physical/site acceptance','remaining_gates':['8F body/titleblock floor conflict','Physical CAD unit and site dimensions','CAD font dependencies / reliable original vector plot','Official logo / content review / 1:1 samples','Installation and specialist acceptance']})
manifest=[{'path':p.relative_to(STAGE).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p)} for p in sorted(STAGE.rglob('*')) if p.is_file()]
save(STAGE/'FILE_MANIFEST.sha256.json',{'revision':'V2.1-DRAFT','self_excluded':True,'files':manifest})
with zipfile.ZipFile(ZIP,'x',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
    for p in sorted(STAGE.rglob('*')):
        if p.is_file():z.write(p,'BeePumpFactoryVisual/'+p.relative_to(STAGE).as_posix())
with zipfile.ZipFile(ZIP) as z:
    assert z.testzip() is None
    assert all(not n.startswith('/') and '..' not in Path(n).parts for n in z.namelist())
    for x in frozen:assert hashlib.sha256(z.read('BeePumpFactoryVisual/'+x['path'])).hexdigest()==x['sha256']
    for x in manifest:assert hashlib.sha256(z.read('BeePumpFactoryVisual/'+x['path'])).hexdigest()==x['sha256']
summary={'stage':str(STAGE),'zip':str(ZIP),'file_count':len(manifest)+1,'zip_bytes':ZIP.stat().st_size,'zip_sha256':sha(ZIP),'all_zip_crc_verified':True,'all_packaged_hashes_verified':True,'frozen_inputs_hash_verified':len(frozen),'excluded_count':len(omit)}
save(OUT/'packaging_result.json',summary)
print(json.dumps(summary,ensure_ascii=False,indent=2))

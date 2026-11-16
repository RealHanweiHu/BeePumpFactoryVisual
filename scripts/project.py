#!/usr/bin/env python3
"""Local project controls. No network calls; no CAD geometry is inferred."""
from __future__ import annotations
import argparse, base64, csv, hashlib, json, math, sys
from collections import Counter
from pathlib import Path
import xml.etree.ElementTree as ET
ROOT = Path(__file__).resolve().parents[1]


def read_json(path: Path):
    return json.loads(path.read_text(encoding='utf-8'))


def safe_path(root: Path, relative: str) -> Path:
    p = (root / relative).resolve()
    if not p.is_relative_to(root.resolve()):
        raise ValueError(f'Path escapes project: {relative}')
    return p


def finite(v) -> bool:
    return isinstance(v, (int, float)) and not isinstance(v, bool) and math.isfinite(v)


def matrix_ok(m) -> bool:
    return (isinstance(m, list) and len(m) == 6 and all(finite(v) for v in m)
            and abs(m[0] * m[3] - m[1] * m[2]) > 1e-12)


def approval_errors(point, root: Path):
    errors = []
    required = ['content', 'location', 'installation']
    if point.get('safety_related'):
        required.append('safety')
    for role in required:
        a = point.get('approvals', {}).get(role, {})
        if not all(a.get(k) for k in ('reviewer', 'approved_at', 'record_path')):
            errors.append(f'{point.get("point_id")}: missing {role} approval evidence')
            continue
        try:
            if not safe_path(root, a['record_path']).is_file():
                errors.append(f'{point.get("point_id")}: {role} evidence file missing')
        except ValueError as exc:
            errors.append(str(exc))
        if a.get('drawing_sha256') != point.get('source_drawing_sha256'):
            errors.append(f'{point.get("point_id")}: {role} approval drawing revision mismatch')
        if a.get('template_revision') != point.get('template_revision'):
            errors.append(f'{point.get("point_id")}: {role} approval template revision mismatch')
    return errors


def check_point(point: dict, floors: dict, templates: dict, root: Path):
    errors = []
    pid = point.get('point_id', '(missing id)')
    key = (point.get('template_code'), point.get('template_revision'))
    if key not in templates:
        errors.append(f'{pid}: unknown template/revision {key}')
    floor = floors.get(point.get('floor_id'))
    if floor is None:
        errors.append(f'{pid}: unknown floor'); return errors
    status = point.get('status')
    if status not in ('proposed', 'in_review', 'approved', 'rejected'):
        errors.append(f'{pid}: invalid status')
    quantity = point.get('quantity')
    if not isinstance(quantity, int) or isinstance(quantity, bool) or quantity <= 0:
        errors.append(f'{pid}: quantity must be positive whole physical signs')
    if point.get('faces') not in (1, 2) or isinstance(point.get('faces'), bool):
        errors.append(f'{pid}: faces must be 1 or 2, independent of quantity')
    if point.get('unit') != 'piece':
        errors.append(f'{pid}: current exporter supports signage pieces only; do not pass meters/area')
    p = point.get('position_world')
    if not isinstance(p, dict) or not finite(p.get('x')) or not finite(p.get('y')):
        errors.append(f'{pid}: coordinates must be finite CAD-world numbers, not placeholder pixels')
    if not finite(point.get('facing_degrees')):
        errors.append(f'{pid}: facing direction missing or invalid')
    if floor.get('calibration', {}).get('status') != 'verified':
        errors.append(f'{pid}: floor calibration not verified')
    if len(floor.get('calibration', {}).get('evidence', [])) < 2:
        errors.append(f'{pid}: need at least two calibration evidence entries')
    if floor.get('geometry_status') != 'verified':
        errors.append(f'{pid}: floor geometry not verified')
    if not floor.get('coordinate_unit') or not matrix_ok(floor.get('world_to_svg')):
        errors.append(f'{pid}: missing units or invertible world-to-SVG transform')
    source = point.get('source_drawing_sha256')
    if not source or source != floor.get('source_drawing_sha256'):
        errors.append(f'{pid}: floor/source drawing revision mismatch')
    if not point.get('evidence'):
        errors.append(f'{pid}: placement needs source evidence')
    if status == 'approved':
        if floor.get('site_status') != 'verified':
            errors.append(f'{pid}: site review not verified')
        if not finite(point.get('installation_height_mm')) or point['installation_height_mm'] <= 0:
            errors.append(f'{pid}: installation height missing')
        if not point.get('mounting_method') or not point.get('material_spec'):
            errors.append(f'{pid}: installation/material specification missing')
        errors += approval_errors(point, root)
    return errors


def validate(root: Path = ROOT):
    errors, warnings = [], []
    sources = read_json(root/'data/sources.json')
    for row in sources['inputs']:
        f = safe_path(root, row['path'])
        if not f.is_file():
            errors.append(f'Missing immutable input: {row["path"]}'); continue
        digest = hashlib.sha256(f.read_bytes()).hexdigest()
        if digest != row['sha256']:
            errors.append(f'Immutable source changed: {row["path"]}')
    registry = read_json(root/'data/templates.json')
    keys = [(r['code'], r['revision']) for r in registry]
    if len(keys) != len(set(keys)):
        errors.append('Duplicate template code/revision')
    for t in registry:
        try:
            f = safe_path(root, t['path']); xml = ET.parse(f).getroot()
            if xml.tag.rsplit('}', 1)[-1] != 'svg':
                errors.append(f'{t["code"]}: not SVG')
            if xml.attrib.get('width') != f'{t["w"]}mm' or xml.attrib.get('height') != f'{t["h"]}mm':
                errors.append(f'{t["code"]}: physical size differs from registry')
        except (OSError, ET.ParseError, ValueError) as exc:
            errors.append(f'{t["code"]}: {exc}')
    fs = read_json(root/'data/floors.json')
    if len({f['floor_id'] for f in fs}) != len(fs): errors.append('Duplicate floor ids')
    floors = {f['floor_id']:f for f in fs}
    rows = read_json(root/'data/points.json')['points']
    ids = [p.get('point_id') for p in rows]
    if None in ids or len(ids) != len(set(ids)): errors.append('Missing or duplicate point ids')
    for p in rows: errors += check_point(p, floors, {k:t for k,t in zip(keys,registry)}, root)
    if not rows: warnings.append('No points surveyed yet; empty is not zero site requirement.')
    for f in fs:
        if f['geometry_status'] != 'verified': warnings.append(f'{f["floor_id"]}: no verified geometry')
    lock = read_json(root/'third_party/taste-skill/provenance.json')
    for x in lock['files']:
        b = safe_path(root,x['local_path']).read_bytes()
        h = hashlib.sha1(f'blob {len(b)}\0'.encode()+b).hexdigest()
        if h != x['git_blob_sha1']: errors.append(f'Upstream Taste snapshot changed: {x["local_path"]}')
    tokens = read_json(root/'data/tokens.json')
    if tokens['brand']['orange'] != '#FF6600': errors.append('Brand orange drift')
    if tokens['floor_markings']['allow_brand_orange']: errors.append('Brand orange not permitted on floor markings')
    return {'passed':not errors,'errors':errors,'warnings':warnings,
            'scope':'File/data checks only; not drawing conversion, visual approval or safety sign-off.',
            'counts':{'templates':len(registry),'floor_baselines':len(fs),'points':len(rows),'frozen_files':len(sources['inputs'])}}


def summarize_quantities(points: list, mode: str):
    """Counts real pieces and faces separately; does NOT estimate a site total."""
    eligible = ('approved',) if mode == 'approved' else ('proposed','in_review','approved')
    counter = Counter()
    for p in points:
        if p['status'] in eligible:
            counter[(p['floor_id'],p['template_code'],p['template_revision'],p['status'],p['faces'])] += p['quantity']
    return [{'floor_id':f,'template_code':t,'revision':r,'status':s,'physical_signs':q,
             'faces_per_sign':n,'printed_faces':q*n,'unit':'piece'}
            for (f,t,r,s,n),q in sorted(counter.items())]


def quantity_export(root: Path, out: Path, mode: str):
    result = validate(root)
    if not result['passed']: raise ValueError('\n'.join(result['errors']))
    points = read_json(root/'data/points.json')['points']
    rows = summarize_quantities(points,mode)
    if not rows:
        raise ValueError('No eligible points: no BOQ total will be generated. This does not mean zero signs required.')
    if out.resolve().is_relative_to((root/'inputs').resolve()): raise ValueError('Cannot export over original inputs')
    out.parent.mkdir(parents=True,exist_ok=True)
    with out.open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f, fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    return rows


def build_preview(root: Path = ROOT):
    data = {k:read_json(root/p) for k,p in [('templates','data/templates.json'),('floors','data/floors.json'),
            ('tasks','data/tasks.json'),('points','data/points.json'),('intake','reports/cad_intake.json')]}
    for t in data['templates']:
        t['svg_data_url'] = 'data:image/svg+xml;base64,' + base64.b64encode(safe_path(root,t['path']).read_bytes()).decode()
    data['project']='BeePump Factory Visual'
    # Escape script boundaries even though current source is trusted original data.
    payload=json.dumps(data,ensure_ascii=False).replace('<','\\u003c').replace('\u2028','\\u2028').replace('\u2029','\\u2029')
    (root/'preview/data.js').write_text('window.BEEPUMP_DATA = '+payload+';\n',encoding='utf-8')
    html=(root/'preview/index.html').read_text()
    html=html.replace('<link rel="stylesheet" href="style.css">','<style>'+(root/'preview/style.css').read_text()+'</style>')
    html=html.replace('<script src="data.js"></script>','<script>window.BEEPUMP_DATA = '+payload+';</script>')
    html=html.replace('<script src="app.js"></script>','<script>'+(root/'preview/app.js').read_text()+'</script>')
    (root/'preview/single_file_review.html').write_text(html,encoding='utf-8')
    return root/'preview/single_file_review.html'


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    sub=parser.add_subparsers(dest='command',required=True)
    sub.add_parser('validate');sub.add_parser('build-preview')
    q=sub.add_parser('quantities');q.add_argument('--mode',choices=['proposal','approved'],required=True);q.add_argument('--out',type=Path,required=True)
    a=parser.parse_args()
    try:
        if a.command=='validate':
            r=validate();print(json.dumps(r,ensure_ascii=False,indent=2));return 0 if r['passed'] else 2
        if a.command=='build-preview': print(build_preview());return 0
        rows=quantity_export(ROOT,a.out,a.mode);print(f'Exported {len(rows)} quantity groups');return 0
    except (OSError, ValueError, KeyError, json.JSONDecodeError) as exc:
        print(f'ERROR: {exc}',file=sys.stderr);return 2

if __name__=='__main__': raise SystemExit(main())

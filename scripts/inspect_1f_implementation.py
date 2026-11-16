"""Traceable partial CAD source review. No point creation, unit approval, or input edits.

Uses existing native DXF/cache and the project's stdlib renderer approach.
All writes are limited to outputs/implementation_v2.4/cad.
"""
from pathlib import Path
import collections
import csv
import hashlib
import html
import json
import math
import re

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'outputs/drawings'
OUT = ROOT / 'outputs/implementation_v2.4/cad'
GROUPS = [('A', 'B224C', 'B158F', 'B1552', -180000),
          ('B', '3EB99', '3C8CE', '3C823', 0),
          ('C', 'B4244', 'B358B', 'B354E', 180000)]


def one(e, c, default=None):
    return next((v for k, v in e if k == c), default)


def num(e, c, default=0):
    try:
        return float(one(e, c, default))
    except (ValueError, TypeError):
        return default


def point(e, c=10):
    return num(e, c), num(e, c + 10)


def vertices(e):
    rows = []
    for c, v in e:
        if c == 10:
            rows.append([float(v), 0])
        elif c == 20 and rows:
            rows[-1][1] = float(v)
    return rows


def apply(pt, m):
    x, y = pt
    a, b, c, d, tx, ty = m
    return a*x + c*y + tx, b*x + d*y + ty


def compose(m, n):
    a, b, c, d, x, y = m
    A, B, C, D, X, Y = n
    return [a*A+c*B, b*A+d*B, a*C+c*D, b*C+d*D, a*X+c*Y+x, b*X+d*Y+y]


def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(1024*1024), b''):
            h.update(chunk)
    return h.hexdigest()


def inside(position, window):
    return bool(position) and window[0] <= position[0] <= window[2] and window[1] <= position[1] <= window[3]


def raw_text(e):
    return ''.join(v for c, v in e if c == 3) + str(one(e, 1, ''))


def source_anchor(t):
    return {'handle': t['handle'], 'entity_type': t['type'], 'layer': t['layer'],
            'source_text_verbatim': t['text'], 'source_text_anchor_world_unverified_units': t['position'],
            'height_source_units': t['height'], 'rotation_degrees': t['rotation'], 'style': t['style'],
            'is_installation_coordinate': False, 'site_verified': None}


class PartialRenderer:
    def __init__(self, entities, blocks, window, preview_id, provenance):
        self.entities, self.blocks, self.window = entities, blocks, window
        self.preview_id, self.provenance = preview_id, provenance
        self.scale = 2200 / (window[2] - window[0])
        self.width, self.height = 2200, (window[3] - window[1]) * self.scale
        self.matrix = [self.scale, 0, 0, -self.scale, -window[0]*self.scale, window[3]*self.scale]
        self.inverse = [1/self.scale, 0, 0, -1/self.scale, window[0], window[3]]
        self.fragments, self.omitted = [], collections.Counter()

    def visible(self, pts):
        x0, y0, x1, y1 = self.window
        return pts and max(x for x, y in pts) >= x0 and min(x for x, y in pts) <= x1 and max(y for x, y in pts) >= y0 and min(y for x, y in pts) <= y1

    def path(self, pts, closed=False):
        if not self.visible(pts):
            return
        pairs = [apply(p, self.matrix) for p in pts]
        path = 'M' + ' L'.join(f'{x:.3f},{y:.3f}' for x, y in pairs) + (' Z' if closed else '')
        self.fragments.append('<path d="' + path + '"/>')

    def render(self, e, matrix, depth=0):
        if depth > 10:
            self.omitted['block_recursion_depth_limit'] += 1
            return
        kind = one(e, 0)
        if kind == 'LINE':
            self.path([apply(point(e, 10), matrix), apply(point(e, 11), matrix)])
        elif kind == 'LWPOLYLINE':
            if any(c == 42 and abs(float(v)) > 1e-10 for c, v in e):
                self.omitted['polyline_bulge_approximated_as_chord'] += 1
            self.path([apply(p, matrix) for p in vertices(e)], bool(int(num(e, 70)) & 1))
        elif kind in ('CIRCLE', 'ARC'):
            x, y = point(e)
            radius = num(e, 40)
            a, z = (num(e, 50), num(e, 51)) if kind == 'ARC' else (0, 360)
            if z < a:
                z += 360
            self.path([apply((x+radius*math.cos(math.radians(a+(z-a)*i/80)),
                              y+radius*math.sin(math.radians(a+(z-a)*i/80))), matrix) for i in range(81)], kind == 'CIRCLE')
        elif kind in ('SOLID', 'TRACE'):
            self.path([apply(point(e, c), matrix) for c in (10, 11, 13, 12)], True)
        elif kind == 'INSERT':
            block = self.blocks.get(one(e, 2))
            if not block:
                self.omitted['missing_block'] += 1
                return
            angle = math.radians(num(e, 50))
            sx, sy = num(e, 41, 1), num(e, 42, 1)
            x, y = point(e)
            bx, by = block['base'][:2]
            n = [sx*math.cos(angle), sx*math.sin(angle), -sy*math.sin(angle), sy*math.cos(angle),
                 x-bx*sx*math.cos(angle)+by*sy*math.sin(angle), y-bx*sx*math.sin(angle)-by*sy*math.cos(angle)]
            if num(e, 70, 1) > 1 or num(e, 71, 1) > 1:
                self.omitted['insert_array_repetition_not_expanded'] += 1
            for child in block['entities']:
                self.render(child, compose(matrix, n), depth + 1)
        elif kind == 'DIMENSION':
            block = self.blocks.get(one(e, 2))
            if not block:
                self.omitted['missing_dimension_block'] += 1
            else:
                for child in block['entities']:
                    self.render(child, matrix, depth + 1)
        elif kind in ('TEXT', 'MTEXT', 'ATTRIB', 'ATTDEF'):
            anchor = apply(point(e), matrix)
            if not inside(anchor, self.window):
                return
            text = re.sub(r'\\[A-Za-z][^;]*;', '', raw_text(e).replace('\\P', ' ')).replace('{', '').replace('}', '')
            text = text.replace('%%P', '±').replace('%%p', '±').replace('%%C', 'Ø').replace('%%c', 'Ø').replace('%%D', '°').replace('%%d', '°')
            if not text:
                return
            x, y = apply(anchor, self.matrix)
            height = num(e, 40, 200)*self.scale*math.hypot(matrix[0], matrix[1])
            angle = -num(e, 50)-math.degrees(math.atan2(matrix[1], matrix[0]))
            self.fragments.append(f'<text x="{x:.3f}" y="{y:.3f}" font-size="{height:.3f}" transform="rotate({angle:.3f},{x:.3f},{y:.3f})" style="stroke:none;fill:#000000;font-family:PingFang SC,Arial,sans-serif">{html.escape(text)}</text>')
        elif kind not in ('SEQEND', 'POINT'):
            self.omitted[kind] += 1

    def save(self, name, extra):
        for e in self.entities:
            self.render(e, [1, 0, 0, 1, 0, 0])
        warnings = [
            '资料核查局部预览；不能量取、定位安装或按打印比例施工。',
            '省略HATCH、SPLINE、ELLIPSE及传统POLYLINE/VERTEX；轻量多段线弧段以弦近似，圆弧采样。',
            '缺原CAD字体；系统中文字体替代，文字对齐/宽度/换行不保证与原生出图一致。',
            '二维投影；没有复现图层开关、颜色、线型、出图样式、SOLID填充和完整OCS/纸空间配置。',
            '遗漏计数是全缓存递归遍历计数，不是本窗口缺件数；空白不能证明现场空地。',
            '保留原源坐标关系；没有移动任何建筑/电梯/消防结构，也没有绘安装点。']
        meta = dict(self.provenance, preview_id=self.preview_id, status='partial_source_preview_not_calibrated',
                    source_window_world_unverified_units=self.window, world_to_display=self.matrix,
                    display_to_world=self.inverse, display_viewbox=[0, 0, self.width, self.height],
                    physical_unit_verified=False, mm_factor=None, floor_identity_confirmed=None,
                    source_title_selection_is_site_version_approval=False, is_installation_coordinate=False,
                    approved_scale=None, approved_installation_position=None, rendered_primitives=len(self.fragments),
                    unsupported_or_approximation_counts_global=dict(self.omitted), warnings=warnings, **extra)
        clip = self.preview_id + '-crop'
        svg = f'<svg id="{self.preview_id}" xmlns="http://www.w3.org/2000/svg" width="{self.width}" height="{self.height}" viewBox="0 0 {self.width} {self.height}"><title>{html.escape(extra["display_title"])}</title><metadata>{html.escape(json.dumps(meta, ensure_ascii=False))}</metadata><rect width="100%" height="100%" fill="#ffffff"/><defs><clipPath id="{clip}"><rect width="{self.width}" height="{self.height}"/></clipPath></defs><g clip-path="url(#{clip})" fill="none" stroke="#000000" stroke-width="0.65">' + ''.join(self.fragments) + '</g></svg>'
        (OUT / (name + '.svg')).write_text(svg, encoding='utf-8')
        write_json(name + '_metadata.json', meta)
        return meta


def write_json(name, data):
    (OUT / name).write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    tracked = [ROOT/'inputs/cad/新厂房平面图（改）.dwg', ROOT/'data/floors.json', ROOT/'data/points.json']
    before = {str(p.relative_to(ROOT)): digest(p) for p in tracked}
    entities = json.loads((SOURCE/'cad_entities.json').read_text())
    blocks = json.loads((SOURCE/'cad_blocks.json').read_text())
    texts = json.loads((SOURCE/'cad_texts.json').read_text())
    dimensions = json.loads((SOURCE/'cad_dimensions.json').read_text())
    inventory = json.loads((SOURCE/'cad_inventory.json').read_text())
    text_by = {t['handle']: t for t in texts}
    entity_by = {one(e, 5): e for e in entities}
    provenance = {'source_drawing': 'inputs/cad/新厂房平面图（改）.dwg',
                  'source_drawing_sha256': before['inputs/cad/新厂房平面图（改）.dwg'],
                  'native_dxf': 'outputs/drawings/factory_converted.dxf',
                  'native_dxf_sha256': digest(SOURCE/'factory_converted.dxf'),
                  'cache_inputs': {f: digest(SOURCE/f) for f in ['cad_texts.json', 'cad_entities.json', 'cad_blocks.json', 'cad_dimensions.json', 'cad_inventory.json']},
                  'unit_header': inventory['header'], 'physical_unit_label': '待工程核验，源单位不是已确认mm'}
    candidates, signatures = [], []
    for group, body, title, frame, offset in GROUPS:
        e = entity_by[frame]
        vs = vertices(e)
        bb = [min(x for x,y in vs), min(y for x,y in vs), max(x for x,y in vs), max(y for x,y in vs)]
        window = [bb[0]-1000, bb[1]-1000, bb[2]+1000, bb[3]+1000]
        sample = [810000+offset, 125000, 950000+offset, 229000]
        local = [t for t in texts if inside(t['position'], bb)]
        sampled = [t for t in texts if inside(t['position'], sample)]
        sig = {(t['text'], t['layer'], round(t['position'][0]-offset, 3), round(t['position'][1], 3)) for t in sampled}
        signatures.append(sig)
        row = {'candidate_id': '1F-' + group, 'role': '资料评审优先候选' if group == 'C' else '保留对照候选',
               'body_title': source_anchor(text_by[body]), 'title_block_title': source_anchor(text_by[title]),
               'frame': {'handle': frame, 'entity_type': one(e, 0), 'layer': one(e, 8), 'closed': bool(int(num(e, 70)) & 1),
                         'source_vertices_world_unverified_units': vs, 'source_bbox_world_unverified_units': bb},
               'source_text_sampling_window_unverified_units': sample, 'source_frame_text_count': len(local),
               'source_sample_text_count': len(sampled), 'baseline_use': '金工、出货、主入口（V1待对照基线）',
               'floor_identity_confirmed': None, 'site_valid_revision': None, 'date_value': None, 'revision_value': None,
               'selection_reason': '同类建筑文字外另有45条工艺/仓储文字，利于分区内容讨论；不表示更新或现场采用' if group == 'C' else '与中组98条采样文字平移一致，保留版本对照',
               'source_anchor_records': [source_anchor(t) for t in local],
               'actual_capacity_area_equipment_quantity': None,
               'numeric_source_labels_are_approved_site_quantities': False}
        candidates.append(row)
        meta = PartialRenderer(entities, blocks, window, 'bp-source-1f-' + group.lower(), provenance).save(
            '1F_candidate_' + group + '_partial', {'display_title': f'1F候选{group}：部分源图核查，单位/有效版本待核', 'candidate_id': row['candidate_id'], 'body_handle': body, 'title_block_handle': title, 'frame_handle': frame})
        row['preview_file'] = '1F_candidate_' + group + '_partial.svg'
        row['metadata_file'] = '1F_candidate_' + group + '_partial_metadata.json'
        row['source_preview_window_world_unverified_units'] = window
        row['world_to_display'] = meta['world_to_display']
    common = set.intersection(*signatures)
    extras = sorted(signatures[2] - common)
    comparison = dict(provenance, status='source_candidate_review_only', selected_for_review='1F-C',
                      selected_site_valid_version=None, source_text_common_count=len(common),
                      right_candidate_additional_text_count=len(extras),
                      comparison_key='verbatim text, layer, source X normalized by +/-180000, source Y; rounded to 0.001 source units',
                      comparison_is_complete_geometry_equivalence=False,
                      title_x_translation_source_units=[-180000, 0, 180000],
                      frame_width_source_units=[r['frame']['source_bbox_world_unverified_units'][2]-r['frame']['source_bbox_world_unverified_units'][0] for r in candidates],
                      candidates=candidates,
                      right_additional_signatures=[{'source_text_verbatim': t, 'layer': l, 'normalized_source_xy_unverified_units': [x,y]} for t,l,x,y in extras],
                      excluded_neighbor_title_records=[source_anchor(text_by[h]) for h in ['3EB40','3EB95','3171C','3164F','31725','3E6FD','3F224','3F3A7']],
                      implementation_exclusions=['未核准的源文字锚点不能用作标牌安装坐标。', '门扇/门框、货客梯门/按钮/前室、楼梯/扶手、消防救援口及设施、消控/配电空间的门/检修面不作为已授权安装承载面。', '作业设备、料架、库位和空白区域的可用安装面/动线均须现场核查，未推定许可。'])
    write_json('1F_candidate_comparison.json', comparison)
    fields = ['candidate_id', 'handle', 'entity_type', 'layer', 'source_text_verbatim', 'source_text_anchor_world_unverified_units', 'height_source_units', 'rotation_degrees', 'style', 'is_installation_coordinate', 'site_verified']
    with (OUT/'1F_source_text_inventory.csv').open('w', encoding='utf-8-sig', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for c in candidates:
            for t in c['source_anchor_records']:
                row = dict(t, candidate_id=c['candidate_id'])
                row['source_text_anchor_world_unverified_units'] = json.dumps(row['source_text_anchor_world_unverified_units'])
                writer.writerow(row)
    selected_dimensions = []
    for handle, axis in [('B4248','X'), ('B4218','Y')]:
        d = next(d for d in dimensions if d['handle'] == handle)
        anns = [raw_text(e) for e in blocks[d['block']]['entities'] if one(e, 0) in ('TEXT','MTEXT')]
        projected = abs(d['definition_2'][0 if axis == 'X' else 1]-d['definition_1'][0 if axis == 'X' else 1])
        selected_dimensions.append(dict(d, axis=axis, annotation_raw=anns, projected_length_world=projected,
                                        projected_measurement_error_world=abs(d['measurement']-projected),
                                        coordinate_unit_verified=False, physical_length_mm=None,
                                        note='自身标注与几何投影数值一致；不是现场尺寸或物理单位校准'))
    write_json('1F_numeric_consistency_units_pending.json', dict(provenance, status='numeric_consistency_only',
               selected_candidate='1F-C', two_axes=selected_dimensions, mm_factor=None, floor_identity_confirmed=None,
               reviewer=None, approved_at=None))
    old_obs = json.loads((SOURCE/'8F_drawing_observations.json').read_text())
    mismatches = [o['handle'] for o in old_obs['observations'] if text_by.get(o['handle']) != o]
    assert not mismatches, mismatches
    old_calibration = json.loads((SOURCE/'8F_candidate_calibration.json').read_text())
    old_meta = json.loads((SOURCE/'8F_render_limitations.json').read_text())
    eight_meta = PartialRenderer(entities, blocks, old_meta['window_world'], 'bp-source-8f-existing', provenance).save(
        '8F_existing_candidate_partial', {'display_title': '8F现有候选部分源图：八层图身/三层图签冲突待核',
        'floor_title_conflict': old_calibration['floor_title_conflict'], 'source_fact_scope': '复核既有证据，无新增现场事实'})
    write_json('8F_evidence_recheck.json', dict(provenance, status='existing_source_evidence_rechecked_no_new_site_facts',
               observation_count=len(old_obs['observations']), all_cached_observation_records_equal=True,
               observations=[source_anchor(t) for t in old_obs['observations']],
               title_conflict=old_calibration['floor_title_conflict'], numeric_consistency=old_calibration['two_axes'],
               existing_preview_transform_unchanged_window=True, new_preview_metadata='8F_existing_candidate_partial_metadata.json',
               existing_preview_window=old_meta['window_world'], mm_factor=None, floor_identity_confirmed=None,
               is_installation_coordinate=False, actual_area_mapping=None, actual_elevator_selection=None,
               note='电子仓不自动映射外采电池包存放；成品区不自动确认整层成品仓。'))
    wanted = set(entity_by[h] and h for h in ['B224C','B158F','3EB99','3C8CE','B4244','B358B','B1552','3C823','B354E','B4248','B4218','F0FBF','F10B1','F112C','F1112'])
    native_checked, record = {}, []
    with (SOURCE/'factory_converted.dxf').open(encoding='utf-8', errors='strict') as f:
        while True:
            a = f.readline()
            if not a:
                break
            b = f.readline().rstrip('\r\n')
            code = int(a.strip())
            if code == 0 and record:
                handle = one(record, 5)
                if handle in wanted:
                    decoded = [[c, re.sub(r'\\U\+([0-9A-Fa-f]{4})', lambda m: chr(int(m[1],16)),v)] for c,v in record]
                    native_checked[handle] = {'native_record_equals_cache': decoded == entity_by[handle], 'type': one(record,0)}
                record = []
            record.append((code,b))
    assert set(native_checked) == wanted and all(r['native_record_equals_cache'] for r in native_checked.values())
    after = {str(p.relative_to(ROOT)): digest(p) for p in tracked}
    assert before == after
    roundtrip_max = 0
    for c in candidates:
        m = c['world_to_display']
        meta = json.loads((OUT/c['metadata_file']).read_text())
        for t in c['source_anchor_records']:
            xy = t['source_text_anchor_world_unverified_units'][:2]
            back = apply(apply(xy,m), meta['display_to_world'])
            roundtrip_max = max(roundtrip_max, max(abs(back[i]-xy[i]) for i in range(2)))
    verification = {'status': 'source_evidence_checks_passed_not_installation_release', 'original_inputs_and_floor_point_files_unchanged': before == after,
                    'tracked_hashes_before': before, 'tracked_hashes_after': after, 'native_dxf_handle_verification': native_checked,
                    'affine_roundtrip_max_error_source_units': roundtrip_max,
                    'source_title_records': 6, 'source_candidate_groups': 3, 'source_text_common_count': len(common),
                    'right_candidate_additional_text_count': len(extras), 'rendered_previews': [c['preview_file'] for c in candidates]+['8F_existing_candidate_partial.svg'],
                    'png_visual_review': None, 'real_installation_points_created': 0,
                    'approval_created': False, 'physical_unit_verified': False}
    write_json('cad_verification.json', verification)
    (OUT/'README.md').write_text('''# 1F / 8F 源图证据深化（V2.4资料评审）

1F六标题分成三组图身/图签；右组C仅优先用于资料评审，并列保留A/B。三组局部采样文字平移一致98条，C多45条；图框宽度不同，不等于几何全同或版本先后。

四幅SVG/PNG为黑白部分源图预览。来源、图框实体、窗口、可逆变换和限制见各metadata JSON。预览没有标牌点位；source文字XY只是检索原图实体的锚点。图框窗口、源尺寸数值与原文字中的480/150/100等不能当现场容量、面积、毫米或制作数量。

8F只复核既有证据；八层图身/三层图签仍冲突，电子仓不自动等于电池仓。实际楼层、版本、单位、安装面、读面、动线、载荷及专项均待现场和责任人复核。

`1F_candidate_comparison.json`：三组标题、框、文字清单、区别及邻图排除。CSV为同内容可编辑索引；源XY单位待核。
`1F_numeric_consistency_units_pending.json`：X/Y源标注数值一致性，不是物理校准。
`8F_evidence_recheck.json`：既有文字/尺寸证据，不增加现场事实。
`cad_verification.json`：原始文件/points/floors哈希、15个原生DXF实体核查与可逆变换自验。

渲染省略填充、样条、椭圆等；原CAD字体缺失，系统中文字体替代；未复现图层开关/出图样式和完整二维投影设置。留白不能证明空地。不要从这些PNG量取或施工。
''', encoding='utf-8')
    print(json.dumps({k: verification[k] for k in ['status','source_candidate_groups','source_text_common_count','right_candidate_additional_text_count','affine_roundtrip_max_error_source_units','original_inputs_and_floor_point_files_unchanged']}, ensure_ascii=False))


if __name__ == '__main__':
    main()

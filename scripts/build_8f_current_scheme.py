#!/usr/bin/env python3
"""Consolidate existing 8F review assets; do not change geometry or preferences."""
import csv
import hashlib
import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DAY = '2026-10-26'
REV = '8F-CONSOLIDATED-2026-10-26-DRAFT'

def read(name):
    return json.loads((ROOT / name).read_text())

def dump(name, obj):
    p = ROOT / name
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + '\n')

def esc(s):
    return html.escape(str(s), quote=True)

def main():
    catalogue_path = '交付_8楼/多方案选择_V2.8/方案目录.json'
    ground_path = '交付_8楼/地面物流规划_V3.1/地面配色与来源.json'
    process_path = 'data/8F_logistics_user_requirements_v2.9.1.json'
    lift_path = '交付_8楼/地面物流规划_V3.0/用户确认_收发电梯与直接标图.json'
    source_paths = [catalogue_path, ground_path, process_path, lift_path,
                    '交付_8楼/客梯入口修订_V2.7/修订记录与来源_V2.7.json',
                    '交付_8楼/specs/material_families.json', '交付_8楼/安装需求与实施接口.csv']
    catalogue = read(catalogue_path)
    ground = read(ground_path)
    process = read(process_path)
    with (ROOT / '交付_8楼/安装需求与实施接口.csv').open(encoding='utf-8-sig') as f:
        interfaces = {r['设计需求编号']: r for r in csv.DictReader(f)}
    groups = [
        {'id': 'G1', 'name': '入口、区域与方向', 'details': ['D01','D02','D03','D16'],
         'action': '对照最新电梯分工，明确区域名称、入口读面、柱号和分岔信息。'},
        {'id': 'G2', 'name': '生产运行与线边管理', 'details': ['D04','D05','D06','D07'],
         'action': '先定六款核心模板的共用样式、数据字段、更新人和状态规则。'},
        {'id': 'G3', 'name': '作业、品质与交接', 'details': ['D08','D09','D10','D12','D13','D14','D19','D21'],
         'action': '逐项落实受控文件、设备/容器身份、品质签发和交接动作。'},
        {'id': 'G4', 'name': '条件项与展示', 'details': ['D11','D15','D17','D18','D20'],
         'action': '先核适用性与获准范围；D15/D18/D20的来源位置仍未定位。'}]
    group_by_detail = {d: g for g in groups for d in g['details']}
    first_batch = ['D02','D03','D04','D05','D06','D07']
    special = {
        'D01': '员工与访客分别到层；客梯画面沿用V2.7，员工起点以V3.0/V3.1更新。',
        'D11': '按实际工单核测试/老化适用性，不能把所有机型都列为老化。',
        'D13': '成品下楼目标为左上梯；接驳门口与C2边界待核。',
        'D15': '未定位；先核获准观察面、陪同范围及停留位置。',
        'D16': '以V3.1当前路线关系核箭头；不直接复制旧版物流箭头。',
        'D17': '条件项；先核真实电子进入要求及适用专业。',
        'D18': '未定位、条件项；外采完整电池包，暂存条件和位置待专业确认。',
        'D20': '未定位；核样件/报告范围与负责角色，不编造验证能力。'}
    requirements = []
    for row in catalogue['requirements']:
        did, rid = row['detail_id'], row['requirement_id']
        upstream = interfaces[rid]
        requirements.append({
            'detail_id': did, 'requirement_id': rid, 'name': row['name'],
            'work_group': group_by_detail[did]['name'],
            'first_batch_recommendation': did in first_batch,
            'template_codes': [x['code'] for x in row['template_references']],
            'nominal_template_sizes_mm': [
                {'code': x['code'], 'size_mm': x.get('nominal_size_mm'),
                 'scope': 'nominal template only; not surveyed manufacturing size'}
                for x in row['template_references']],
            'source_anchor_id': row['source_anchor_id'],
            'source_anchor_is_actual_point': False,
            'responsible_roles': upstream['责任角色'],
            'reading_action': upstream['阅读后动作'],
            'next_action': special.get(did, upstream['更新规则']),
            'site_check': upstream['现场核对'],
            'selection_import_status': 'no_verified_human_selection_imported_into_this_summary',
            'selected_style': None, 'selected_position_relation': None,
            'selection_notes': None, 'position_world': None,
            'actual_quantity': None, 'actual_size_mm': None,
            'installation_height_mm': None, 'approvals': None,
            'production_release': False})
    gates = [
        {'id':'F01','name':'有效底图与比例','status':'blocked',
         'action':'工程核图身“八层”与图签“三层”冲突；确认有效图框、单位、两向校准与现场一致性。',
         'roles':'业主、工程','evidence':'docs/CAD_WORKFLOW.md'},
        {'id':'F02','name':'物流与员工走段','status':'pending_site_review',
         'action':'逐段核C1访客交叉、C2左上梯门口、C3中间梯分流及P02员工后续更衣/进入；量人工车，登记未来电动车型与转弯需求。',
         'roles':'生产、工程、安全','evidence':ground_path},
        {'id':'F03','name':'牌面样式与真实内容','status':'ready_for_design_review',
         'action':'先审WF-02/WF-04/WH-01/PM-01/PM-02/FL-01，再完成其余需求；从V2.8导出真实选择，核区域/资产/批次ID与更新责任。',
         'roles':'设计负责人、生产、品质、技术；访客内容由销售参与','evidence':catalogue_path},
        {'id':'F04','name':'安装面、量尺与打样','status':'pending_site_review',
         'action':'同次踏勘记录真实墙/柱/架/工位、朝向、尺寸、高度、固定、材质和1:1试样；专项条件由对应角色确认。',
         'roles':'工程、生产、品质、安全','evidence':'交付_8楼/specs/blank_setting_out.csv'},
        {'id':'F05','name':'核量、报价与制作安装','status':'not_released',
         'action':'实际放样后分配point_id；实物件数、面数、耗材备品与地面长度/面积分别核量，报价与具名批准闭合后另发制作安装稿。',
         'roles':'工程、生产、品质、安全、业主','evidence':'交付_8楼/specs/quotation_scope.csv'}]
    versions = [
        {'purpose':'地面物流、人行与定置配色','version':'V3.1','path':'地面物流规划_V3.1/打开地面配色图.html',
         'scope':'当前配色提案；色带宽度是显示像素，实际尺寸未核。'},
        {'purpose':'原图接驳、路线关系与来源','version':'V3.0','path':'地面物流规划_V3.0/打开原图标注.html',
         'scope':'保留L/P/C/E关系及用户电梯分工；颜色显示以V3.1为准。'},
        {'purpose':'逐项牌面与位置关系选型','version':'V2.8','path':'多方案选择_V2.8/START_HERE.html',
         'scope':'A/B/C与P1/P2/P3可独立选；旧人流/物流图须对照V3.1。'},
        {'purpose':'小客梯位置与到层入口画面','version':'V2.7','path':'客梯入口修订_V2.7/START_HERE.html',
         'scope':'替代V2.5/V2.6对应入口画面；后续员工/物流分工以V3.0/V3.1为准。'},
        {'purpose':'材料、报价、打样及现场表','version':'V2.4','path':'START_HERE.html',
         'scope':'保留实施交接框架；真实点位/尺寸/数量与制作安装仍待核。'},
        {'purpose':'名义尺寸、早期图纸标注','version':'V2.6 / V2.5','path':'逐项样式尺寸_参观预览_V2.6/START_HERE.html',
         'scope':'历史参考；入口和人流物流内容不可覆盖后续修订。'}]
    plan = {
        'revision': REV, 'status': 'draft_consolidation_of_existing_designs',
        'updated_on': DAY, 'floor_id': '8F', 'production_release': False,
        'user_priority': '先完成8F方案；1F及其余楼层保留现有成果，暂不扩展设计。',
        'scope': '方案整理、引用和推进清单；不新增几何、不代选偏好、不核定工程量。',
        'confirmed_for_planning': {
            'current_transport': process['current_transport']['value'],
            'future_transport': '考虑电动搬运车，预留意向已确认；车型和尺寸未知。',
            'process': process['process']['value'],
            'lift_roles': read(lift_path)['lift_roles'],
            'scope': '复用既有用户确认，只用于规划；不等于通路、专项条件或安装批准。'},
        'current_floor_palette_proposal': ground['palette'],
        'source_records': [{'path': p, 'sha256': hashlib.sha256((ROOT/p).read_bytes()).hexdigest()} for p in source_paths],
        'source_drawing_sha256': ground['source_drawing_sha256'],
        'versions': versions, 'work_groups': groups,
        'recommended_first_batch_details': first_batch,
        'recommendation_is_human_selection': False,
        'requirements': requirements, 'closure_gates': gates,
        'unresolved_source_items': ground['unresolved'],
        'physical_unit': None, 'actual_quantities': None,
        'actual_cad_points': [], 'actual_cad_points_note': '未勘测，空数组不是零需求。',
        'preferences_note': '本汇总未导入已核实的用户选择。V2.8浏览器可能已有本机选择，请在原页导出；本脚本不读取或重置浏览器存储。reports内QA测试导出不作为用户选择。'}
    point_manifest_path = ROOT/'design/v2/point_effects_2026-10-26/manifest.json'
    is_point_gallery = point_manifest_path.is_file()
    effect_manifest_path = point_manifest_path if is_point_gallery else ROOT/'design/v2/effect_previews_2026-10-26/manifest.json'
    effect_gallery_path = '交付_8楼/逐点效果与功能优化_2026-10-26/打开这里.html' if is_point_gallery else '交付_8楼/效果预览_2026-10-26/打开效果预览.html'
    if effect_manifest_path.is_file():
        plan['effect_previews'] = {
            'manifest_path': str(effect_manifest_path.relative_to(ROOT)),
            'manifest_sha256': hashlib.sha256(effect_manifest_path.read_bytes()).hexdigest(),
            'gallery_path': effect_gallery_path,
            'scope': 'Generated local concept scenes; not site photographs, CAD reconstruction or selected A/B/C designs.',
            'production_release': False}
    supplement_manifest_path = 'design/v2/8f_reference_supplement_v3.2/manifest.json'
    supplement_path = '点位补充_V3.2/打开这里.html'
    supplement = None
    if (ROOT / supplement_manifest_path).is_file() and (ROOT / '交付_8楼' / supplement_path).is_file():
        supplement = read(supplement_manifest_path)
        plan['reference_supplement'] = {
            'revision': supplement['revision'],
            'updated_on': supplement['updated_on'],
            'path': f'交付_8楼/{supplement_path}',
            'manifest_path': supplement_manifest_path,
            'survey_rows': supplement['survey_rows'],
            'mapped_candidates': supplement['mapped_candidates'],
            'unplaced_candidates': supplement['unplaced_candidates'],
            'reference_rows': supplement['reference_rows'],
            'production_release': False}
    partition_manifest_path = 'design/v2/8f_partition_v3.4/manifest.json'
    partition_path = '围板设计_V3.4/打开这里.html'
    partition = None
    if (ROOT / partition_manifest_path).is_file() and (ROOT / '交付_8楼' / partition_path).is_file():
        partition = read(partition_manifest_path)
        plan['partition_supplement'] = {
            'revision': partition['revision'],
            'updated_on': partition['date'],
            'path': f'交付_8楼/{partition_path}',
            'manifest_path': partition_manifest_path,
            'module_count': partition['module_count'],
            'production_release': False}
    dump('data/8F_current_scheme.json', plan)
    csvpath = ROOT / 'outputs/planning/8F_方案收口清单.csv'
    fields = ['详图编号','需求ID','需求名称','工作组','首批建议','模板代码','来源核对编号','名义模板尺寸','样式选择','位置关系选择','责任角色','下一步','现场核对','实际尺寸','安装高度','实物数量','真实点位ID','制作安装状态']
    with csvpath.open('w', encoding='utf-8-sig', newline='') as f:
        w = csv.DictWriter(f, fieldnames=fields); w.writeheader()
        for r in requirements:
            sizes = '；'.join(f"{x['code']} {x['size_mm'][0]}×{x['size_mm'][1]}mm（名义）" for x in r['nominal_template_sizes_mm'] if x['size_mm'])
            w.writerow(dict(zip(fields,[r['detail_id'],r['requirement_id'],r['name'],r['work_group'],
                '建议先审' if r['first_batch_recommendation'] else '后续', ' / '.join(r['template_codes']),
                r['source_anchor_id'] or '未定位',sizes,'未汇入已核实选择','未汇入已核实选择',
                r['responsible_roles'],r['next_action'],r['site_check'],'','','','','未放行'])))
    md = f'''# 8 楼当前方案与推进清单

版本 {REV}；整理日期 {DAY}。本文件整理既有评审稿，不表示方案已定稿或制作安装放行。

当前目标是先完成 8F。1F 与其他楼层资料保留，暂不扩展新设计。

**主入口：[8楼当前方案](../交付_8楼/打开这里.html)** · [21项收口CSV](../outputs/planning/8F_方案收口清单.csv) · [结构化台账](../data/8F_current_scheme.json)

## 已确认的规划骨架

- 当前人工周转车；未来考虑电动搬运车，预留但未选车型。
- 来料交接 → 装配 → 测试／老化（按实际工单适用）→ 包装 → 成品交接。
- 原料仓旁中间货梯：收料和员工到层；小客梯：访客；左上梯：成品下楼；左下和右下暂未规划使用。
- 上述为已有用户确认的规划关系；门到门通路、员工后续走段、净宽及固定面仍待现场核对。

## 当前采用哪些文件

| 用途 | 版本 | 适用范围 |
|---|---|---|
'''
    for v in versions:
        md += f"| [{v['purpose']}](../交付_8楼/{v['path']}) | {v['version']} | {v['scope']} |\n"
    md += '''
V3.1灰底黄边物流、白色人行、白框普通定置为当前配色提案。蓝待检、绿放行、红不合格、黄冻结的质量状态词、动作及范围独立保留。品牌橙不上地面。

## 建议推进顺序

1. **先看总图**：核物流、人行、定置用途及C1/C2/C3；P02只确认员工到层起点，后续走段未确认。
2. **先收口六款核心模板**：D02/WF-02、D03/WF-04、D04/PM-01、D05/PM-02、D06/WH-01、D07/FL-01（配套FL-02）。统一视觉方向、字段和更新责任。这是设计推进建议，不是代替用户选择。
3. **补齐作业/品质**：SOP、设备身份、质量状态、包装、跨层、返修、空器具与工装量具。
4. **逐项核条件与展示**：D11测试/老化、D15访客、D17电子进入、D18电池暂存、D20样件验证；D15/D18/D20尚未定位。
5. **同次踏勘收齐现场资料**：底图、走段、安装面、尺寸/高度/朝向、车辆包络、材料/固定和数量；记录复核责任。

本汇总未导入已核实的用户选择。已有V2.8本机选择请在原页导出JSON；不要清除原浏览器存储。QA测试文件不作为真实选型。

## 全部需求

| 详图 | 需求 | 模板 | 工作组 | 本轮下一步 |
|---|---|---|---|---|
'''
    for r in requirements:
        md += f"| {r['detail_id']} | {r['name']} | {' / '.join(r['template_codes'])} | {r['work_group']} | {r['next_action']} |\n"
    md += '\n## 完成8F方案还需要闭合的事项\n\n'
    for g in gates:
        md += f"- **{g['id']} {g['name']}**：{g['action']} 责任角色：{g['roles']}。\n"
    md += '''
当前21条是功能需求，不等于21个安装点或21块牌。尺寸是模板名义尺寸；现场尺寸、数量、高度与具体位置保持空值。P02/P05仍阻塞。图身“八层”/图签“三层”、物理单位和两向校准需工程确认后，才可生成真实坐标及可核量点位。

## 本地目录说明

`交付_8楼/`集中保存评审资料；`design/v2/`为设计源稿；`outputs/drawings/`为共享CAD副本；`inputs/`为封存原件；`reports/`为验证及历史证据。1F/8F散装目录的重复DXF改为项目内相对链接，项目整体保留即可读取。若单独携带V2.4资料，请使用各层原有Source ZIP；ZIP仍含完整DXF。复制当前散装目录时需同时保留项目根目录，或将链接另存为普通文件。
'''
    if supplement:
        note = (f'**新增：[V3.2点位补充与踏勘](../交付_8楼/{supplement_path})**。'
                f'含{supplement["survey_rows"]}项踏勘、{supplement["mapped_candidates"]}项图上标注'
                f'和{supplement["reference_rows"]}项PPT逐项对照。真实点位与数量待核。\n\n')
        md = md.replace('## 已确认的规划骨架', note + '## 已确认的规划骨架', 1)
    if partition:
        note = (f'**新增：[V3.4围板设计补充](../交付_8楼/{partition_path})**。'
                '访客侧、装配工位侧、仓口侧及维修侧的立面草案，附可编辑源稿和现场踏勘表。\n\n')
        md = md.replace('## 已确认的规划骨架', note + '## 已确认的规划骨架', 1)
    (ROOT/'docs/8楼方案推进清单.md').write_text(md)
    version_rows = ''.join(f'<tr><th scope="row"><a href="{esc(v["path"])}">{esc(v["purpose"])}</a></th><td>{esc(v["version"])}</td><td>{esc(v["scope"])}</td></tr>' for v in versions)
    req_sections = ''
    for group in groups:
        rows = ''
        for r in requirements:
            if r['detail_id'] not in group['details']: continue
            tag = '<span class="badge">首批建议</span>' if r['first_batch_recommendation'] else ''
            rows += f'<tr><th scope="row">{esc(r["detail_id"])}</th><td>{esc(r["name"])} {tag}<small>{esc(" / ".join(r["template_codes"]))}</small></td><td>{esc(r["next_action"])}</td><td>{esc(r["responsible_roles"])}</td></tr>'
        req_sections += f'<section><h3>{esc(group["name"])}</h3><p>{esc(group["action"])}</p><div class="scroll" tabindex="0" aria-label="{esc(group["name"])}需求表"><table><thead><tr><th>编号</th><th>功能需求 / 模板</th><th>下一步</th><th>责任角色</th></tr></thead><tbody>{rows}</tbody></table></div></section>'
    gate_html = ''.join(f'<li><h3>{esc(g["id"])} · {esc(g["name"])}</h3><p>{esc(g["action"])}</p><small>责任角色：{esc(g["roles"])}</small></li>' for g in gates)
    metadata = json.dumps({'revision': REV, 'updated_on': DAY, 'status': 'draft_navigation_and_plan', 'production_release': False, 'source_records': plan['source_records']}, ensure_ascii=False).replace('<','\\u003c')
    page = '''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>BeePump｜8楼当前方案</title><style>
*{box-sizing:border-box}html{scroll-behavior:smooth}body{margin:0;background:#fff;color:#3E3A39;font:16px/1.75 system-ui,-apple-system,"PingFang SC",sans-serif}a{color:inherit;text-underline-offset:4px}a:hover,a:focus-visible{outline:2px solid #FF6600;outline-offset:4px}main{max-width:1180px;margin:auto;padding:30px 32px 60px}header{border-bottom:2px solid #000;padding-bottom:24px}h1{font-size:38px;line-height:1.25;margin:16px 0;color:#000}h2{font-size:27px;line-height:1.4;color:#000;margin:0 0 14px}h3{font-size:20px;line-height:1.45;color:#000;margin:0 0 10px}p{margin:10px 0}small{font-size:13px;display:block}nav{display:flex;gap:16px;flex-wrap:wrap;margin-top:20px}.eyebrow{font-size:13px;font-weight:700;letter-spacing:.1em}.intro{font-size:19px;max-width:850px}.status{border-left:4px solid #FF6600;padding:10px 16px;background:#f5f5f5;margin:20px 0}.actions{display:grid;grid-template-columns:repeat(3,1fr);gap:18px;margin:30px 0}.card{border:1px solid #ccc;padding:23px;display:flex;flex-direction:column;align-items:start}.card p{flex:1}.primary{display:inline-block;background:#000;color:#fff;padding:10px 18px;border-left:4px solid #FF6600;text-decoration:none;font-weight:700;margin:12px 0}.section{border-top:1px solid #bbb;padding-top:26px;margin-top:40px}figure{margin:20px 0}figure img{display:block;width:100%;height:auto;border:1px solid #ddd}figcaption{font-size:13px;padding:10px 0}.facts{display:grid;grid-template-columns:1fr 1fr;gap:12px 26px}.facts p{border-left:2px solid #000;padding-left:14px}table{width:100%;border-collapse:collapse;font-size:14px;text-align:left}th,td{padding:12px 14px;border-bottom:1px solid #ddd;vertical-align:top}thead th{background:#000;color:white}tbody th{color:#000;min-width:65px}td:nth-child(2){min-width:180px}td:nth-child(3){min-width:280px}.scroll{overflow-x:auto}.badge{font-size:12px;display:inline-block;padding:0 6px;background:#f3f3f3;border:1px solid #aaa;white-space:nowrap}section section{margin:28px 0}ol{padding-left:28px}ol li{padding:10px 0 20px;border-bottom:1px solid #ddd}footer{border-top:2px solid #000;margin-top:35px;padding-top:18px;font-size:13px}.skip{position:absolute;top:-100px}.skip:focus{top:0;background:#fff}.history{font-size:14px}details{margin:20px 0}summary{cursor:pointer;font-weight:700}body [id]{scroll-margin-top:20px}@media(max-width:760px){main{padding:22px 18px 40px}h1{font-size:30px}.actions,.facts{grid-template-columns:1fr}.actions{gap:12px}.card{padding:18px}h2{font-size:24px}}@media(prefers-reduced-motion:reduce){html{scroll-behavior:auto}}@media print{main{max-width:none;padding:0}.actions{grid-template-columns:1fr 1fr 1fr}nav,.skip{display:none}h2,h3{break-after:avoid}tr,li,.card{break-inside:avoid}.scroll{overflow:visible}td:nth-child(3){min-width:0}a{text-decoration:none}}
</style><script type="application/json" id="artifact-metadata">__META__</script></head><body><a class="skip" href="#main">跳到8楼方案</a><main id="main"><header><p class="eyebrow">BEEPUMP · 8F · 当前方案 / 2026-10-26</p><h1>先完成 8 楼</h1><p class="intro">把总图、牌面和现场收口资料放在一个入口。先确认物流、人行与区域，再完成核心模板和真实安装条件。</p><div class="status"><strong>当前状态：方案评审与收口</strong><br>已有主流程与电梯分工；真实底图单位、员工后续走段、现场安装面及数量待核。21条为功能需求，制作安装尚未放行。</div><nav aria-label="方案章节"><a href="#overview">方案骨架</a><a href="#drawing">当前总图</a><a href="#requirements">21项需求</a><a href="#closure">完成关口</a><a href="#versions">版本索引</a></nav></header>
<div class="actions"><section class="card"><p class="eyebrow">01 · 看总图</p><h2>物流、人行与定置</h2><p>V3.1直接在来源底图上显示地面配色提案；支持切换查看图层。</p><a class="primary" href="地面物流规划_V3.1/打开地面配色图.html">打开当前地面方案</a><a href="地面物流规划_V3.1/8F_地面物流与地标规划_评审稿.pdf">3页评审PDF</a></section><section class="card"><p class="eyebrow">02 · 定牌面</p><h2>逐项比较样式</h2><p>V2.8保留21项A/B/C样式及位置关系选项。先看六款核心模板，再审其他需求。</p><a class="primary" href="多方案选择_V2.8/START_HERE.html">打开牌面选择</a><a href="多方案选择_V2.8/output/pdf/BeePump_8F_Options_V2.8.pdf">23页比较PDF</a></section><section class="card"><p class="eyebrow">03 · 收齐现场资料</p><h2>量尺、核图与核量</h2><p>按同一张收口表落实责任、现场条件与真实值，保留现有材料和验收表。</p><a class="primary" href="../outputs/planning/8F_方案收口清单.csv" download>下载21项收口清单</a><a href="output/pdf/BeePump_8F_SettingOut_Acceptance_V2.4.pdf">8页现场表PDF</a></section></div>
<section class="section" id="overview"><h2>已确认的规划骨架</h2><div class="facts"><p><strong>物料主流程</strong><br>来料交接 → 装配 → 测试／老化（按工单适用）→ 包装 → 成品交接。</p><p><strong>搬运方式</strong><br>当前人工周转车；未来考虑电动搬运车，保留扩展意向，车型和包络未定。</p><p><strong>收料与员工到层</strong><br>原料仓旁中间货梯；员工后续更衣/进入走段仍待核。</p><p><strong>访客与成品</strong><br>小客梯供访客到层；左上梯用于成品下楼；左下/右下暂未规划使用。</p></div><small>复用既有用户确认，仅作为规划关系。完整走段、现场可用性及适用专项需分别核对。</small></section>
<section class="section" id="drawing"><h2>当前总图 · V3.1</h2><p>灰底黄边为物流、白色带配人行为人行、白框为普通定置；蓝/绿/红/黄质量状态独立保留。品牌橙不上地面。</p><figure><a href="地面物流规划_V3.1/打开地面配色图.html"><img src="地面物流规划_V3.1/预览/01_物流与人行彩色总图.png" alt="8楼V3.1地面物流、人行与定置配色提案总图，点击打开图层版" width="1680" height="1188"></a><figcaption>原图叠加评审提案。显示像素不等于毫米；C1/C2/C3、员工后续走段、E01电动预留及接驳灰虚线需另核，不能据此直接放样刷漆。</figcaption></figure><p><a href="地面物流规划_V3.1/预览/02_作业区实际配色放大图.png">作业区放大</a> · <a href="地面物流规划_V3.1/预览/03_人行通道与物流分界放大图.png">人行分界放大</a> · <a href="地面物流规划_V2.9.1/人工与未来电动_双工况核对表.csv">人工/未来电动测量表</a></p></section>
<section class="section" id="requirements"><h2>21项需求，按工作内容收口</h2><p><strong>建议先审：</strong>WF-02区域吊牌、WF-04柱牌、WH-01库位标签、PM-01生产运行、PM-02日会行动、FL-01在制限量（配套FL-02）。</p><p>本汇总未导入已核实的用户选择；已有V2.8本机选择请在原页导出JSON。此页不读取或重置浏览器选择，QA测试导出不作为真实选型。</p>__REQ__</section>
<section class="section" id="closure"><h2>完成8楼方案，还需闭合5项</h2><p>样式与内容可以继续评审；真实坐标与点位核量依赖底图、现场条件及相应复核。</p><ol>__GATES__</ol><p><a href="../docs/8楼方案推进清单.md">完整推进说明</a> · <a href="../data/8F_current_scheme.json">结构化方案台账</a> · <a href="specs/quotation_scope.csv">报价边界</a> · <a href="specs/material_families.json">材料家族</a></p></section>
<section class="section" id="versions"><h2>按用途查版本</h2><p>当前方案由不同专业内容的最新适用稿组成。旧版入口、人流和物流箭头需对照后续修订。</p><div class="scroll" tabindex="0" aria-label="各版本适用范围"><table><thead><tr><th>用途</th><th>版本</th><th>适用范围</th></tr></thead><tbody>__VERSIONS__</tbody></table></div><details><summary>历史资料、编辑源稿与独立源包</summary><p class="history"><a href="图纸标注_V2.5/START_HERE.html">V2.5来源标注</a> · <a href="逐项样式尺寸_参观预览_V2.6/可编辑模板/">V2.6可编辑模板</a> · <a href="客梯入口修订_V2.7/START_HERE.html">V2.7客梯画面</a> · <a href="地面物流规划_V2.9.1/打开地面物流方案.html">V2.9.1地面规则与测量</a> · <a href="design/">V2.4编辑源稿</a></p><p class="history"><a href="BeePump_8F_Implementation_V2.4_Source.zip">V2.4独立源包</a> · <a href="BeePump_8F_地面配色_V3.1_评审包.zip">V3.1配色评审包</a> · <a href="../交付_1楼/打开这里.html">1楼保留资料</a> · <a href="../FLOOR_DELIVERIES.html">两楼历史总目录</a></p></details></section>
<footer>8F-CONSOLIDATED-2026-10-26-DRAFT · 方案整理，无新增制作安装批准。<br>底图图身八层/图签三层、物理单位、现场坐标/尺寸/数量保持待核；P02/P05阻塞保留。<br>散装目录使用项目内共享DXF；单独携带V2.4资料请用独立Source ZIP。<a href="../reports/cleanup_2026-10-26/整理报告.md">查看本次清理记录</a></footer></main></body></html>'''
    for old, new in [('__META__',metadata),('__REQ__',req_sections),('__GATES__',gate_html),('__VERSIONS__',version_rows)]:
        page = page.replace(old,new)
    if effect_manifest_path.is_file():
        gallery = effect_gallery_path.removeprefix('交付_8楼/')
        effect_manifest = read(str(effect_manifest_path.relative_to(ROOT)))
        thumbnail_rows = effect_manifest['assets']
        if is_point_gallery:
            priority = ['D14','D04','D02','D11','U01','D06']
            thumbnail_rows = sorted((r for r in thumbnail_rows if r['key'] in priority), key=lambda r:priority.index(r['key']))
        thumbnails = ''.join(
            f'<figure><a href="{esc(gallery)}#{esc(row["id"])}"><img src="../{esc(row["path"])}" '
            f'alt="{esc(row["title"])}概念效果，空间与设备为示意" '
            f'width="{row["width_px"]}" height="{row["height_px"]}"></a>'
            f'<figcaption>{esc(row["title"])}</figcaption></figure>'
            for row in thumbnail_rows)
        section = '<section class="section" id="effect-preview"><h2>8楼概念效果预览</h2>'
        if is_point_gallery:
            section += f'<p>已保存{len(effect_manifest["assets"])}张逐项功能概念图，优先查看维修台、流水线头、装配区、测试区、老化充电管理、物料超市。附小红书案例采用记录及六款可编辑模板前后对照。</p>'
        else:
            section += '<p>装配作业区、地面物流与线边定置、访客到层导览。</p>'
        section += '<p>空间和设备为生成示意，不是本厂实景或CAD还原，也不代表A/B/C最终选型。真实位置、尺寸、数量与制作安装未核。</p>'
        section += '<div class="actions">'+thumbnails+'</div>'
        label = '打开逐项效果图与功能优化' if is_point_gallery else '打开三张完整效果图'
        section += f'<a class="primary" href="{esc(gallery)}">{label}</a></section>'
        page = page.replace('</header>', '</header>'+section, 1)
        page = page.replace('<a href="#overview">', '<a href="#effect-preview">效果预览</a><a href="#overview">', 1)
    if supplement:
        section = ('<section class="section" id="reference-supplement">'
                   '<h2>V3.2 点位补充与现场踏勘</h2>'
                   f'<p>对照新参考PPT，补充{supplement["survey_rows"]}项8F踏勘需求。'
                   f'在现有底图标注{supplement["mapped_candidates"]}项核查对象，'
                   f'另有{supplement["unplaced_candidates"]}项待定位。'
                   '包含来源对照、责任与计量口径，现场尺寸和安装量待核。</p>'
                   f'<a class="primary" href="{esc(supplement_path)}">打开补充点位图与清单</a></section>')
        page = page.replace('</header>', '</header>'+section, 1)
        page = page.replace('<a href="#overview">', '<a href="#reference-supplement">点位补充</a><a href="#overview">', 1)
    if partition:
        section = ('<section class="section" id="partition-supplement">'
                   '<h2>V3.4 围板设计补充</h2>'
                   '<p>访客侧、装配工位侧、原料仓和维修侧的围板立面示意。'
                   '含固定文字、可换资料、留白和板面踏勘表，现场板体与尺寸待核。</p>'
                   f'<a class="primary" href="{esc(partition_path)}">看围板设计与踏勘表</a></section>')
        page = page.replace('</header>', '</header>'+section, 1)
        page = page.replace('<a href="#overview">', '<a href="#partition-supplement">围板设计</a><a href="#overview">', 1)
    (ROOT/'交付_8楼/打开这里.html').write_text(page)
    print('Built 8F current scheme: 21 requirements, 6 core-template recommendations; no choices or actual points created.')

if __name__ == '__main__':
    main()

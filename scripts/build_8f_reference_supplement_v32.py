#!/usr/bin/env python3
"""Build the local 8F reference supplement from the draft survey register."""
import base64
import csv
import hashlib
import html
import json
from pathlib import Path

from build_8f_onplan_v30 import rect, txt

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "design/v2/8f_reference_supplement_v3.2"
OUT = ROOT / "交付_8楼/点位补充_V3.2"
PDF = "output/pdf/8F_点位补充与踏勘图_V3.2.pdf"
SURVEY = "8F_踏勘清单.csv"
CROSSWALK = "8F_PPT逐项对照.csv"
SOURCE_LINK = "../../design/v2/8f_reference_supplement_v3.2/"
ESC = html.escape
FONT = "PingFang SC, Noto Sans CJK SC, Microsoft YaHei, sans-serif"
DARK = "#3E3A39"

RULES = [
    ("通道与定置", "V3.1灰底黄边物流、白色人行、白框普通定置。C1/C2/C3先按实际净宽、门扇、视距、满载转弯及分流核对。PPT第4–5页的绿蓝满铺、宽度、线宽及固定斑马线仅作参考。"),
    ("品质与维修", "蓝待检、绿放行、红普通不合格、黄冻结。维修看板记录待修、在修、已修待复判及报废待处置，品质状态随授权结论更新。"),
    ("三级标识与两级看板", "PPT第6–8页的楼层/区域、工位/定置层级落实到既有模板。先核线别与工位号，再核综合管理看板和线头运行板。尺幅、安装高与实物数量随实际读面确认。"),
    ("线数与选址差异", "PPT第14–15页展示六条装配线，含左侧两条线。V3.1底图对应处无这两条线，当前只在中央可识别线体标一组代表性核查位置。休息区和退货隔离面由现场另核。"),
    ("专项复核", "PPT第9、15、17页等涉及消防、电气、UV、镭雕、ESD等。实际设施、适用条件、图形与措施以本厂经复核的专项文件为依据。"),
    ("跨楼层参考", "PPT第10–13页提供注塑与装配车间做法。日后复核2F注塑与4F手打气筒装配时，可比对机台、模具、线头和工装字段，先核楼层及业务再考虑布点。"),
]

MEASURE = [
    ("现场取证", "带底图核真实区域、门或资产位号，记录照片、参照物、朝向、识读面、净宽、门扇及现有标识。重复线体以当前在用线/工位清点。"),
    ("按载体核量", "核到实物后按载体复制清单行，保留K号及现场资产位号。同一底板共用多项时登记一次，并注明关联K号。双面牌按一件实物、两面印刷计。标签备品、原有牌、拟制作牌、线长和涂装面积分别核。未测值留空。"),
    ("形成真实点位", "工程确认有效图框、“八层/三层”图签差异、图纸单位与两方向校准，且位置/固定面有现场证据后，按项目契约录入真实点位，并完成内容、位置、安装及适用专项复核。"),
]


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def records(fields, rows):
    return [dict(zip(fields, row, strict=True)) for row in rows]


def write_csv(path, columns, rows):
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(columns)
        writer.writerows(rows)


def open_sheet(title, subtitle, page, meta):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="1680" height="1188" '
            f'viewBox="0 0 1680 1188" role="img" aria-label="{ESC(title)}">'
            f'<metadata>{ESC(json.dumps(meta, ensure_ascii=False))}</metadata>'
            f'<g font-family="{FONT}">'
            + rect(0, 0, 1680, 1188, "#FFFFFF")
            + rect(0, 0, 1680, 152, "#000000")
            + txt(46, 54, "BEEPUMP  /  8F  /  V3.2 踏勘评审稿", 23, "#FFFFFF", True)
            + txt(46, 115, title, 45, "#FFFFFF", True)
            + txt(1634, 109, f"{page:02d} / 04", 27, "#FFFFFF", True, "end")
            + txt(46, 202, subtitle, 26, DARK))


def close_sheet():
    return (rect(46, 1102, 1588, 1.5, "#B6B2B0")
            + txt(46, 1136, "底图沿用V3.1候选截图 · 图身“八层”/图签“三层”与物理单位待核 · 图中编号用于踏勘", 20, DARK)
            + txt(46, 1164, "参考《车间目视化设计方案》PPT第14–20页 · 适用性、实地量尺、真点位及制作安装待确认", 19, DARK)
            + "</g></svg>\n")


def image_layer(image_url, base, crop, x, y, width, height):
    return (f'<svg x="{x}" y="{y}" width="{width}" height="{height}" '
            f'viewBox="{" ".join(map(str, crop))}" overflow="hidden" preserveAspectRatio="xMidYMid meet">'
            f'<image width="{base["width_px"]}" height="{base["height_px"]}" href="{image_url}"/>')


def marker(item):
    ax, ay = item["display_anchor_px"]
    x, y = item["display_label_px"]
    short = item["stage"] == "首轮"
    outline = "#000000" if short else DARK
    fill = "#000000" if short else "#FFFFFF"
    edge = (f'<path d="M {ax} {ay} L {x} {y}" fill="none" '
            f'stroke-linecap="round" stroke-linejoin="round"')
    return (f'<g id="{item["id"]}"><title>{ESC(item["name"])}</title>'
            + edge + ' stroke="#FFFFFF" stroke-width="4.2"/>'
            + edge + f' stroke="{outline}" stroke-width="1.2"/>'
            + f'<circle cx="{ax}" cy="{ay}" r="4.4" fill="#FFFFFF" stroke="{outline}" stroke-width="2"/>'
            + rect(x - 20, y - 11.5, 40, 23, "#FFFFFF", "#FFFFFF", 3, 'rx="4"')
            + rect(x - 20, y - 11.5, 40, 23, fill, outline, 1.3, 'rx="4"')
            + txt(x, y + 5, item["id"], 14, "#FFFFFF" if short else "#000000", True, "middle")
            + "</g>")


def overview(data, image_url, mapped_count, unplaced):
    title = "8F｜点位补充与踏勘总览"
    meta = {"revision": data["revision"], "status": "draft", "sheet": "overview",
            "base_sha256": data["base"]["sha256"], "production_release": False}
    s = open_sheet(title, "从现有工序和到层分工出发，用K编号逐项核对实际读面、固定面和现场数量。", 1, meta)
    s += rect(46, 236, 1060, 712, "#FFFFFF", "#BAB8B7", 1.4)
    s += image_layer(image_url, data["base"], (-15, 155, 1920, 1246), 57, 246, 1038, 686)
    for label, x, w, label_x in [("西侧", 6, 640, 267), ("中央", 646, 500, 903), ("东侧", 1146, 675, 1504)]:
        s += rect(x, 180, w, 607, "none", DARK, 3, 'stroke-dasharray="9 7"')
        s += rect(label_x - 80, 812, 160, 55, "#000000", extra='rx="4"')
        s += txt(label_x, 850, label, 40, "#FFFFFF", True, "middle")
    s += "</svg>"
    s += txt(46, 995, "按西侧、中央、东侧三张放大图踏勘。虚线框用于阅读分区。", 23, DARK)
    s += txt(46, 1036, "主流程  来料交接 → 装配 → 适用测试／老化 → 包装 → 成品交接", 23, DARK)
    s += txt(1152, 269, "踏勘优先顺序", 30, "#000000", True)
    lines = [
        ("到层与交叉", ["中间货梯收料＋员工，小客梯仅访客。", "左上梯成品下楼，C1/C2/C3逐处核。"]),
        ("先给一条在用线试样", ["线端识别、首件、工位、检验和线边料位。", "按现场线号、读面和在用载体逐线核。"]),
        ("按批次核工序交接", ["老化、普通不良/冻结、维修复判、成品待运。", "蓝待检、绿放行、红普通不合格、黄冻结。"]),
    ]
    for i, (heading, body) in enumerate(lines):
        y = 326 + 130 * i
        s += txt(1152, y, heading, 25, "#000000", True)
        for j, line in enumerate(body):
            s += txt(1152, y + 38 + 29 * j, line, 21, DARK)
    s += rect(1152, 709, 482, 339, "#F4F3F2")
    s += txt(1174, 750, f"{mapped_count}项图上核查  /  {len(unplaced)}项待定位", 25, "#000000", True)
    for i, item in enumerate(unplaced):
        s += txt(1174, 798 + i * 42, f'{item["id"]}   {item["name"]}', 22, DARK)
    return s + close_sheet()


def panel_svg(data, panel, rows, image_url, page):
    title = panel["title"]
    meta = {"revision": data["revision"], "status": "draft", "sheet": title,
            "base_sha256": data["base"]["sha256"], "display_crop_px": panel["crop"],
            "candidate_ids": [r["id"] for r in rows], "production_release": False}
    s = open_sheet(title, panel["subtitle"], page, meta)
    s += rect(46, 236, 1000, 806, "#FFFFFF", "#BAB8B7", 1.4)
    s += image_layer(image_url, data["base"], panel["crop"], 52, 244, 988, 790)
    s += "".join(marker(row) for row in rows) + "</svg>"
    s += txt(1080, 270, "现场核查对象", 31, "#000000", True)
    s += txt(1080, 309, "黑底为首轮，其余见右侧阶段", 21, DARK)
    for i, row in enumerate(rows):
        y = 344 + i * 70
        s += rect(1080, y, 554, 1, "#D8D5D3")
        s += txt(1080, y + 28, row["id"], 22, "#000000", True)
        s += txt(1143, y + 28, row["name"], 24, "#000000", True)
        s += txt(1634, y + 28, row["stage"], 20, DARK, anchor="end")
        s += txt(1143, y + 54, row["short_check"], 20, DARK)
    s += txt(46, 1078, "引线端指向踏勘对象或候选区域。色带、路线与定置配色对照V3.1。", 20, DARK)
    return s + close_sheet()


def html_page(candidates, crosswalk, panels, files, data):
    map_html = []
    for (label, title), filename in zip(panels, files, strict=True):
        src = SOURCE_LINK + filename
        map_html.append(
            f'<section id="{label}"><h2>{ESC(title)}</h2><figure>'
            f'<a href="{src}"><img src="{src}" alt="{ESC(title)}" width="1680" height="1188"></a>'
            f'<figcaption><a href="{src}" download>下载可编辑SVG</a></figcaption></figure></section>')
    sections = []
    for group in ("西侧", "中央", "东侧", None):
        label = f"{group}踏勘项" if group else "待定位项"
        group_rows = []
        for row in [r for r in candidates if r["panel"] == group]:
            row_id = row["id"]
            references = ESC(row["references"])
            codes = ESC(row["template_codes"]) or "按专项文件选用"
            details = ESC(row["existing_details"]) or "新增条件核查"
            group_rows.append(f'<details id="{row_id}"><summary><b>{row_id}　{ESC(row["name"])}</b> '
                              f'<span>{row["stage"]}</span></summary><dl>'
                              f'<dt>位置依据</dt><dd>{ESC(row["placement_basis"])}</dd>'
                              f'<dt>牌面及使用动作</dt><dd>{ESC(row["content_and_action"])}</dd>'
                              f'<dt>现场核对</dt><dd>{ESC(row["survey_gate"])}</dd>'
                              f'<dt>责任与计量口径</dt><dd>{ESC(row["roles"])} · {ESC(row["measurement_grain"])}</dd>'
                              f'<dt>方案索引</dt><dd>PPT {references} · 现有方案 {details} · 模板 {codes}</dd>'
                              '</dl></details>')
        sections.append(f'<h3>{label}</h3>{"".join(group_rows)}')
    rules = "".join(f'<dt>{name}</dt><dd>{description}</dd>' for name, description in RULES)
    measure = "".join(f'<dt>{name}</dt><dd>{description}</dd>' for name, description in MEASURE)
    compare_table = []
    for row in crosswalk:
        name, slide = data["reference_groups"][row["ref_id"][0]]
        links = ' / '.join(f'<a href="#{key}">{key}</a>' for key in row["candidates"].split(" / "))
        compare_table.append(f'<tr><th scope="row">{row["ref_id"]}<small>第{slide}页 · {name}</small></th>'
                             f'<td>{ESC(row["ref_scope"])}</td><td>{links}</td>'
                             f'<td><b>{ESC(row["decision"])}</b><br>{ESC(row["adaptation"])}</td></tr>')
    return f'''<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>8F 点位补充与踏勘 · V3.2</title><style>
:root{{--brand:#ff6600;--ink:#000;--body:#3e3a39;--border:#d8d5d3}}*{{box-sizing:border-box}}
body{{margin:0;font:16px/1.65 {FONT};color:var(--body);background:#fff}}
main{{max-width:1180px;padding:32px 24px 60px;margin:auto}}
header{{background:#000;color:#fff;padding:28px clamp(18px,4vw,52px) 34px}}
header>div{{max-width:1084px;margin:auto}}header a{{color:#fff}}
h1,h2,h3{{line-height:1.22;color:#000}}h1{{color:#fff;margin:12px 0 20px;font-size:clamp(32px,5vw,58px)}}
h2{{font-size:clamp(25px,3vw,34px);margin:0 0 16px}}h3{{margin:28px 0 10px}}
a{{color:inherit;text-underline-offset:4px}}a:focus-visible,summary:focus-visible{{outline:3px solid var(--brand);outline-offset:3px}}
p{{margin:0 0 12px}}nav{{display:flex;flex-wrap:wrap;gap:8px 20px;margin-top:18px}}
nav a{{padding:5px 0}}.primary{{display:inline-block;background:var(--brand);color:#000;text-decoration:none;padding:9px 14px;font-weight:700}}
section{{padding:30px 0;border-bottom:1px solid var(--border)}}figure{{margin:0}}
img{{max-width:100%;height:auto;display:block;border:1px solid var(--border)}}figcaption{{margin:8px 0 0}}
details{{padding:11px 0;border-bottom:1px solid var(--border);scroll-margin-top:12px}}details:target{{background:#fff3e9}}
summary{{cursor:pointer;color:#000}}summary span{{font-size:.85em;color:var(--body);margin-left:6px;white-space:nowrap}}
dl{{display:grid;grid-template-columns:minmax(7rem,auto) 1fr;gap:6px 16px;margin:12px 0}}
dt{{font-weight:700;color:#000}}dd{{margin:0}}
table{{border-collapse:collapse;width:100%;min-width:660px}}td,th{{vertical-align:top;text-align:left;padding:10px;border-bottom:1px solid var(--border)}}
thead{{background:#f4f3f2}}small{{display:block;font-weight:400}}
.table-scroll{{overflow:auto}}.file-links{{display:flex;flex-wrap:wrap;align-items:center;gap:10px 18px}}
footer{{font-size:14px;padding-top:24px}}
@media(max-width:620px){{main{{padding:10px 14px 36px}}dl{{display:block}}dd{{margin:0 0 10px}}}}
</style></head><body><header><div>
<p><a href="../打开这里.html">返回8楼当前方案</a>　/　V3.2 · 踏勘评审稿</p>
<h1>8F 点位补充与踏勘</h1>
<p>把参考PPT的6S、品质、仓库、维修及电子区做法落到现有8F方案。图中K编号指向核查对象或候选区域。</p>
<nav aria-label="补充方案"><a class="primary" href="{PDF}">打开4页踏勘图 PDF</a>
<a href="{SURVEY}" download>下载踏勘清单 CSV</a><a href="#surveys">逐项核查</a><a href="#crosswalk">PPT逐项对照</a><a href="#measure">现场核量</a></nav>
</div></header><main>
<section id="rules"><h2>与现有方案的衔接</h2><dl>{rules}</dl>
<p><a href="../地面物流规划_V3.1/打开地面配色图.html">查看现有V3.1地面配色与路线关系</a></p></section>
{"".join(map_html)}
<section id="surveys"><h2>逐项核查</h2><p>展开编号查看候选位置、牌面内容、现场事项及责任角色。现行D编号用于对照21项原需求。</p>
{"".join(sections)}</section>
<section id="crosswalk"><h2>PPT逐项对照</h2><p>按PPT播放顺序计页。参考稿的A–F编号和BeePump现行D编号各有自己的来源。</p>
<p><a href="{CROSSWALK}" download>下载A–F逐项对照 CSV</a></p><div class="table-scroll" tabindex="0" aria-label="PPT参考项与踏勘编号对照">
<table><thead><tr><th>参考编号</th><th>PPT内容</th><th>对应踏勘项</th><th>本轮处理</th></tr></thead>
<tbody>{"".join(compare_table)}</tbody></table></div></section>
<section id="measure"><h2>现场核量与放样</h2><dl>{measure}</dl>
<p><a href="{SURVEY}" download>下载可填写踏勘清单</a> · <a href="{SOURCE_LINK}踏勘项与参考映射.json">查看结构化底稿</a></p></section>
<footer>参考来源《{ESC(data["reference"]["name"])}》，气泵车间图第14页及明细第15–19页。<br>
{data["date"]} · 底图、真实坐标、安装尺寸和数量待核，制作安装未放行。</footer></main>
<script>function reveal(){{const target=document.getElementById(location.hash.slice(1));if(target?.tagName==='DETAILS')target.open=true}}addEventListener('hashchange',reveal);reveal();</script>
</body></html>'''


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    data = json.loads((SRC / "踏勘项与参考映射.json").read_text())
    base = data["base"]
    image_path = ROOT / base["path"]
    ground_path = image_path.parent / "地面配色与来源.json"
    ground = json.loads(ground_path.read_text())
    if digest(image_path) != base["sha256"] or ground["source_png_sha256"] != base["sha256"]:
        raise ValueError("V3.1底图来源与补充稿登记不一致")
    if ground["source_drawing_sha256"] != base["source_drawing_sha256"]:
        raise ValueError("DWG来源与V3.1登记不一致")
    image_url = "data:image/png;base64," + base64.b64encode(image_path.read_bytes()).decode()

    candidates = records(data["candidate_fields"], data["candidates"])
    crosswalk = records(data["crosswalk_fields"], data["crosswalk"])
    ids = {r["id"] for r in candidates}
    details = {r["detail_id"] for r in json.loads((ROOT / "data/8F_current_scheme.json").read_text())["requirements"]}
    templates = {r["code"] for r in json.loads((ROOT / "data/templates.json").read_text())}
    linked_details = set()
    if len(ids) != len(candidates):
        raise ValueError("K编号重复")
    expected_refs = [f"{letter}{n}" for letter, count in zip("ABCDEF", (10, 7, 10, 7, 4, 4), strict=True)
                     for n in range(1, count + 1)]
    if [r["ref_id"] for r in crosswalk] != expected_refs:
        raise ValueError("PPT A–F编号不完整")
    for row in crosswalk:
        if not set(row["candidates"].split(" / ")) <= ids:
            raise ValueError(f'PPT {row["ref_id"]}引用了未知K编号')
    for row in candidates:
        template_refs = set(filter(None, row["template_codes"].split(" / ")))
        detail_refs = set(filter(None, row["existing_details"].split(" / ")))
        linked_details.update(detail_refs)
        if not (template_refs <= templates and detail_refs <= details):
            raise ValueError(f'{row["id"]}引用了未知的现有详图或模板')
        if row["panel"] is None:
            if row["display_anchor_px"] is not None or row["display_label_px"] is not None:
                raise ValueError(f'{row["id"]}待定位项含像素标记')
        else:
            x, y, w, h = data["map_panels"][row["panel"]]["crop"]
            ax, ay = row["display_anchor_px"]
            lx, ly = row["display_label_px"]
            if not (x <= ax <= x+w and y <= ay <= y+h and x+21 <= lx <= x+w-21 and y+12 <= ly <= y+h-12):
                raise ValueError(f'{row["id"]}超出图框')
    if linked_details != details:
        raise ValueError(f'未衔接现有方案需求 {details - linked_details}')

    filenames = ["01_踏勘总览.svg", "02_西侧品质与维修.svg", "03_中央装配与成品.svg", "04_东侧到层与仓储.svg"]
    unplaced = [row for row in candidates if not row["panel"]]
    (SRC / filenames[0]).write_text(overview(data, image_url, len(candidates) - len(unplaced), unplaced))
    panels = [("overview", "踏勘总览")]
    for i, ((zone, panel), filename) in enumerate(zip(data["map_panels"].items(), filenames[1:], strict=True), 2):
        rows = [r for r in candidates if r["panel"] == zone]
        (SRC / filename).write_text(panel_svg(data, panel, rows, image_url, i))
        panels.append((f"map-{i}", panel["title"]))

    columns = ["踏勘编号", "楼层", "图区", "核查对象", "阶段", "参考PPT编号或页码", "既有详图", "可复用模板代码",
               "候选位置依据", "牌面及使用动作", "现场核查", "责任角色", "计量依据"]
    fieldwork = ["处置（沿用/移位/新增/共板/暂缓）", "实际房间或资产位号", "读面与固定面", "朝向", "尺寸mm",
                 "安装高度mm", "最窄净宽mm", "实物件数", "印刷面数", "备品件数", "线长m", "涂装面积m2",
                 "照片或文件编号", "现场结论及复核人", "核准后真实点位ID"]
    keys = ["name", "stage", "references", "existing_details", "template_codes", "placement_basis",
            "content_and_action", "survey_gate", "roles", "measurement_grain"]
    write_csv(OUT / SURVEY, columns + fieldwork,
              [[r["id"], data["floor_id"], r["panel"] or "待定位"]
               + [r[key] for key in keys] + [""] * len(fieldwork) for r in candidates])
    write_csv(OUT / CROSSWALK, ["PPT播放页", "模块", "PPT编号", "参考事项", "8F踏勘编号", "适配结论", "实施口径"],
              [[data["reference_groups"][r["ref_id"][0]][1], data["reference_groups"][r["ref_id"][0]][0],
                r["ref_id"], r["ref_scope"], r["candidates"], r["decision"], r["adaptation"]] for r in crosswalk])
    (OUT / "打开这里.html").write_text(html_page(candidates, crosswalk, panels, filenames, data))

    manifest = {
        "revision": data["revision"], "status": data["status"], "updated_on": data["date"], "floor_id": data["floor_id"],
        "production_release": False, "reference": data["reference"], "base": base,
        "governing_scheme": {"ground_path": str(ground_path.relative_to(ROOT)), "ground_sha256": digest(ground_path)},
        "scope": "候选对象、相对位置及现场踏勘流程。实物数量和世界坐标待核。",
        "survey_rows": len(candidates), "mapped_candidates": len(candidates) - len(unplaced),
        "unplaced_candidates": len(unplaced), "reference_rows": len(crosswalk),
        "world_points": [], "approved_quantities": None, "actual_quantities": None,
        "assets": [{"path": str((SRC / name).relative_to(ROOT)), "sha256": digest(SRC / name), "type": "draft_svg"}
                   for name in filenames],
        "delivery": [{"path": str((OUT / name).relative_to(ROOT)), "sha256": digest(OUT / name)}
                     for name in (SURVEY, CROSSWALK, "打开这里.html")] + [
                         {"path": str((OUT / PDF).relative_to(ROOT)), "type": "draft_pdf"}],
    }
    (SRC / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")
    print(f'Built {manifest["survey_rows"]} survey items, {manifest["mapped_candidates"]} on map, '
          f'{manifest["reference_rows"]} reference rows and {len(filenames)} draft SVGs.')


if __name__ == "__main__":
    main()

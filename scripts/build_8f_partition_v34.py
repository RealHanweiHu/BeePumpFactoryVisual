#!/usr/bin/env python3
"""Produce the 8F partition-face concept artwork and local review index."""
import json

from build_8f_onplan_v30 import rect, txt
from build_8f_reference_supplement_v32 import ROOT, ESC, FONT, digest, write_csv

SRC = ROOT / "design/v2/8f_partition_v3.4"
OUT = ROOT / "交付_8楼/围板设计_V3.4"
DATA = SRC / "围板设计与踏勘.json"
PDF = "output/pdf/8F_围板设计_V3.4.pdf"
SURVEY = "8F_围板踏勘补充.csv"
BASE = "../点位补充_V3.2/打开这里.html"
W, H = 1200, 460
BLACK, WHITE, ORANGE, GRAY = "#000000", "#FFFFFF", "#FF6600", "#3E3A39"


def rule(x, y, w, fill="#CCC9C7"):
    return rect(x, y, w, 1.5, fill)


def headers(title, tag):
    return (rect(0, 0, W, H, WHITE)
            + rect(0, 0, W, 106, BLACK)
            + txt(42, 70, title, 46, WHITE, True)
            + txt(1158, 65, tag, 25, ORANGE, True, "end"))


def slot(x, y, w, h, name, caption):
    return (rect(x, y, w, h, "#F5F4F3", GRAY, 1.8, 'stroke-dasharray="8 6"')
            + txt(x+w/2, y+h/2-2, name, 33, BLACK, True, "middle")
            + txt(x+w/2, y+h/2+42, caption, 22, GRAY, False, "middle"))


def visitor():
    s = rect(0, 0, W, H, WHITE) + rect(0, 0, W, 251, BLACK)
    s += txt(45, 59, "BeePump", 33, WHITE, True)
    s += txt(1155, 70, "8F", 42, ORANGE, True, "end")
    s += txt(45, 174, "锂电充气泵装配", 86, WHITE, True)
    s += txt(47, 307, "本层工序", 32, BLACK, True) + rule(45, 329, 1110)
    for i, name in enumerate(["来料交接", "装配", "测试／老化", "包装", "成品交接"]):
        x = 45 + i * 225
        s += txt(x, 389, name, 29, BLACK, True)
        if i < 4:
            s += txt(x+185, 389, "→", 25, GRAY, False, "middle")
    s += txt(495, 428, "按工单适用", 20, GRAY)
    return s


def assembly():
    s = headers("装配工位", "8F")
    s += txt(42, 166, "线别／工位", 31, BLACK, True) + rule(42, 189, 575)
    s += txt(42, 241, "开工前", 31, BLACK, True)
    s += txt(42, 278, "核对工单、物料与现行作业文件。", 27, GRAY)
    s += txt(42, 352, "发现异常", 31, BLACK, True)
    s += txt(42, 389, "按工位已发布的异常流程报告。", 27, GRAY)
    s += '<g id="replaceable-doc">' + slot(670, 133, 488, 286, "作业文件", "现行 SOP 可换页示意") + "</g>"
    return s


def receiving():
    s = headers("原料仓 · 收货交接", "8F")
    for i, (label, note) in enumerate([
        ("核对来料", "复核物料、批次及数量单位。"),
        ("记录交接", "关联单据与批次状态。"),
        ("确认接收", "按批次状态交接，由接收角色确认。"),
    ]):
        y = 170 + 99 * i
        s += txt(42, y, label, 31, BLACK, True) + txt(42, y+35, note, 25, GRAY)
        if i < 2:
            s += rule(42, y+53, 575)
    s += '<g id="replaceable-doc">' + slot(670, 133, 488, 286, "交接资料", "批准的收货要求可换页示意") + "</g>"
    return s


def repair():
    s = headers("维修交接", "8F")
    s += txt(42, 168, "已修件交品质复判", 36, BLACK, True)
    for i, name in enumerate(["待修", "在修", "已修待复判", "报废待处置"]):
        x = 42 + i * 285
        s += rect(x, 212, 261, 148, "#F5F4F3", GRAY, 1.8)
        s += txt(x+15, 250, name, 27, BLACK, True)
        s += rule(x+15, 273, 231)
        s += txt(x+15, 321, "放置当前维修记录", 20, GRAY)
    s += txt(42, 414, "关联批次、维修记录和当前接手角色。", 26, GRAY)
    return s


LAYOUTS = {"visitor": visitor, "assembly": assembly, "receiving": receiving, "repair": repair}


def source_svg(module, metadata):
    title = ESC(module["title"])
    body = LAYOUTS[module["id"]]()
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="{title}">'
            f'<title>{title}</title><metadata>{ESC(json.dumps(metadata, ensure_ascii=False))}</metadata>'
            f'<g font-family="{FONT}">{body}</g></svg>\n')


def review_card(module, source_url):
    linked = " · ".join(f'<a href="{BASE}#{key}">{key}</a>' for key in module["survey_refs"])
    return f'''<article id="{module['id']}">
<h3>{ESC(module["title"])}</h3>
<p class="summary">{ESC(module["summary"])}</p>
<figure>
<div class="compare">
<div><span>空白围板示意</span><div class="prior" aria-hidden="true"><i></i><i></i></div></div>
<div><span>加入信息后的示意</span><div class="proposed"><a href="{source_url}"><img src="{source_url}" width="{W}" height="{H}" alt="{ESC(module['title'])}"></a><i aria-hidden="true"></i></div></div>
</div>
</figure>
<dl>
<dt>去哪找板面</dt><dd>{ESC(module['position'])}</dd>
<dt>固定内容</dt><dd>{ESC(module['fixed'])}</dd>
<dt>可换内容</dt><dd>{ESC(module['replaceable'])}</dd>
<dt>现场怎么核</dt><dd>{ESC(module['site_check'])}</dd>
<dt>复核角色</dt><dd>{ESC(module['roles'])}</dd>
</dl>
<p class="links">V3.2 踏勘 {linked}　<a download href="{source_url}">下载可编辑 SVG</a></p>
</article>'''


def page_content(data, cards):
    return f'''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>8F 围板设计补充 | V3.4</title>
<style>
:root{{--ink:#000;--text:#3e3a39;--line:#d0cdca;--accent:#ff6600}}
*{{box-sizing:border-box}}body{{margin:0;font:16px/1.59 {FONT};color:var(--text);background:#fff}}
header{{padding:31px 26px;background:#000;color:#fff}}header>div,main{{max-width:1270px;margin:auto}}
main{{padding:22px 26px 42px}}header h1{{margin:11px 0;font-size:clamp(29px,4vw,50px);line-height:1.16;}}
header p{{margin:.3em 0}}header a{{color:inherit}}nav{{display:flex;flex-wrap:wrap;gap:10px 22px;align-items:center;margin-top:15px}}
.primary{{background:var(--accent);color:#000;padding:8px 14px;text-decoration:none;font-weight:700}}a{{color:inherit;text-underline-offset:4px}}
a:focus-visible{{outline:3px solid var(--accent);outline-offset:3px}}
.pair{{margin:22px 0 32px}}.grid{{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:25px}}
h2,h3{{line-height:1.25;color:#000}}h2{{margin:0 0 13px;font-size:26px}}h3{{margin:0 0 7px;font-size:21px}}
article{{border-top:2px solid #000;padding:14px 0 8px}}article p{{margin:0 0 10px}}
figure{{margin:0 0 11px}}.compare>div>span{{display:block;font-weight:600;font-size:.86em;margin:6px 0 3px}}
.prior,.proposed{{background:#e7e4e1;border:1px solid #ada8a4;display:grid;grid-template-columns:minmax(0,5fr) minmax(0,1fr);align-items:stretch;gap:3px;padding:5px}}
.prior{{height:34px}}.prior i,.proposed i{{background:#f2f0ee;border:1px solid #c5c0bc;display:block}}.proposed a{{display:block;align-self:center}}
img{{width:100%;height:auto;display:block;border:1px solid var(--text)}}dl{{display:grid;grid-template-columns:max-content 1fr;gap:6px 11px;margin:0 0 12px}}
dt{{font-weight:700;color:#000}}dd{{margin:0}}.links{{font-size:.87em}}.site-notes{{border-top:2px solid var(--text);padding-top:20px}}.site-notes ul{{padding-left:1.2em}}
footer{{border-top:1px solid var(--line);padding-top:13px;font-size:.87em}}
.print-title{{display:none}}
@media(max-width:850px){{.grid{{grid-template-columns:minmax(0,1fr)}}main{{padding:17px 15px 30px}}}}
@media print {{
@page{{size:A3 landscape;margin:13mm}}
body{{font-size:13pt}}header,.site-notes,footer,.links{{display:none}}
main{{max-width:none;margin:0;padding:0}}.pair{{margin:0;break-after:page}}.pair:last-of-type{{break-after:auto}}
.grid{{grid-template-columns:repeat(2,minmax(0,1fr));gap:8mm}}
.print-title{{display:block;font-size:11pt;letter-spacing:.025em;margin:0 0 4mm;color:#3e3a39}}
h2{{font-size:25pt;margin-bottom:4mm}}h3{{font-size:19pt}}dt{{font-size:.95em}}article{{break-inside:avoid}}.prior{{height:9mm}}
}}
</style></head><body><header><div>
<p><a href="../打开这里.html">返回8楼当前方案</a>　/　V3.4 方案评审</p>
<h1>8F 围板设计补充</h1>
<p>在可用的实心围板上安排区域身份、作业资料和交接提示。每块板按主要读者选内容，留出板边、板缝及观察开口。</p>
<nav aria-label="文件和章节"><a class="primary" href="{PDF}">打开两页立面评审 PDF</a><a href="{SURVEY}" download>下载围板踏勘表</a>
<a href="#work">仓口与维修</a><a href="#site">现场复核</a></nav>
</div></header><main>
<section class="pair" id="visitor-assembly"><p class="print-title">BEEPUMP / 8F / V3.4 围板草案 · 立面、板跨与比例用于评审</p>
<h2>访客侧与装配工位侧</h2><div class="grid">{cards[0]}{cards[1]}</div></section>
<section class="pair" id="work"><p class="print-title">BEEPUMP / 8F / V3.4 围板草案 · 安装面、尺寸和固定待踏勘</p>
<h2>原料仓收货与维修交接</h2><div class="grid">{cards[2]}{cards[3]}</div></section>
<div class="site-notes" id="site"><h2>现场复核</h2>
<ul>
<li>先选一侧可读的实心板面。拍整面和接缝近照，记录正反面、有效净宽净高、材质、固定条件、读距及可停留空间。板体及开口以现场为准。</li>
<li>玻璃、网板、观察窗、活动门、通风、设备检修、急停和消防设施附近优先留白。已有标识与视线范围一并核对。</li>
<li>先按现场尺寸做一处纸样，站在实际位置读、走一遍通行路径，并实际试换文件。工程确认基材与固定，再按实物及印刷面核量。</li>
<li>优先复核装配工位侧。访客侧需先明确获准停留和可公开内容。</li></ul>
<p><a href="{SURVEY}" download>打开踏勘补充表</a> · <a href="{BASE}">对照V3.2点位补充</a></p></div>
<footer>{data["date"]} · 立面为排版示意。实际围板位置、尺寸、数量及制作安装待复核。</footer>
</main></body></html>'''


def main():
    data = json.loads(DATA.read_text())
    reference_path = ROOT / data["reference_manifest"]
    survey_data = json.loads((reference_path.parent / "踏勘项与参考映射.json").read_text())
    known = {row[0] for row in survey_data["candidates"]}
    known_details = {row["detail_id"] for row in json.loads((ROOT / "data/8F_current_scheme.json").read_text())["requirements"]}
    known_templates = {row["code"] for row in json.loads((ROOT / "data/templates.json").read_text())}
    modules = data["modules"]
    if [r["id"] for r in modules] != list(LAYOUTS):
        raise ValueError("围板样式与图稿不一致")
    OUT.mkdir(parents=True, exist_ok=True)
    assets, cards = [], []
    for module in modules:
        if not (set(module["survey_refs"]) <= known and set(module["template_refs"]) <= known_templates
                and set(module["detail_refs"]) <= known_details):
            raise ValueError(f'引用编号待确认 {module["id"]}')
        path = SRC / module["filename"]
        meta = dict(revision=data["revision"], status=data["status"], floor_id="8F", production_release=False,
                    size_basis="normalized drawing units only", site_size_mm=None, site_facing=None,
                    point_id=None, quantity=None, survey_refs=module["survey_refs"], detail_refs=module["detail_refs"],
                    template_refs=module["template_refs"])
        path.write_text(source_svg(module, meta))
        assets.append({"path": str(path.relative_to(ROOT)), "sha256": digest(path), **meta})
        cards.append(review_card(module, "../../design/v2/8f_partition_v3.4/" + path.name))
    fields = ["楼层", "围板用途", "V3.2核查项", "建议核查位置", "固定内容", "可换内容", "现场复核", "复核角色"]
    blanks = ["围板或资产位号", "照片编号", "阅读面或朝向", "材质或板体类别", "可用净宽mm", "可用净高mm",
              "板缝门窗及设备避让", "实际读距mm", "固定方式及工程复核", "实物件数", "印刷面数", "审核记录"]
    write_csv(OUT / SURVEY, fields + blanks, [
        ["8F", row["title"], " / ".join(row["survey_refs"]), row["position"], row["fixed"], row["replaceable"],
         row["site_check"], row["roles"]] + [""] * len(blanks) for row in modules])
    entry = OUT / "打开这里.html"
    entry.write_text(page_content(data, cards))
    manifest = {key: data[key] for key in ["revision", "status", "date", "floor_id", "production_release",
                                           "site_measurements", "world_points", "actual_quantities"]}
    manifest.update(reference_manifest=data["reference_manifest"], reference_sha256=digest(reference_path),
                    module_count=len(assets), assets=assets, register_sha256=digest(DATA),
                    delivery=[{"path": str(p.relative_to(ROOT)), "sha256": digest(p)} for p in (entry, OUT / SURVEY)]
                    + [{"path": str((OUT / PDF).relative_to(ROOT)), "type": "draft_pdf"}])
    (SRC / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")
    print(f"Built {len(assets)} editable partition-face proposals and field survey links.")


if __name__ == "__main__":
    main()

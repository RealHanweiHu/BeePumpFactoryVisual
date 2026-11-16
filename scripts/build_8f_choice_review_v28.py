#!/usr/bin/env python3
"""Build a local choice catalogue. Choices express design preferences, never release."""
import base64
import copy
import hashlib
import html
import json
from pathlib import Path
import shutil
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
DESIGN = ROOT/'design/v2/options_v2.8'
OUT = ROOT/'交付_8楼/多方案选择_V2.8'
V27 = ROOT/'交付_8楼/客梯入口修订_V2.7'
REV = 'V2.8-OPTIONS-DRAFT'


def esc(s): return html.escape(str(s), quote=True)
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(p, d): p.write_text(json.dumps(d, ensure_ascii=False, indent=2)+'\n')


def relation_svg(opt):
    kind=opt['diagram_type']; board='<rect x="198" y="30" width="145" height="72" fill="white" stroke="#000" stroke-width="2"/><rect x="198" y="30" width="145" height="17" fill="#000"/><rect x="198" y="47" width="145" height="4" fill="#FF6600"/><text x="270" y="80" text-anchor="middle" font-size="18">信息牌</text>'
    obj='<rect x="35" y="80" width="150" height="80" fill="#F3F3F0" stroke="#3E3A39" stroke-width="2"/><text x="110" y="113" text-anchor="middle" font-size="17">业务对象</text><text x="110" y="139" text-anchor="middle" font-size="14">设备／容器／岗位</text>'
    if kind in ('near_wall','wall','wall_mount'):
        structure='<path d="M20 20 H420" stroke="#3E3A39" stroke-width="6"/><text x="25" y="49" font-size="15">可用墙面候选</text>'
    elif kind in ('free_standing','stand','independent_carrier'):
        structure='<path d="M240 104 V165 M300 104 V165 M218 165 H323" stroke="#3E3A39" stroke-width="4"/><text x="221" y="187" font-size="14">独立载体候选</text>'
    elif kind in ('existing_carrier','existing_frame'):
        structure='<rect x="190" y="22" width="160" height="92" fill="none" stroke="#3E3A39" stroke-width="6"/><text x="206" y="143" font-size="14">既有载体候选</text>'
    elif kind in ('at_object','object','on_object'):
        board=board.replace('x="198"','x="88"').replace('x="270"','x="160"').replace('y="30"','y="69"').replace('y="47"','y="86"').replace('y="80"','y="119"')
        structure='<path d="M35 160 H185" stroke="#3E3A39" stroke-width="4"/>'
        obj='<rect x="35" y="50" width="230" height="115" fill="#F3F3F0" stroke="#3E3A39" stroke-width="2"/><text x="49" y="44" font-size="15">对象可用外侧面候选</text>'
    elif kind in ('overhead','suspended'):
        structure='<path d="M20 10 H420 M220 10 V28 M320 10 V28" stroke="#3E3A39" stroke-width="3"/><text x="250" y="132" font-size="14">吊挂关系候选</text>'
    else:
        structure='<path d="M193 160 H365" stroke="#3E3A39" stroke-width="4"/><text x="208" y="184" font-size="14">交接／读写载体候选</text>'
    return '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 440 220" role="img" aria-label="安装位置关系示意"><style>text{font-family:PingFang SC,Arial,sans-serif;fill:#3E3A39}</style>'+obj+structure+board+'<rect x="354" y="132" width="66" height="34" fill="white" stroke="#3E3A39"/><text x="387" y="155" text-anchor="middle" font-size="17">读者</text><path d="M355 145 L307 121" stroke="#888" stroke-dasharray="5 4" fill="none"/><text x="18" y="211" font-size="13">关系示意｜非比例、坐标、通道或安装尺寸</text></svg>'


def context_svg(anchor, source_data):
    if not anchor:
        return '<svg xmlns="http://www.w3.org/2000/svg" width="900" height="600" viewBox="0 0 900 600"><rect width="900" height="600" fill="#F4F4F0"/><g font-family="PingFang SC,Arial" fill="#3E3A39" text-anchor="middle"><text x="450" y="240" font-size="36">尚未定位</text><text x="450" y="305" font-size="26">先比较牌面与载体关系</text><text x="450" y="352" font-size="24">不在底图上虚设安装点</text></g></svg>'
    x,y=anchor['source_preview_pixel_anchor']; cw,ch=850,560
    cx=max(0,min(2200-cw,x-cw/2));cy=max(0,min(1679-ch,y-ch/2))
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="900" height="650" viewBox="0 0 900 650"><metadata>{esc(json.dumps({"revision":REV,"status":"source_object_context_not_installation_point","position_world":None,"production_release":False},ensure_ascii=False))}</metadata><rect width="900" height="650" fill="white"/><text x="20" y="39" font-family="PingFang SC,Arial" font-size="25">{esc(anchor["annotation_id"])}｜来源对象范围，非安装位置</text><svg x="20" y="65" width="860" height="565" viewBox="{cx} {cy} {cw} {ch}"><image width="2200" height="1679" href="data:image/png;base64,{source_data}"/><circle cx="{x}" cy="{y}" r="21" fill="none" stroke="#FF6600" stroke-width="5"/></svg></svg>'


CSS = '''*{box-sizing:border-box}body{margin:0;background:#f3f3ef;color:#3E3A39;font:16px/1.65 system-ui,-apple-system,"PingFang SC",sans-serif}a{color:inherit;text-underline-offset:4px}button,input,select,textarea{font:inherit}button{cursor:pointer}button:focus-visible,a:focus-visible,input:focus-visible,select:focus-visible,textarea:focus-visible{outline:3px solid #FF6600;outline-offset:3px}header{background:#000;color:#fff;padding:32px max(24px,calc((100vw - 1460px)/2))}h1{font-size:34px;line-height:1.35;margin:8px 0 14px}header p{max-width:1100px;margin:8px 0}.eyebrow{font-size:13px;letter-spacing:.1em}.toolbar{position:sticky;top:0;z-index:5;background:#fff;border-bottom:1px solid #ccc;padding:12px 24px;display:flex;flex-wrap:wrap;gap:12px;align-items:center}.toolbar input[type=search]{min-width:230px;flex:1}.toolbar input[type=checkbox]{min-width:0;width:auto;flex:none;margin-right:8px}.toolbar select,.toolbar input,.toolbar button{padding:8px 12px;border:1px solid #bbb;background:#fff;color:#000}.toolbar .primary{background:#000;color:white;border-left:5px solid #FF6600}main{max-width:1500px;margin:auto;padding:24px}.intro{background:white;padding:20px 24px;margin-bottom:24px;border-left:5px solid #FF6600}.intro p{margin:8px 0}.req{background:white;padding:28px;margin:28px 0;scroll-margin-top:110px}.req[hidden]{display:none}.req-head{display:flex;justify-content:space-between;align-items:start;gap:24px;border-bottom:1px solid #ddd;padding-bottom:18px}.req h2{margin:0 0 8px;font-size:27px;line-height:1.4}.id{font-variant-numeric:tabular-nums;font-size:14px;color:#666}.context{width:240px;max-height:175px;object-fit:contain;background:#fafafa}.context-link{flex:none}.source-caption{font-size:13px;margin:3px 0}.anchor-note{font-size:14px;color:#555}fieldset{border:0;padding:0;margin:24px 0}legend{font-size:20px;font-weight:700;color:#000;margin-bottom:12px}.choices{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:16px}.choice{border:2px solid #d7d7d2;padding:16px;min-width:0}.choice:has(input:checked){border-color:#FF6600;background:#fffaf5}.choice-label{display:flex;align-items:baseline;gap:10px;font-size:18px;font-weight:700;color:#000;cursor:pointer}.choice-label input{accent-color:#FF6600;width:18px;height:18px;flex:none}.choice p{margin:9px 0}.style-desc{font-size:14px;min-height:48px}.template-grid{display:grid;gap:12px}.template-grid.multiple{grid-template-columns:repeat(2,minmax(0,1fr))}.thumb{border:0;background:#efefec;padding:10px;width:100%;display:block}.thumb img{width:100%;height:190px;object-fit:contain;display:block}.multiple .thumb img{height:126px}.template-title{font-size:13px;line-height:1.45;margin:6px 0}.nominal{font-size:12px;color:#666}.relation svg{width:100%;height:160px;background:#fafafa}.choice dl{font-size:14px;margin:10px 0}.choice dt{font-weight:700;float:left;clear:left;margin-right:6px}.choice dd{margin:0 0 8px}.choice details{font-size:13px}.choice ul{padding-left:20px}.note-row{display:flex;gap:16px;align-items:start}.note-row textarea{flex:1;min-height:70px;padding:10px;border:1px solid #aaa;resize:vertical}.note-row button{padding:8px 14px;background:white;border:1px solid #aaa}.selection-status{font-size:14px;color:#555;margin-top:10px}.summary{background:white;padding:24px;overflow:auto}.summary table{width:100%;border-collapse:collapse;font-size:14px}.summary th,.summary td{padding:9px 12px;border-bottom:1px solid #ddd;text-align:left;vertical-align:top}.summary h2{margin-top:0}#notice{font-size:14px;min-height:24px}#zoom{width:min(96vw,1400px);max-height:94vh;border:1px solid #777;padding:18px}#zoom::backdrop{background:#0009}#zoom img{width:100%;height:78vh;object-fit:contain;background:#f5f5f3}.zoom-top{display:flex;align-items:center;justify-content:space-between;gap:12px}.zoom-top button{background:#000;color:white;padding:8px 16px;border:0}.hidden{display:none}.print-page{display:none}@media(max-width:850px){.choices{grid-template-columns:1fr}.req-head{display:block}.context{width:100%;max-height:240px;margin-top:15px}.req{padding:18px}.note-row{display:block}.note-row textarea{width:100%}.style-desc{min-height:0}.toolbar{position:static}.thumb img{height:260px}.multiple .thumb img{height:180px}h1{font-size:27px}main{padding:12px}}@media print{header,.toolbar,.req,.intro,dialog,#notice{display:none!important}main{max-width:none;padding:0}.summary{padding:0}.summary h2:after{content:"（设计偏好记录，未作制作安装批准）";font-size:12px}body{background:white;font-size:12px}.summary th,.summary td{padding:7px}}'''

APP = r'''
const catalogue=JSON.parse(document.getElementById('catalogue-data').textContent);
const storageKey='beepump-8f-options-v28';
const allowed=new Set(catalogue.requirements.map(r=>r.requirement_id));
let choices={};
function blank(){return {style:null,placement:null,note:''};}
function normalize(raw){
 const value={};
 for(const id of allowed){const r=raw[id]||{};value[id]={style:['A','B','C'].includes(r.style)?r.style:null,placement:['P1','P2','P3'].includes(r.placement)?r.placement:null,note:typeof r.note==='string'?r.note.slice(0,2000):''};}
 return value;
}
let storageWarning='';
try{const saved=JSON.parse(localStorage.getItem(storageKey)||'null');if(saved&&saved.catalogue_sha256===catalogue.catalogue_sha256){choices=normalize(saved.choices||{});}else{choices=normalize({});if(saved)storageWarning='方案目录已更新，旧选择没有自动套用。请按本版重新核对。';}}catch{choices=normalize({});}
const el=id=>document.getElementById(id);
function announce(s){el('notice').textContent=s;}
function persist(){try{localStorage.setItem(storageKey,JSON.stringify({catalogue_sha256:catalogue.catalogue_sha256,choices}));}catch{announce('浏览器未能保存，请导出选择清单保留。');}}
function updateSummary(){
 const tbody=el('summary-body');tbody.replaceChildren();let complete=0,started=0;
 for(const r of catalogue.requirements){const c=choices[r.requirement_id];if(c.style&&c.placement)complete++;if(c.style||c.placement||c.note)started++;
  const tr=document.createElement('tr');
  const vals=[r.detail_id+' '+r.name,c.style?c.style+' '+catalogue.styles.find(s=>s.id===c.style).label:'未选择',c.placement?c.placement+' '+r.placement_options.find(p=>p.id===c.placement).title:'未选择',c.note||''];
  for(const v of vals){const td=document.createElement('td');td.textContent=v;tr.append(td);}tbody.append(tr);
  const status=document.querySelector('[data-status="'+r.requirement_id+'"]');status.textContent='当前：样式 '+(c.style||'未选')+' ／ 位置关系 '+(c.placement||'未选');
 }
 el('progress').textContent=complete+' / 21 项已选两类方案';el('started').textContent=started+' 项有选择或备注；可混选，例如样式 B ＋ 位置关系 P2。';
}
function hydrate(){for(const id of allowed){const c=choices[id];const req=document.querySelector('[data-req="'+id+'"]');req.querySelectorAll('input[type=radio]').forEach(i=>i.checked=c[i.dataset.kind]===i.value);req.querySelector('textarea').value=c.note;}updateSummary();filter();}
function filter(){const q=el('search').value.trim().toLowerCase(),g=el('group').value,open=el('only-open').checked;let n=0;
 document.querySelectorAll('.req').forEach(e=>{const c=choices[e.dataset.req],match=(!q||e.dataset.search.includes(q))&&(!g||e.dataset.group===g)&&(!open||!c.style||!c.placement);e.hidden=!match;if(match)n++;});el('shown').textContent='显示 '+n+' 项';}
document.querySelectorAll('.req').forEach(req=>{
 req.addEventListener('change',e=>{if(e.target.matches('input[type=radio]')){choices[req.dataset.req][e.target.dataset.kind]=e.target.value;persist();updateSummary();filter();}});
 req.querySelector('textarea').addEventListener('input',e=>{choices[req.dataset.req].note=e.target.value.slice(0,2000);persist();updateSummary();});
 req.querySelector('[data-clear]').addEventListener('click',()=>{choices[req.dataset.req]=blank();persist();hydrate();});
});
['search','group','only-open'].forEach(id=>el(id).addEventListener('input',filter));
function download(name,type,text){const url=URL.createObjectURL(new Blob([text],{type}));const a=document.createElement('a');a.href=url;a.download=name;a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);}
el('export-json').addEventListener('click',()=>{const rows=catalogue.requirements.map(r=>({requirement_id:r.requirement_id,detail_id:r.detail_id,name:r.name,...choices[r.requirement_id]}));download('8F_V2.8_方案选择.json','application/json',JSON.stringify({record_type:'design_preference_selection',revision:catalogue.revision,catalogue_sha256:catalogue.catalogue_sha256,choices:rows,position_world:null,production_release:false},null,2));announce('选择清单已导出。可将 JSON 发回继续深化。');});
const csvCell=s=>{let v=String(s??'');if(/^\s*[=+@-]/.test(v))v="'"+v;return '"'+v.replaceAll('"','""')+'"';};
el('export-csv').addEventListener('click',()=>{const rows=[['需求编号','需求名称','牌面样式','位置关系','备注','选择性质'],...catalogue.requirements.map(r=>[r.detail_id,r.name,choices[r.requirement_id].style,choices[r.requirement_id].placement,choices[r.requirement_id].note,'设计偏好；未作制作安装批准'])];download('8F_V2.8_方案选择.csv','text/csv;charset=utf-8','\uFEFF'+rows.map(r=>r.map(csvCell).join(',')).join('\r\n'));});
el('import-file').addEventListener('change',async e=>{const f=e.target.files[0];if(!f)return;try{if(f.size>1024*1024)throw Error('文件过大');const data=JSON.parse(await f.text());if(data.record_type!=='design_preference_selection'||data.revision!==catalogue.revision||data.catalogue_sha256!==catalogue.catalogue_sha256||!Array.isArray(data.choices))throw Error('选择文件与本版方案目录不一致');const incoming={};for(const r of data.choices){if(!allowed.has(r.requirement_id)||incoming[r.requirement_id])throw Error('含未知或重复需求');incoming[r.requirement_id]=r;}choices=normalize(incoming);persist();hydrate();announce('已导入本版设计偏好。');}catch(error){announce('导入失败：'+error.message);}e.target.value='';});
el('print-summary').addEventListener('click',()=>window.print());
el('import-picker').addEventListener('click',()=>el('import-file').click());
document.querySelectorAll('[data-zoom]').forEach(b=>b.addEventListener('click',()=>{el('zoom-image').src=b.dataset.zoom;el('zoom-title').textContent=b.dataset.title;el('zoom-source').href=b.dataset.zoom;el('zoom').showModal();}));
el('close-zoom').addEventListener('click',()=>el('zoom').close());
hydrate();
if(storageWarning)announce(storageWarning);
'''


def template_markup(r, style, variants, image_cache):
    parts=[]
    for ref in r['template_references']:
        key=(style['id'],Path(ref['recommended_svg_path']).name)
        v=variants[key]; dest=image_cache[key]
        title=f'{ref["code"]} {ref["name"]}｜样式 {style["id"]}'
        dims=' × '.join(str(n) for n in ref['nominal_size_mm'])
        parts.append(f'<div><button type="button" class="thumb" data-zoom="{esc(dest)}" data-title="{esc(title)}" aria-label="放大 {esc(title)}"><img src="{esc(dest)}" alt="{esc(title)}" loading="lazy"></button><div class="template-title">{esc(ref["code"])} {esc(ref["name"])}</div><div class="nominal">{esc(dims)} mm · 既有模板名义整版尺寸</div></div>')
    return '<div class="template-grid count-'+str(len(parts))+' '+('multiple' if len(parts)>1 else '')+'">'+''.join(parts)+'</div>'


def build():
    OUT.mkdir(parents=True,exist_ok=True);(OUT/'styles').mkdir(exist_ok=True);(OUT/'contexts').mkdir(exist_ok=True)
    original=json.loads((V27/'逐项需求与来源_V2.7.json').read_text())
    place=json.loads((DESIGN/'placement_options.json').read_text())
    pm={r['requirement_id']:r for r in place['requirements']}
    manifest=json.loads((DESIGN/'style_manifest.json').read_text())
    variants={(v['style_id'],Path(v['source_path']).name):v for v in manifest['variants']}
    styles=manifest['styles']; assert len(styles)==3
    assert [s['id'] for s in styles]==['A','B','C']
    req_ids=[r['requirement_id'] for r in original['requirements']]
    assert len(req_ids)==len(set(req_ids))==21
    assert set(pm)==set(req_ids)
    assert len(variants)==78
    image_cache={}
    for key,v in variants.items():
        dest=Path('styles')/v['style_id']/Path(v['path']).name
        (OUT/dest).parent.mkdir(exist_ok=True);shutil.copyfile(ROOT/v['path'],OUT/dest)
        meta=(ROOT/v['path']).with_suffix('.meta.json')
        if meta.exists():shutil.copyfile(meta,(OUT/dest).with_suffix('.meta.json'))
        image_cache[key]=dest.as_posix()
    data64=base64.b64encode((ROOT/'交付_8楼/逐项样式尺寸_参观预览_V2.6/原始底图_只读.png').read_bytes()).decode()
    contexts={}; requirements=[]; articles=[]; print_pages=[]
    for i,r in enumerate(original['requirements'],1):
        rid=r['requirement_id'];detail=f'D{i:02}';p=pm[rid];a=original['source_annotation_map'].get(rid);group=a['annotation_id'] if a else 'UNLOCATED'
        if group not in contexts:
            dest='contexts/'+group+'.svg'
            content=context_svg(a,data64)
            if '<metadata>' not in content:
                content=content.replace('><rect','><metadata>'+esc(json.dumps({'revision':REV,'status':'draft_unlocated_context','position_world':None,'production_release':False},ensure_ascii=False))+'</metadata><rect',1)
            (DESIGN/'contexts').mkdir(exist_ok=True)
            (DESIGN/dest).write_text(content);(OUT/dest).write_text(content);contexts[group]=dest
        ops=p['options'];assert [o['id'] for o in ops]==['P1','P2','P3']
        style_cards=[];print_styles=[]
        for st in styles:
            thumbs=template_markup(r,st,variants,image_cache)
            style_cards.append(f'<article class="choice style-card"><label class="choice-label"><input type="radio" name="style-{rid}" data-kind="style" value="{st["id"]}">{st["id"]} · {esc(st["label"])}</label><p class="style-desc">{esc(st["description"])}</p>{thumbs}</article>')
            print_thumbs=thumbs.replace(' loading="lazy"','')
            print_styles.append(f'<div class="print-choice"><h3>{st["id"]} · {esc(st["label"])}</h3>{print_thumbs}</div>')
        loc_cards=[];print_locs=[]
        for op in ops:
            check=''.join(f'<li>{esc(c)}</li>' for c in op['site_checks'])
            diagram=relation_svg(op)
            loc_cards.append(f'<article class="choice location-card"><label class="choice-label"><input type="radio" name="placement-{rid}" data-kind="placement" value="{op["id"]}">{op["id"]} · {esc(op["title"])}</label><div class="relation">{diagram}</div><dl><dt>位置关系</dt><dd>{esc(op["placement_relation"])}</dd><dt>载体／读面</dt><dd>{esc(op["carrier"])}；{esc(op["reading_side"])}</dd><dt>适合</dt><dd>{esc(op["why_choose"])}</dd><dt>取舍</dt><dd>{esc(op["tradeoff"])}</dd></dl><details><summary>现场需核对的条件</summary><ul>{check}</ul></details></article>')
            print_locs.append(f'<div class="print-choice"><h3>{op["id"]} · {esc(op["title"])}</h3><div class="relation">{diagram}</div><p><b>位置：</b>{esc(op["placement_relation"])}</p><p><b>适合：</b>{esc(op["why_choose"])}</p><p><b>取舍：</b>{esc(op["tradeoff"])}</p></div>')
        anchor_label=a['title'] if a else '尚未定位；不将候选载体画成真实点位'
        srch=esc(' '.join([detail,rid,r['name'],anchor_label]+[t['code'] for t in r['template_references']]).lower())
        articles.append(f'<section class="req" id="{detail}" data-req="{rid}" data-group="{group}" data-search="{srch}"><div class="req-head"><div><div class="id">{detail} · {rid}</div><h2>{esc(r["name"])}</h2><p>{esc(r["reading_decision"])}</p><p class="anchor-note">来源范围：{esc(anchor_label)}<br>面向：{esc("、".join(r["reading_actor"]))}</p></div><a class="context-link" href="{contexts[group]}" target="_blank"><img class="context" src="{contexts[group]}" alt="来源对象范围"><p class="source-caption">放大来源范围；不是待选安装点</p></a></div><fieldset><legend>① 选牌面样式</legend><div class="choices">{"".join(style_cards)}</div></fieldset><fieldset><legend>② 独立选安装位置关系</legend><div class="choices">{"".join(loc_cards)}</div></fieldset><label for="note-{detail}">本项备注</label><div class="note-row"><textarea id="note-{detail}" maxlength="2000" aria-label="{detail} 备注" placeholder="例如：样式 B，位置 P2；希望与相邻看板合并。"></textarea><button type="button" data-clear>清除本项选择</button></div><p class="selection-status" data-status="{rid}"></p></section>')
        print_pages.append(f'<section class="sheet" id="print-{detail}"><div class="print-head"><div><span>{detail} / {rid}</span><h2>{esc(r["name"])}</h2></div><div class="print-anchor">{esc(anchor_label)}</div></div><p class="print-purpose">{esc(r["reading_decision"])}</p><h4>牌面样式 · A / B / C</h4><div class="print-grid style-row">{"".join(print_styles)}</div><h4>安装位置关系 · P1 / P2 / P3（示意，不是实际点位）</h4><div class="print-grid location-row">{"".join(print_locs)}</div><div class="paper-choice">我的选择：样式 □ A　□ B　□ C　　　位置关系 □ P1　□ P2　□ P3　　　备注：________________________________</div><footer>V2.8 设计偏好评审稿 · 名义尺寸沿用源模板；实体尺寸/高度/数量待核 · 选择不构成制作安装批准　|　{i+2} / 23</footer></section>')
        requirements.append({'requirement_id':rid,'detail_id':detail,'name':r['name'],'source_anchor_id':a['annotation_id'] if a else None,'source_anchor_title':anchor_label,'template_references':r['template_references'],'placement_options':ops,'style_options':[s['id'] for s in styles],'position_world':None,'actual_quantity':None,'production_release':False})
    data={'revision':REV,'record_type':'design_option_catalogue','styles':styles,'requirements':requirements,'source_requirements_sha256':sha(V27/'逐项需求与来源_V2.7.json'),'style_manifest_sha256':sha(DESIGN/'style_manifest.json'),'placement_options_sha256':sha(DESIGN/'placement_options.json'),'production_release':False}
    data['catalogue_sha256']=hashlib.sha256(json.dumps(data,ensure_ascii=False,sort_keys=True).encode()).hexdigest()
    dump(OUT/'方案目录.json',data);dump(OUT/'空白选择清单.json',{'revision':REV,'record_type':'design_preference_selection','catalogue_sha256':data['catalogue_sha256'],'choices':[{'requirement_id':r['requirement_id'],'detail_id':r['detail_id'],'style':None,'placement':None,'note':''} for r in requirements],'production_release':False})
    opts='<option value="">全部来源范围</option>'+''.join(f'<option value="{g}">{esc(g if g!="UNLOCATED" else "尚未定位（3项）")}</option>' for g in contexts)
    header='<header><div class="eyebrow">BEEPUMP / 8F / V2.8</div><h1>每项方案，由你来选</h1><p>21 项需求，每项 3 种牌面样式 ＋ 3 种安装位置关系。两类可独立混选，点牌面可放大查看。</p><p>右上客梯及用户标注进入方向沿用 V2.7。关系示意不指定现场坐标；实体尺寸、安装面和数量由后续量尺核对。</p></header>'
    toolbar='<nav class="toolbar" aria-label="方案工具"><input id="search" type="search" aria-label="搜索需求或模板" placeholder="搜索需求、区域或模板码"><select id="group" aria-label="来源范围筛选">'+opts+'</select><label><input id="only-open" type="checkbox"> 仅看未选完</label><span id="shown"></span><a href="#summary">选择汇总</a><button id="export-json" class="primary">导出选择 JSON</button><button id="export-csv">导出 CSV</button><button id="import-picker">导入选择</button><input class="hidden" type="file" accept=".json,application/json" id="import-file"><a href="print_book.html" target="_blank">完整打印册</a></nav>'
    intro='<div class="intro"><b id="progress"></b><p id="started"></p><p>初始没有预选。浏览器会尝试保留本机选择；请导出 JSON 保存，并将其发回继续深化。选择仅记录设计偏好。</p><p><a href="../客梯入口修订_V2.7/START_HERE.html">入口纠错依据 V2.7</a> · <a href="方案目录.json">全部方案与来源</a> · <a href="output/pdf/BeePump_8F_Options_V2.8.pdf">23 页 PDF 比较册</a></p><div id="notice" role="status" aria-live="polite"></div></div>'
    summary='<section class="summary" id="summary"><h2>我的逐项选择</h2><p>样式与位置关系分别选择；尚未选择的项目保留为空。</p><button id="print-summary">打印选择汇总</button><table><thead><tr><th>需求</th><th>牌面样式</th><th>位置关系</th><th>备注</th></tr></thead><tbody id="summary-body"></tbody></table></section>'
    modal='<dialog id="zoom"><div class="zoom-top"><b id="zoom-title"></b><a id="zoom-source" target="_blank">单独打开 SVG</a><button id="close-zoom">关闭</button></div><img id="zoom-image" alt="放大的牌面样式"></dialog>'
    payload=json.dumps(data,ensure_ascii=False).replace('<','\\u003c')
    (OUT/'START_HERE.html').write_text('<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>8楼多方案选择 V2.8</title><style>'+CSS+'</style>'+header+toolbar+'<main>'+intro+''.join(articles)+summary+'</main>'+modal+'<script type="application/json" id="catalogue-data">'+payload+'</script><script>'+APP+'</script></html>')
    print_css='''*{box-sizing:border-box}body{margin:0;background:#e9e9e5;color:#3e3a39;font:16px/1.55 "PingFang SC",Arial,sans-serif}.sheet{width:1495px;height:1030px;background:white;margin:25px auto;padding:24px 30px;position:relative;overflow:hidden;break-after:page}.sheet h2{font-size:30px;margin:3px 0}.sheet h4{font-size:19px;margin:13px 0 8px}.print-head{display:flex;justify-content:space-between;gap:24px;border-bottom:4px solid #000;padding-bottom:10px}.print-anchor{font-size:15px;width:420px;text-align:right}.print-purpose{font-size:16px;margin:10px 0}.print-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:18px}.print-choice{border:1px solid #bbb;padding:10px 13px;min-width:0}.print-choice h3{font-size:19px;margin:0 0 8px}.style-row{height:312px}.style-row .template-grid{display:grid;grid-template-columns:1fr;gap:6px}.style-row .multiple{grid-template-columns:repeat(2,minmax(0,1fr))}.thumb{display:block;border:0;background:#f4f4f0;padding:4px;width:100%}.thumb img{width:100%;height:183px;object-fit:contain}.multiple .thumb img{height:86px}.count-2 .thumb img{height:183px}.template-title{font-size:12px;line-height:1.35}.nominal{font-size:11px}.location-row{height:345px}.location-row .relation svg{width:100%;height:115px}.location-row p{font-size:14px;line-height:1.45;margin:5px 0}.paper-choice{border-top:2px solid #000;margin-top:17px;padding-top:15px;font-size:18px}footer{position:absolute;bottom:18px;left:30px;right:30px;font-size:12px;color:#555;border-top:1px solid #ddd;padding-top:8px}.cover h1{font-size:48px;line-height:1.3;margin:22px 0}.cover .bar{height:14px;background:#FF6600;width:190px}.cover .index{columns:3;font-size:18px;line-height:2}.cover .big{font-size:27px;margin:25px 0}.source-map{display:block;width:1400px;height:875px;object-fit:contain}@page{size:A3 landscape;margin:12mm}@media print{body{background:white}.sheet{margin:0;padding:16px 24px;width:1495px;height:1030px}.print-nav{display:none}}'''
    index=''.join(f'<div>{r["detail_id"]}　{esc(r["name"])}</div>' for r in requirements)
    cover='<section class="sheet cover"><p>BEEPUMP / 8F / V2.8 设计评审</p><div class="bar"></div><h1>8 楼逐项多方案<br>样式与位置关系选择册</h1><p class="big">21 项需求　×　3 种样式　＋　3 种位置关系</p><p>每项可混选，例如 B ＋ P2。纸面勾选后可在本地选型页录入、备注和导出。</p><div class="index">'+index+'</div><p>尺寸为既有模板名义尺寸；关系图不是现场点位。右上客梯沿用用户 V2.7 标注。</p><footer>设计偏好选择不构成制作安装批准 · production_release=false　|　1 / 23</footer></section>'
    sourcepage='<section class="sheet"><h2>8F 来源与已纠正客梯</h2><img class="source-map" src="../客梯入口修订_V2.7/8楼_客梯与进入方向修正_V2.7.png" alt="V2.7右上客梯纠错依据"><footer>本册各位置方案只比较关系，不在未校准底图上增加候选安装坐标　|　2 / 23</footer></section>'
    (OUT/'print_book.html').write_text('<!doctype html><html lang="zh-CN"><meta charset="utf-8"><title>8楼多方案打印册 V2.8</title><style>'+print_css+'</style><p class="print-nav"><a href="START_HERE.html">返回可选择方案</a>　<button onclick="window.print()">打印完整方案</button></p>'+cover+sourcepage+''.join(print_pages)+'</html>')
    dump(OUT/'来源与输出说明.json',{'revision':REV,'requirements':21,'style_variants':len(variants),'style_groups':63,'placement_options':63,'position_world':None,'actual_quantity':None,'production_release':False,'source_requirements':str((V27/'逐项需求与来源_V2.7.json').relative_to(ROOT)),'source_requirements_sha256':sha(V27/'逐项需求与来源_V2.7.json'),'style_manifest_sha256':sha(DESIGN/'style_manifest.json'),'placement_options_sha256':sha(DESIGN/'placement_options.json')})
    print(json.dumps({'output':str(OUT),'requirements':21,'styles':len(variants),'placement_options':63,'print_pages':23},ensure_ascii=False))


if __name__=='__main__':build()

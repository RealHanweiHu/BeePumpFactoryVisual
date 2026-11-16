"""Build a local per-requirement concept gallery, without treating concepts as site points."""
from pathlib import Path
import csv
import hashlib
import html
import json
import os

ROOT=Path(__file__).resolve().parents[1]
SRC=ROOT/'design/v2/point_effects_2026-10-26'
REPORT=ROOT/'reports/point_effects_2026-10-26'
OUT=ROOT/'交付_8楼/逐点效果与功能优化_2026-10-26'
REV='8F-POINT-EFFECTS-2026-10-26-DRAFT'

FOCUS={
 'D01':('到层身份与获准范围分开；接待与范围采用可换信息。','正式Logo、访客范围、固定面。'),
 'D02':('远读区域吊牌、近读柱牌/文件与线边地址形成层级。','区域边界、真实名称/ID、安装面、工位适用。'),
 'D03':('区域字段只出现一次；永久柱号独立可换，不用区域号代替。','真实柱号、主进路、柱面保护与固定。'),
 'D04':('线头的计划/实际/差异与异常接手分开；工单与版本可换。','数据口径、更新责任、非通行驻足面。'),
 'D05':('SQDCP五项保持独立；下方行动卡落实接手、措施与验证。','指标口径/阈值、人员信息可见范围、更新动作。'),
 'D06':('库位地址固定，物料/批次卡可换；增加补料信号回收位。','实物地址、库存上限、补料触发与物流责任。'),
 'D07':('当前占用与批准上限分开；满位停投、冻结品退出普通FIFO。','车/箱/件口径、真实容量、先后顺序与物理可用面。'),
 'D08':('作业文件靠近实际读面，产品版本与进入条件分开更新。','受控内容、操作视线、换页可达、实际进入条件。'),
 'D09':('固定设备身份、可换设备状态和点检记录独立，不盖原牌。','资产台账、设备许可、固定面与检修可达。'),
 'D10':('质量卡同时保留色、词、对象、范围与签发；不作交通灯。','真实对象/批次、状态转换和品质签发权限。'),
 'D11':('测试项目/记录/结论与品质放行独立；只示外侧管理。','真实项目、工单适用、设备/工艺与专业条件。'),
 'D12':('当前包装文件、首件记录和旧版回收有独立位置。','实际包装/产品版次、清线、资料可见范围。'),
 'D13':('手推车定置、批次与跨层交接记录对应，去向不靠箭头猜。','左上成品梯接驳、C2门口、去向与承接责任。'),
 'D14':('工具影形对应工具；待判/维修中/待复检与质量卡分开。','维修工具清单、普通不良边界、复检接手与固定面。'),
 'D15':('在获准外侧讲解，展示范围/陪同与证据分别可换。','尚未定位；观察面、保密及实际停留/行走许可。'),
 'D16':('去向模块与方向模块可换；方向未核不印实箭头。','实际分岔、去向/箭头、遮挡和对应进路。'),
 'D17':('电子进入条件与记录分列，信息牌不替代设施或授权。','适用专业、电子进入规则；不新增ESD安全图形。'),
 'D18':('外采完整电池包暂存信息为条件项；对象/批次/接手留真值。','尚未定位；设施、存储条件和专项依据待核。'),
 'D19':('空器具归位与退料交接分开，地址与可换退料卡对应。','容器清单、退料状态、放行与接回责任。'),
 'D20':('样件、任务、版本、报告与结论形成对应，不编造验证能力。','尚未定位；真实项目/报告口径、展示权限与接手。'),
 'D21':('工具身份与有效状态分开，保留借还记录，工具轮廓待实样。','真实ID、量具有效依据、固定及不遮刻度。'),
 'U01':('老化/充电任务记录与品质放行分开；只表达外侧信息管理。','用户新增条件项；工艺/设备/电气/消防/回路/环境未核，不据图建设设施。')}

def read(p):return json.loads(p.read_text())
def save(p,j):p.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n')
def esc(s):return html.escape(str(s),quote=True)

def main():
    OUT.mkdir(parents=True,exist_ok=True)
    specs=read(SRC/'prompts.json')['prompts']
    catalogue=read(ROOT/'交付_8楼/多方案选择_V2.8/方案目录.json')
    by_id={r['detail_id']:r for r in catalogue['requirements']}
    manifest=read(SRC/'manifest.json') if (SRC/'manifest.json').exists() else {'revision':REV,'assets':[]}
    assets={r['key']:r for r in manifest['assets']}
    references=read(REPORT/'reference_records.json')
    core=read(SRC/'templates/manifest.json')
    new_templates={r['code']:r['path'] for r in core['templates']}
    proposals=[];sections=[]
    priority=['D14','D04','D02','D11','U01','D06']
    ordered=sorted(specs,key=lambda r:(0,priority.index(r['key'])) if r['key'] in priority else (1,r['key']))
    for spec in ordered:
        key=spec['key'];up=by_id.get(key);asset=assets.get(key);change,pending=FOCUS[key]
        templates=up['template_references'] if up else []
        row={'preview_id':spec['id'],'detail_id':key,'requirement_id':up['requirement_id'] if up else None,
             'scene':spec['title'],'record_type':'functional_concept_not_surveyed_point',
             'priority_scene':key in priority,'proposed_improvement':change,'pending':pending,
             'template_codes':[t['code'] for t in templates] if up else ['BT-02 (conditional carrier reference)'],
             'actual_point_id':None,'position_world':None,'actual_quantity':None,'actual_dimensions_mm':None,
             'production_release':False,'image_status':'generated' if asset else 'pending',
             'image_path':asset['path'] if asset else None,'selected_style':None}
        proposals.append(row)
        links=[]
        for t in templates:
            p=new_templates.get(t['code'],t['recommended_svg_path'])
            if not (ROOT/p).exists():p='交付_8楼/'+p
            links.append('<a href="'+esc(os.path.relpath(ROOT/p,OUT))+'">'+esc(t['code'])+'</a>')
        if asset:
            src=os.path.relpath(ROOT/asset['path'],OUT)
            picture=f'<figure><a href="{esc(src)}"><img src="{esc(src)}" alt="{esc(spec["title"])}功能场景概念，空间设备为示意" width="{asset["width_px"]}" height="{asset["height_px"]}" loading="lazy"></a><figcaption>生成场景 · <a href="{esc(src)}" download>保存原图</a> · {esc(str(asset["width_px"]))}×{esc(str(asset["height_px"]))}px</figcaption></figure>'
        else:picture='<div class="empty">效果图待生成；不使用其他场景代替。</div>'
        search=spec['title']+' '+key+' '+' '.join(row['template_codes'])
        sections.append(f'<section class="scene" id="{esc(spec["id"])}" data-search="{esc(search)}" data-priority="{str(row["priority_scene"]).lower()}"><p class="eyebrow">{esc(spec["id"])} · {esc(row["requirement_id"] or "用户新增条件项")}</p><h2>{esc(spec["title"])}</h2>{picture}<div class="details"><p><strong>这处怎样优化</strong><br>{esc(change)}</p><p><strong>现场仍需核实</strong><br>{esc(pending)}</p></div><p class="meta">关联模板：'+(' · '.join(links) if links else 'BT-02信息载体参考，充电适用性另核')+'</p></section>')
    save(ROOT/'data/8F_point_visual_proposals.json',{'revision':REV,'status':'draft','production_release':False,'functional_requirement_count':21,'supplemental_conditional_scene_count':1,'generated_image_count':len(assets),'proposals':proposals,'xiaohongshu_status':references['xiaohongshu_status']})
    fields=['预览编号','需求编号','场景','拟优化内容','现场待核','模板','图片状态','图片','实际点位ID','实际坐标','实物量','制作安装状态']
    with (OUT/'需求与效果图对照.csv').open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.writer(f);w.writerow(fields)
        for r in proposals:w.writerow([r['preview_id'],r['requirement_id'],r['scene'],r['proposed_improvement'],r['pending'],' / '.join(r['template_codes']),r['image_status'],r['image_path'] or '','','','','未放行'])
    source_links=''.join('<li><a href="'+esc(r['url'])+'">'+esc(r['title'])+'</a>：'+esc(r['application'])+'</li>' for r in references['sources'])
    external_note=('小红书案例读取状态：'+references['xiaohongshu_status'])
    meta=json.dumps({'revision':REV,'status':'draft_concept','production_release':False,'source_manifest':'design/v2/point_effects_2026-10-26/manifest.json'},ensure_ascii=False).replace('<','\\u003c')
    page='''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>BeePump｜8楼逐项效果与功能优化</title><style>*{box-sizing:border-box}body{margin:0;background:#fff;color:#3E3A39;font:17px/1.7 system-ui,-apple-system,"PingFang SC",sans-serif}main{max-width:1420px;margin:auto;padding:28px 32px 60px}h1,h2,h3{color:#000;line-height:1.35}h1{font-size:36px}h2{font-size:28px;margin:8px 0 18px}a{color:inherit;text-underline-offset:4px}a:focus-visible,button:focus-visible,input:focus-visible{outline:3px solid #FF6600;outline-offset:4px}.eyebrow,.meta,figcaption{font-size:13px}.eyebrow{font-weight:700;letter-spacing:.05em}.note{border-left:4px solid #FF6600;padding:14px 18px;background:#f5f5f5}.tools{display:flex;gap:16px;flex-wrap:wrap;margin:24px 0}input,button{font:inherit;padding:10px 14px;border:1px solid #aaa;background:#fff;color:#000}input{flex:1;min-width:220px}button[aria-pressed="true"]{background:#000;color:#fff}nav{display:flex;gap:12px 24px;flex-wrap:wrap}header{border-bottom:2px solid #000;padding-bottom:25px}.scene{border-top:1px solid #ccc;padding-top:27px;margin-top:42px}figure{margin:18px 0}img{display:block;width:100%;height:auto}figcaption{padding-top:8px}.details{display:grid;grid-template-columns:1fr 1fr;gap:22px}.details p{border-left:2px solid #aaa;padding-left:15px}.empty{padding:40px;background:#f2f2f2;border:1px dashed #aaa}details{margin:25px 0}summary{cursor:pointer;font-weight:700}footer{border-top:2px solid #000;padding-top:18px;font-size:13px;margin-top:40px}[hidden]{display:none!important}@media(max-width:760px){main{padding:20px 16px 40px}h1{font-size:28px}h2{font-size:23px}.details{grid-template-columns:1fr}.tools{gap:10px}input{width:100%}}@media print{.tools,nav{display:none}.scene{break-before:page}img{max-height:65vh;object-fit:contain}.details{font-size:12px}}</style><script type="application/json" id="artifact-metadata">__META__</script></head><body><main><header><p><a href="../打开这里.html">← 返回8楼方案</a></p><p class="eyebrow">BEEPUMP · 8F · 逐项功能方案</p><h1>每一处，都说清楚怎么识别和操作</h1><p>__COUNT__张已生成概念图 / 22个规划预览场景：覆盖21项既有需求，补充老化充电管理条件项。</p><p class="note">这些是功能场景，不是实测安装点。空间、设备、道具数量与材质为示意；实际point_id、位置、尺寸、数量和制作安装批准保持待核。A/B/C既有用户选择不被代选或重置。</p><nav><a href="#FX-8F-D14">维修台</a><a href="#FX-8F-D04">流水线头</a><a href="#FX-8F-D02">装配区</a><a href="#FX-8F-D11">测试区</a><a href="#FX-8F-U01">老化充电管理</a><a href="#FX-8F-D06">物料超市</a></nav><div class="tools"><input id="search" type="search" aria-label="搜索场景或模板" placeholder="搜索名称、D编号或模板代码"><button id="priority" aria-pressed="false">只看六个重点场景</button></div><p id="count" role="status"></p><p><a href="需求与效果图对照.csv" download>下载全部需求与效果图对照</a> · <a href="../../reports/point_effects_2026-10-26/templates_compare.html">六款模板前后对照</a> · <a href="../../docs/8F_逐项视觉优化说明.md">设计与参考说明</a></p></header><p id="no-results" hidden>没有匹配的场景，请修改关键词。</p>__SCENES__<section class="scene"><h2>参考与采用边界</h2><p class="note">__EXTERNAL__</p><ul>__SOURCES__</ul><p>只借用布局、对象对应、补料与可换信息的方法，不照搬他厂的尺寸、颜色标准、数据、法规或安全结论。品牌橙不上地面，蓝/绿/红/黄质量状态继续独立。</p></section><footer>8F-POINT-EFFECTS-2026-10-26-DRAFT · 未经制作安装确认。<br><a href="../../design/v2/point_effects_2026-10-26/prompts.json">完整提示词</a> · <a href="../../design/v2/point_effects_2026-10-26/manifest.json">逐图来源与哈希</a> · <a href="../../reports/point_effects_2026-10-26/交付记录.md">检查与未完成事项</a> · <a href="../效果预览_2026-10-26/打开效果预览.html">保留的三张早期概念</a></footer></main><script>const search=document.querySelector('#search'),button=document.querySelector('#priority'),scenes=[...document.querySelectorAll('[data-search]')];function filter(){const q=search.value.toLocaleLowerCase().trim(),only=button.getAttribute('aria-pressed')==='true';let n=0;for(const s of scenes){const match=(!q||s.dataset.search.toLocaleLowerCase().includes(q))&&(!only||s.dataset.priority==='true');s.hidden=!match;if(match)n++}document.querySelector('#count').textContent='显示 '+n+' / '+scenes.length+' 个功能场景；场景条数不等于实物点位数。';document.querySelector('#no-results').hidden=n!==0}search.addEventListener('input',filter);button.addEventListener('click',()=>{button.setAttribute('aria-pressed',String(button.getAttribute('aria-pressed')!=='true'));filter()});filter();</script></body></html>'''
    for key,value in [('__META__',meta),('__COUNT__',str(len(assets))),('__SCENES__',''.join(sections)),('__EXTERNAL__',esc(external_note)),('__SOURCES__',source_links)]:page=page.replace(key,value)
    page=page.replace('<div class="tools">','<p class="meta">图中少量背景小字可能有生成误差；正式牌面文字以可编辑SVG及受控内容为准。</p><div class="tools">',1)
    (OUT/'打开这里.html').write_text(page)
    print('Built gallery:',len(assets),'images for',len(proposals),'functional scene proposals.')

if __name__=='__main__':main()

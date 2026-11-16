#!/usr/bin/env python3
"""Color-filled floor proposal on the unchanged V3.0 source image."""
import base64
import copy
import csv
import html
import json
import shutil
from pathlib import Path
import build_8f_onplan_v30 as base

ROOT=base.ROOT
SRC=ROOT/'design/v2/ground_logistics_v3.1'
OUT=ROOT/'交付_8楼/地面物流规划_V3.1'
REV='V3.1-FLOOR-COLOR-DRAFT'
GRAY='#969B9F';WHITE='#FFFFFF';DARK='#3E3A39';YELLOW=base.YELLOW
PALETTE={
 'logistics':{'name':'物流通道','fill':GRAY,'edge':YELLOW,'text':WHITE,'meaning':'灰底＋黄边＋物流文字/方向'},
 'pedestrians':{'name':'人行通道','fill':WHITE,'edge':WHITE,'text':DARK,'meaning':'白色带＋人行文字；员工与访客到层分别注明'},
 'positioning':{'name':'普通定置','fill':GRAY,'edge':WHITE,'text':WHITE,'meaning':'白框＋用途/位号，不占通道'},
 'pending':{'name':'待检/待测','edge':base.BLUE,'text':base.BLUE},
 'released':{'name':'合格放行','edge':base.GREEN,'text':base.GREEN},
 'nonconforming':{'name':'普通不合格','edge':base.RED,'text':base.RED},
 'hold':{'name':'冻结 HOLD','edge':YELLOW,'text':'#000000'},
 'unresolved':{'name':'待核/预留','fill':None,'edge':DARK,'is_paint_instruction':False}}

def band(points,kind,width):
    d='M'+' L'.join(f'{x},{y}' for x,y in points)
    attr=' fill="none" stroke-linecap="butt" stroke-linejoin="round"'
    if kind=='logistics':
        return f'<path d="{d}"{attr} stroke="{YELLOW}" stroke-width="{width+5}"/><path d="{d}"{attr} stroke="{GRAY}" stroke-width="{width}"/>'
    # Show adjacent gray floor so a white paint band remains visible on white CAD.
    return f'<path d="{d}"{attr} stroke="{GRAY}" stroke-width="{width+14}" data-ground-context="illustration-not-extra-paint-area"/><path d="{d}"{attr} stroke="{WHITE}" stroke-width="{width}"/>'

def tag(x,y,words,kind='logistics',rotate=0,size=16):
    color=WHITE if kind=='logistics' else DARK
    # Plain management words, no new regulated safety symbol.
    return f'<text x="{x}" y="{y}" font-size="{size}" fill="{color}" font-weight="700" text-anchor="middle" transform="rotate({rotate},{x},{y})">{html.escape(words)}</text>'

def legend(x,y,width=1000):
    r,t=base.rect,base.txt
    s=t(x,y,'看底色和边界，就能分清通道',36,bold=True)
    entries=[('物流通道',GRAY,YELLOW,'灰底＋黄边，白色物流文字'),('人行通道',WHITE,DARK,'白色带，深灰“人行”文字'),('普通定置',GRAY,WHITE,'白框＋用途名称，不作为通道')]
    for i,(title,fill,edge,sub) in enumerate(entries):
        yy=y+32+i*143
        s+=r(x,yy,width,80,GRAY,DARK,1)+r(x+18,yy+12,265,55,fill,edge,5)
        s+=t(x+150,yy+49,title,28,WHITE if fill==GRAY else DARK,True,'middle')+t(x+310,yy+49,sub,28)
    s+=t(x,y+513,'质量定置色保持独立',34,bold=True)
    entries=[('待检 / 待测',base.BLUE),('合格放行',base.GREEN),('普通不合格',base.RED),('冻结 HOLD',YELLOW)]
    for i,(title,color) in enumerate(entries):
        cell=(width-35)/2;xx=x+(i%2)*(cell+35);yy=y+545+(i//2)*100
        s+=r(xx,yy,cell,75,'#FFFFFF',color,6)+t(xx+cell/2,yy+49,title,28,'#000000' if color==YELLOW else color,True,'middle')
    s+=base.note(x,y+795,'灰网纹/灰虚线＝待核，不是地面漆',['接驳门口、员工后续走段及未来电动预留','不把网纹范围当成现在就可以刷漆的通道','图中带宽是可视化宽度，实际净宽另核'])
    return s

def main():
    SRC.mkdir(parents=True,exist_ok=True);OUT.mkdir(parents=True,exist_ok=True);(SRC/'地贴样式').mkdir(exist_ok=True)
    previous=ROOT/'交付_8楼/地面物流规划_V3.0'
    manifest=copy.deepcopy(json.loads((previous/'原图标注与来源.json').read_text()))
    source=previous/'原始底图_只读.png';assert base.sha(source)==manifest['source_png_sha256']
    for rec in json.loads((ROOT/'data/sources.json').read_text())['inputs']:assert base.sha(ROOT/rec['path'])==rec['sha256']
    img='data:image/png;base64,'+base64.b64encode(source.read_bytes()).decode()
    routes=manifest['proposed_display_routes'];zones=manifest['proposed_display_zones']
    # Targeted collision repair of display proposals: avoid the visible west column.
    # This changes only the candidate overlay and creates no physical-width claim.
    for route in routes:
        if route['id']=='L02':route['segments']=[[[653 if x==661 else x,y] for x,y in seg] for seg in route['segments']]
        if route['id']=='L05':route['segments']=[[[687,464],[653,464],[653,345],[592,345],[592,318]]]
    manifest['display_revision_notes']=['西侧出料候选中心线661px移为653px，避开可见柱体；非毫米位移','空车返回候选线并入西侧同一走廊关系，是否分时/双向由现场核定']
    def overlay(mode):
        r,t,b=base.rect,base.txt,base.badge
        s='<g data-layer="reserve">'+r(1148,399,74,349,'url(#pendingHatch)',DARK,1.6,'stroke-dasharray="8 5"')+b(1185,768,'E01',DARK)+'</g>'
        # All logistics bodies are drawn first; smaller route arrows are not paint width.
        s+='<g data-layer="logistics">'
        active=[q for q in routes if q['id'].startswith('L') and (mode!='people' or q['id']=='L01')]
        for route in active:
            width=30 if route['id']=='L01' else 22
            for seg in route['segments']:s+=band(seg,'logistics',width)
        # White direction arrows are generic logistics cues, never evacuation arrows.
        for route in active:
            for seg in route['segments']:
                s+=base.line(seg,WHITE,2.2,'',True).replace('url(#arrow)','url(#whiteArrow)')
        if mode!='people':
            for x,y,k in [(1182,449,'L01'),(653,550,'L02'),(603,475,'L03'),(537,220,'L04'),(653,375,'L05')]:s+=b(x,y,k,DARK)
            s+=tag(900,220,'← 成品下楼',size=14)+tag(603,405,'物流',rotate=-90,size=14)
        s+=tag(1182,537,'物流',rotate=-90,size=16)+'</g>'
        s+='<g data-layer="pedestrians">'
        visitor=next(q for q in routes if q['id']=='P01')
        for seg in visitor['segments']:s+=band(seg,'pedestrians',16)
        s+=tag(1412,307,'人行',kind='pedestrians',rotate=-90,size=13)+tag(1505,493,'人行',kind='pedestrians',rotate=-90,size=13)+tag(1320,612,'人行',kind='pedestrians',size=14)
        s+=b(1530,424,'P01 访客人行',DARK)
        # Staff arrival is known; further walking/entry sequence is not known.
        staff=next(q for q in routes if q['id']=='P02')
        for seg in staff['segments']:s+=base.line(seg,DARK,2.8,'4 5',False)
        s+=r(1167,337,62,53,'url(#pendingHatch)',DARK,1.5,'stroke-dasharray="4 3"')+b(1125,352,'P02 员工待核',DARK)
        s+='</g><g data-layer="zones">'
        simple={'Z01':'来料交接','Z02':'放行备料','Z03':'线边接收','Z04':'WIP等待','Z05':'待检','Z06':'不合格','Z07':'冻结','Z08':'包装核对','Z09':'成品放行交接','Z10':'空车'}
        quality={'Z02':base.GREEN,'Z05':base.BLUE,'Z06':base.RED,'Z07':YELLOW,'Z09':base.GREEN}
        for z in zones:
            if mode=='people' and z['id'] not in ['Z03']:continue
            i=z['id'];x,y,w,h=z['source_display_rect_px'];c=quality.get(i)
            s+=r(x,y,w,h,c or GRAY,c or WHITE,3.5,'fill-opacity="0.22"' if c else 'fill-opacity="0.62"')
            fg='#000000' if c==YELLOW else (c or '#000000')
            small=h<45
            if small:s+=t(x+w/2,y+h/2+5,simple[i],min(15,w/max(len(simple[i]),1)-2),fg,True,'middle')
            else:s+=t(x+w/2,y+h/2-3,i,14,fg,True,'middle')+t(x+w/2,y+h/2+17,simple[i],16,fg,True,'middle')
        s+='</g><g data-layer="unresolved">'
        for route in routes:
            if route['id'].startswith('C-'):
                for seg in route['segments']:s+=base.line(seg,DARK,3,'4 7',False)
        for x,y,k in [(1184,612,'C1'),(213,220,'C2'),(1237,315,'C3')]:s+=f'<circle cx="{x}" cy="{y}" r="18" fill="white" stroke="{DARK}" stroke-width="2"/>'+t(x,y+6,k,17,DARK,True,'middle')
        for x,y,w,h,title in [(1248,259,80,115,'收料/员工'),(39,268,68,110,'成品下楼')]:s+=r(x,y,w,h,'none',DARK,3,'stroke-dasharray="7 4"')+b(x+w/2,y-18,title,DARK)
        s+=b(1319,180,'访客梯',DARK)
        for x,y in [(63,1248),(1289,1245)]:s+=r(x-45,y-65,90,130,'none',DARK,2,'stroke-dasharray="4 4"')+b(x,y+87,'暂不用',DARK)
        return s+'</g>'
    modes={k:overlay(k) for k in ['total','detail','people']}
    pages=[]
    def drawing(mode,x,y,w,h,vb):return f'<svg x="{x}" y="{y}" width="{w}" height="{h}" viewBox="{vb}" overflow="hidden"><image href="{img}" width="2200" height="1679"/>'+modes[mode]+'</svg>'
    def page(num,title,body,crop,transform):
        meta=dict(revision=REV,status='physical_floor_palette_proposal_not_installed',source_png_sha256=manifest['source_png_sha256'],source_drawing_sha256=manifest['source_drawing_sha256'],source_crop_display_px=crop,source_to_page_display_transform=transform,source_geometry_changed=False,physical_dimensions_mm=None,production_release=False,palette=PALETTE,band_widths_are_display_pixels=True,actual_quantities=None)
        svg=f'''<svg xmlns="http://www.w3.org/2000/svg" width="3400" height="2400" viewBox="0 0 3400 2400" role="img" aria-labelledby="title desc"><title id="title">8F 地面配色 {title} {REV}</title><desc id="desc">拟用地面配色直接覆盖原图，灰底黄边物流，白色人行；未核范围保持无涂装指定。不是现状照片或毫米施工图。</desc><metadata>{html.escape(json.dumps(meta,ensure_ascii=False))}</metadata><defs><marker id="whiteArrow" markerWidth="9" markerHeight="9" refX="7" refY="4" orient="auto" markerUnits="userSpaceOnUse"><path d="M0 0 L7 4 L0 8 Z" fill="white"/></marker><pattern id="pendingHatch" width="12" height="12" patternUnits="userSpaceOnUse"><path d="M-4 12 L12 -4 M3 19 L19 3" stroke="{DARK}" stroke-width="1" opacity="0.32"/></pattern></defs><g font-family="PingFang SC,Microsoft YaHei,Noto Sans CJK SC,Arial,sans-serif">{base.rect(0,0,3400,2400,WHITE)}{base.rect(0,0,3400,170,'#000000')}{base.txt(50,58,'BEEPUMP / 8F / 拟用地面颜色 / '+REV,28,WHITE)}{base.txt(50,125,'8F 地面配色｜'+title,52,WHITE,True)}{base.txt(3340,113,f'{num:02d} / 03',36,WHITE,True,'end')}{base.txt(50,222,'物流＝灰底黄边　｜　人行＝白色带＋人行文字　｜　中间货梯：收料＋员工　｜　小客梯：访客',32,bold=True)}{body}{base.line([[50,2255],[3350,2255]],'#A0A0A0',1,arrow=False)}{base.txt(50,2301,'配色评审稿 · 颜色对应拟用地面标识；图上带宽不等于实测净宽或线宽；未核段不指定刷漆',30,bold=True)}{base.txt(50,2347,'灰底为配色示意，现场基层/样色另核；人行白带两侧灰色仅表示地坪底色，不新增涂装范围。',27,DARK)}{base.txt(50,2384,'品牌橙不上地面；没有新增疏散/消防图形。实际定位、专项边界、材料、尺寸、数量与安装放行待核。',25,DARK)}</g></svg>'''
        name=f'{num:02d}_{title}.svg';(SRC/name).write_text(svg);base.dump(SRC/name.replace('.svg','.meta.json'),meta);pages.append(name)
    body=drawing('total',50,270,2200,1679,'0 0 2200 1679')+legend(2310,310)
    body+=base.note(2310,1438,'白色人行带的两类起点',['P01：小客梯上来的访客，沿既有示意分段标色','P02：员工在中间货梯到层，后续走段仍待核','员工待核区不涂成“已定人行通道”'])
    body+=base.note(2310,1690,'先区分用途，再定物理宽度',['灰底黄边带连接补料、工序转运与成品方向','白色人行带不作为载具临停或堆料位','C1/C3交叉接驳要另核分流，颜色不代替隔离'])
    body+=base.note(70,2040,'完整原图保留；彩色带只覆盖本轮候选范围',['左上梯用于成品下楼；左下/右下暂不规划使用。既有门、柱、墙、消防和原文字不修改。','普通定置与质量定置是区域用途，不能把蓝/绿/红/黄状态框当成人行/物流通行许可。'])
    page(1,'物流与人行彩色总图',body,[0,0,2200,1679],[1,0,0,1,50,270])
    body=drawing('detail',50,280,3300,1254,'0 165 1850 703')
    body+=base.note(60,1630,'灰底黄边：物流通道',['原料仓/电子仓门外的东侧带：补料主线，载具到线边接收接口。','西侧灰黄带：工序转运、适用测试/老化及空车返回关系；不得把柱体画成通行空地。','北侧灰黄带：包装/成品交接后，指向左上成品下楼梯；C2细虚线仍待核门口。'])
    body+=base.note(1760,1630,'白色带：人行通道提案',['P01访客从小客梯到层，按原有进入示意分段标白，不默认开放全部参观范围。','P02员工从中间货梯到层；下梯后更衣/进入条件与实际走段未知，灰网纹不指定刷漆。','人行与物流交叉C1、出梯分流C3仍待核；不得凭色带认定净宽或隔离已满足。'])
    body+=base.note(60,1950,'定置区只负责“放什么、什么状态”',['白框：线边接收、WIP、包装、空车等普通用途。蓝待检/待测、绿放行、红普通不合格、黄冻结保持原语义。','质量颜色配合真实批次/容器与状态卡使用；黄色物流边界与黄色冻结框依靠连续边界/区域形状和用途文字区分。'])
    page(2,'作业区实际配色放大图',body,[0,165,1850,703],[3300/1850,0,0,3300/1850,50,280-165*3300/1850])
    body=drawing('people',70,280,2332,1632.4,'540 165 1080 756')+legend(2460,330,width=890)
    body+=base.note(2460,1450,'中间货梯：收料＋员工到层',['灰黄带接物料；P02标员工到层接口','更衣/进入走段未核，不补画完整白带','C3接驳处核出梯人员与物料交接分流'])
    body+=base.note(2460,1710,'E01 未来电动预留',['灰网纹表示待核预留，不是现在涂装范围','扩展不能挤占人行、门扇、消防和检修','选型、满载转弯与会车条件核定后再定边界'])
    body+=base.note(70,2040,'配色提案与人车分流分别核查',['本图选择灰/黄物流、白色人行，不将质量放行绿改成人行语义；质量色仍独立使用。','定性参考：HSE Separating pedestrians and vehicles；不作为本地法规、尺寸或配色强制标准。'])
    scale=2332/1080;page(3,'人行通道与物流分界放大图',body,[540,165,1080,756],[scale,0,0,scale,70-540*scale,280-165*scale])
    for route in routes:
        route['upstream_annotation_style']=route['style']
        route['style']='gray_body_yellow_edges' if route['id'].startswith('L') else ('white_pedestrian_band_proposal' if route['id']=='P01' else 'uncolored_pending_staff_interface' if route['id']=='P02' else 'uncolored_gray_dotted_pending_link')
    manifest.update(revision=REV,supersedes='V3.0-ONPLAN-DRAFT',status='physical_floor_color_proposal',production_release=False,pages=pages,palette=PALETTE,
        no_orange_floor=True,original_source_geometry_changed=False,staff_onward_walkway_not_invented=True,
        colored_bands_are_not_physical_dimensions=True,palette_basis=['FM-01 V1 gray floor/yellow route boundary/white mobile-object positioning','V2.4 quality semantics and V2.9 no-quality-release-green-on-pedestrian convention','white pedestrian band is this revision proposal, not asserted existing paint or national standard'],
        references=[{'url':'https://www.hse.gov.uk/workplacetransport/separating.htm','scope':'qualitative pedestrian/vehicle separation only; no numeric or palette standard claim'}])
    refs=['交付_8楼/地面物流规划_V3.0/原图标注与来源.json','inputs/v1/BeePump_Design_Package/03_Templates_SVG/FM-01_地面定置图例.svg','design/v2/implementation_ops_v2.4/FM-01_地面定置图例_V2.4-IMPLEMENTATION-DRAFT.svg','docs/DECISIONS.md','data/tasks.json']
    manifest['source_records']=[dict(path=p,sha256=base.sha(ROOT/p)) for p in refs]
    base.dump(OUT/'地面配色与来源.json',manifest);base.dump(SRC/'revision_metadata.json',dict(revision=REV,status='draft',production_release=False,physical_dimensions_mm=None))
    base.dump(OUT/'FM-01_配色审查.json',dict(revision=REV,template_code='FM-01',decision='Refine',preserve=['灰底/黄边/白定位框','蓝待检绿放行红不合格黄冻结','无橙色地面','原图几何与原字不改'],refine=['用宽色带直接区分物流和人行','人行改白色带，不使用质量放行绿或旧注释紫色','未核门口与员工后续走段不指派涂装','西侧候选线避开可见柱体'],source_render='reports/implementation_operations_render/v1/FM-01.png',production_release=False))
    shutil.copy2(source,OUT/'原始底图_只读.png');shutil.copytree(SRC,OUT/'可编辑SVG',dirs_exist_ok=True)
    with (OUT/'地面颜色与用途.csv').open('w',encoding='utf-8-sig',newline='') as f:
        fields=['用途','地面底色_提案','边界或框色_提案','文字','范围','实际宽度_mm','实际数量','批准状态'];w=csv.DictWriter(f,fieldnames=fields);w.writeheader()
        for i,v in PALETTE.items():w.writerow(dict(zip(fields,[v['name'],v.get('fill') or '不指定整面涂装',v.get('edge',''),v.get('meaning',v['name']),'待核范围不指定刷漆' if i=='unresolved' else '见原图提案；实测另核','','','未制作安装放行'])))
    (OUT/'先读说明.md').write_text('''# 8F 地面实际配色提案 V3.1

本轮将V3.0原图注释线改为拟用地面配色色带，直接回答哪里是物流、哪里是人行。灰底黄边=物流；白色带配“人行”=人行；普通定置白框；蓝待检、绿放行、红普通不合格、黄冻结保持独立质量语义。白色人行是本轮设计提案，不是已证实现有地面，也不宣称国家统一颜色标准。灰底示意来自既有FM-01，不确认现场基层实际色值。品牌橙不上地面。

中间货梯：收料＋员工到层；小客梯：访客；左上梯：成品下楼；左下/右下暂不用。P01沿既有访客方向分段标白；P02只标员工到层，后续更衣/进入走段待核，不伪造连续人行通道。灰网纹/灰虚线用于待核接驳和未来电动预留，不指定现场照画、刷漆或通行。C1/C3交叉/分流另核，颜色不代替隔离或视线条件。

物流带显示宽度为图纸像素，不是毫米净宽、线宽或安全余量。西侧出料候选线和空车候选线做局部显示调整以避开可见柱体，不作为已完成净宽校核。未来电动扩展不能侵占人行、门扇、消防、设备检修；待车型、满载包络与现场核定。

原始PNG完整嵌入且保持哈希、纵横比与原文字。图签、物理单位、现场通路/门口/定置面、材料、防滑/适用ESD、尺寸、数量和人类批准仍待核。没有新增真实CAD点或工程量。

定性参考：[HSE人车分流](https://www.hse.gov.uk/workplacetransport/separating.htm)，仅参考分流、交叉与人员保护，不作为本地法规、数值或配色强制标准。
''')
    maps=''.join('<section>'+(SRC/n).read_text()+'</section>' for n in pages)
    controls=''.join(f'<label><input type="checkbox" checked data-toggle="{k}">{v}</label>' for k,v in [('logistics','灰黄物流'),('pedestrians','白色人行'),('zones','定置区'),('reserve','未来电动待核'),('unresolved','接口/待核')])
    (OUT/'打开地面配色图.html').write_text('''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>8F 地面配色 V3.1</title><style>body{margin:0;font-family:PingFang SC,Arial,sans-serif;background:#eee}header{padding:24px;background:white}p,label,a{font-size:18px;line-height:1.6}label{display:inline-block;margin-right:24px}a{color:#000}a:focus-visible,input:focus-visible{outline:3px solid #005EB8}section{margin:24px auto;max-width:3400px;background:white}section>svg{width:100%;height:auto;display:block}@media print{header{display:none}section{margin:0;break-after:page}@page{size:A3 landscape;margin:0}}</style><header><h1>8F 地面颜色：物流与人行 V3.1</h1><p>灰底黄边＝物流，白色带＝人行，质量色只用于对应定置用途。灰网纹/虚线待核，不指定刷漆。带宽不是毫米实测。</p><p><a href="8F_地面物流与地标规划_评审稿.pdf">打开3页配色PDF</a> · <a href="地面颜色与用途.csv">颜色与用途</a> · <a href="地面配色与来源.json">来源与提案范围</a></p>'''+controls+'</header>'+maps+'''<script>document.querySelectorAll('[data-toggle]').forEach(i=>i.addEventListener('change',()=>document.querySelectorAll('[data-layer="'+i.dataset.toggle+'"]').forEach(g=>g.style.display=i.checked?'':'none')))</script></html>''')
    print(json.dumps(dict(revision=REV,pages=len(pages),output=str(OUT)),ensure_ascii=False))

if __name__=='__main__':main()

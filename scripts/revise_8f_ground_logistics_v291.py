#!/usr/bin/env python3
"""Preserve V2.9 and record user-confirmed flow and future electric allowance."""
import csv
import hashlib
import json
import shutil
from pathlib import Path
from zipfile import ZipFile
import build_8f_ground_logistics_v29 as base

ROOT=Path(__file__).resolve().parents[1]
VERSION='V2.9.1'
REV=VERSION+'-GROUND-LOGISTICS-DRAFT'
OLD=ROOT/'交付_8楼/地面物流规划_V2.9'
OUT=ROOT/('交付_8楼/地面物流规划_'+VERSION)
SRC=ROOT/'design/v2/ground_logistics_v2.9.1'
EVIDENCE=ROOT/'data/8F_logistics_user_requirements_v2.9.1.json'

def read_previous(name):
    path = OLD / name
    if path.is_file():
        return path.read_bytes()
    archive = OLD.with_name('BeePump_8F_地面物流规划_V2.9_评审包.zip')
    with ZipFile(archive) as bundle:
        return bundle.read(f'{OLD.name}/{name}')

def main():
    copied_files = ['8F_地面放样与核量_待填.csv', '原始底图_只读.png']
    previous_files = {name: read_previous(name) for name in [*copied_files, '打开地面物流方案.html', '先读说明.md']}
    manifest=json.loads((OLD/'规划与来源.json').read_text())
    base.dump(EVIDENCE,dict(revision=REV,recorded_on='2026-10-18',source='Direct human user reply in current chat',
        current_transport={'value':'人工周转车','status':'user_confirmed','dimensions_mm':None},
        future_transport={'value':'电动搬运车','status':'under_consideration_allow_for_future','selected_type':None,'selected_model':None,'procurement_approval':None,'dimensions_mm':None},
        process={'value':['来料交接','装配','测试／老化','包装','成品交接'],'status':'user_confirmed_for_planning','aging_applicability':'per_actual_work_order_not_all_models_confirmed'},
        verbatim_replies=['目前是人工周转车，但之后考虑切换为电动搬运车，需要考虑预留','可以'],
        confirmation_scope='运输现状、未来预留意向与主流程；不是位置、尺寸、安全或制作安装批准',
        freight_lift_identified=False,physical_dimensions_mm=None,production_release=False))
    # Store the confirmation before hashing project context into the new manifest.
    tasks=ROOT/'data/tasks.json';data=json.loads(tasks.read_text())
    item=next(x for x in data if x['id']=='P16')
    item['acceptance']='V2.9.1保留V2.9，更新8页A3评审册及16份SVG（8页+8地贴）。用户确认当前人工周转车、未来考虑电动搬运车需预留，主流程来料交接→装配→测试/老化→包装→成品交接可按此深化。新增电动预留关系页及双工况测量CSV；未来车型、货梯、底图身份/单位、现场实测和真实定位尺寸/数量仍未核定。未制作安装放行；P02/P05阻塞保留。'
    tasks.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
    decisions=ROOT/'docs/DECISIONS.md';contents=decisions.read_text()
    heading='## 2026-10-18｜8F 人工周转车与未来电动搬运预留'
    if heading not in contents:
        decisions.write_text(contents+'\n'+heading+'\n\n用户确认目前采用人工周转车，之后考虑切换电动搬运车，需要预留；对“来料交接 → 装配 → 测试／老化 → 包装 → 成品交接”回答“可以”，作为本轮规划主流程。老化是否适用各工单仍按真实工艺核定。此回复没有指认货梯，也没有选定步行式、站驾式、牵引式或其他未来电动车型。\n\nV2.9.1提出分别核定人工和未来电动两种满载工况，主通道、转弯/交叉、接收和停放联动预留；未核定候选扩展边界前，相关线边定置先作为可调整提案。充电/换电设施不作为通道预留的一部分自行布置。车型、厂家工况参数、现场测量与适用专项完成后才能确定控制包络和实际尺寸。本确认不解除图签/单位冲突、P02/P05阻塞或制作安装批准关卡。\n')
    OUT.mkdir(parents=True,exist_ok=True);SRC.mkdir(parents=True,exist_ok=True)
    replacements={
        '主物流：按工单和品质结论向下游交接':'主物流：用户确认按此流程深化，按工单及品质结论交接',
        '供料 → 接收 → 下游交接；实际单／双向、转弯及净宽待核':'当前人工周转车；预留未来电动车工况；流向、包络和净宽待核',
        '本轮未确认实际工序顺序。':'用户已确认主流程；具体工单与现场接口待核。',
        '线色沿用V1黄色示例，待现场样色确认':'直线与转弯按人工／未来电动两种工况核定',
        '按满载外廓与取放空间核定车位':'按两种工况核定车位；未来车型与尺寸待定',
        '② 测车辆满载外廓、双向会车及转弯包络':'② 分测人工与未来电动满载外廓、会车及转弯',
        '车辆与货物最大外廓、会车／单向方案、人员分流':'分别核定人工／未来电动工况，兼顾人员分流',
        '实际货梯、工艺顺序、车辆与现场净空待核':'货梯、未来电动车型及两种满载工况的净空待核',
        '实际工序/设备身份待核':'实际工位/设备身份待核',
    }
    for p in (ROOT/'design/v2/ground_logistics_v2.9').rglob('*'):
        if not p.is_file():continue
        target=SRC/p.relative_to(ROOT/'design/v2/ground_logistics_v2.9');target.parent.mkdir(parents=True,exist_ok=True)
        content=p.read_text().replace('V2.9',VERSION).replace('v2.9','v2.9.1').replace('/ 07','/ 08')
        for old,new in replacements.items():content=content.replace(old,new)
        target.write_text(content)
    base.SRC=SRC;base.OUT=OUT;base.REV=REV
    r,t,l,panel,pa=base.rect,base.text,base.lines,base.panel,base.path
    b=panel(40,190,780,180,'已确认｜现在的使用工况',['人工周转车；主流程按用户确认深化','来料交接 → 装配 → 测试／老化 → 包装 → 成品交接','当前仍须实测：车／货／操作者外廓与操作空间'])
    b+=panel(850,190,790,180,'未来考虑｜电动搬运车预留',['选型未定：步行式／站驾式／牵引式等不可混同','先核车型、载荷、转向与厂商适用工况参数','预留是规划要求，不是已具备电动车运行条件'])
    b+=t(40,420,'通道横向关系示意｜人行与物流分开核定，不按此图量尺寸',28,weight=700)
    b+=r(40,454,1600,250,'#D8DADB')
    b+=r(65,480,305,188,'none','#FFFFFF',5)+t(217,560,'独立人行关系',29,weight=700,anchor='middle')+t(217,608,'净宽 / 隔离条件待核',22,anchor='middle')
    b+=r(430,480,1180,188,'none','#3E3A39',3)+t(1020,518,'未来电动车通行包络：选型与现场核定后确定',26,weight=700,anchor='middle')
    b+=r(465,544,665,100,'none','#FFFFFF',6)+t(797,586,'当前人工周转车工况',28,weight=700,anchor='middle')+t(797,625,'车、货与操作者操作范围均需核定',21,anchor='middle')
    b+=t(1370,581,'候选扩展范围',26,weight=700,anchor='middle')+t(1370,623,'尚未定位 / 尺寸待核',21,anchor='middle')
    b+=t(40,746,'定置先避开候选扩展冲突；候选范围核定前，线边框位采用可调整提案。图中比例不表达预留大小。',22)
    b+=panel(40,783,780,240,'联动预留｜不能只看直线路宽',['转弯／交叉：核满载包络、视线和人员候行','交接／停车：核接收面、满位状态与退出方式','货梯／地坪：核门宽、轿厢、载荷及楼层适用条件','人员：复核自然人行路径及交叉／隔离方式'])
    b+=panel(850,783,790,240,'实施分期｜当前放样与未来切换',['当前：核定人工工况后再确认标线与地贴','未来：选定车型后重测并更新定位与运行方案','不默认与现有周转车直接混行或沿用相同车位','充电／换电设施另作专项，不自行放进通道预留'])
    b+=t(40,1060,'定性参考：HSE Traffic routes / Separating pedestrians and vehicles（不作本地法规或尺寸依据）',20)
    new_name=base.page(8,'8F 地面物流规划｜人工使用与电动预留','以当前人工周转车为现状，以未来电动搬运为预留意向；没有选定车型、尺寸或充电点。',b)
    f=SRC/new_name;f.write_text(f.read_text().replace('/ 07','/ 08'))
    manifest.update(revision=REV,supersedes='V2.9-GROUND-LOGISTICS-DRAFT',user_requirements_path=str(EVIDENCE.relative_to(ROOT)),
        confirmed_current_transport='人工周转车',future_transport='电动搬运车（考虑中，需预留，车型未定）',
        confirmed_process=['来料交接','装配','测试／老化','包装','成品交接'],
        confirmation_scope='planning_inputs_only_not_engineering_approval',
        assumptions=['主流程已获用户确认；老化按实际工单适用','当前人工周转车已确认；车辆尺寸待测','未来考虑电动搬运，选型与工况未知','沿用V2.7右上客梯仅作人员接口，货梯身份待核'],
        unresolved=['8F图身/3F图签冲突','CAD物理单位与现场两向校核','原生完整底图与字体依赖','货梯身份与真实交接面','人工车满载实测、未来电动车型与厂家参数','两种工况通道/转弯/交叉/接收/停放包络','现场定位尺寸、材料、数量与人类批准'])
    manifest['pages'].append(new_name)
    paths=[rec['path'] for rec in manifest['source_records']]+[str(EVIDENCE.relative_to(ROOT)),'docs/DECISIONS.md']
    manifest['source_records']=[dict(path=p,sha256=hashlib.sha256((ROOT/p).read_bytes()).hexdigest()) for p in paths]
    for par in manifest['parameters']:
        if par['parameter']=='vehicle_type':par.update(actual_value='人工周转车',evidence=str(EVIDENCE.relative_to(ROOT)),value_status='user_confirmed_not_engineering_approval')
    manifest['parameters'].append(dict(parameter='future_electric_vehicle_model',actual_value=None,evidence=None,unit=None,approval=None))
    manifest['external_references']=[dict(url='https://www.hse.gov.uk/workplacetransport/trafficroutes.htm',scope='qualitative_route_surface_and_junction_review_only'),dict(url='https://www.hse.gov.uk/workplacetransport/separating.htm',scope='qualitative_pedestrian_vehicle_separation_only')]
    base.dump(OUT/'规划与来源.json',manifest)
    for name in copied_files:
        (OUT/name).write_bytes(previous_files[name])
    base.dump(OUT/'用户确认与预留边界.json',json.loads(EVIDENCE.read_text()))
    fields=['项目','当前人工周转车','未来电动搬运车','单位','测量或参数依据','确认角色','状态']
    surveys=[('运输形式','人工周转车','电动搬运车（考虑中，具体形式待定）',''),('车型／厂家／型号','','',''),('车体／货物／操作者最大外廓','','','mm'),('满载总重与地坪／货梯条件','','','kg及适用条件'),('单向／会车／超车与混行规则','','',''),('转弯／交叉／制动与视线条件','','','现场记录'),('线边接收与停车取放包络','','','mm'),('货梯门／轿厢／进出方式','','','mm及适用条件'),('人行净空与隔离方式','','','mm及方案'),('未来充电／换电设施是否需要','','','专项确认'),('最终通道与候选扩展边界','','','经核定坐标与尺寸')]
    with (OUT/'人工与未来电动_双工况核对表.csv').open('w',encoding='utf-8-sig',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=fields);writer.writeheader()
        for a,current,future,unit in surveys:writer.writerow(dict(zip(fields,[a,current,future,unit,'用户确认现状；尺寸及工况另核' if a=='运输形式' else '','','现状/意向已确认；尺寸与批准未定' if a=='运输形式' else '待核'])))
    shutil.copytree(SRC,OUT/'可编辑SVG',dirs_exist_ok=True)
    html=previous_files['打开地面物流方案.html'].decode('utf-8').replace('V2.9',VERSION).replace('7页','8页')
    html=html.replace('图纸身份和单位仍有待核项。','图纸身份和单位仍有待核项。已纳入用户确认：当前人工周转车，未来考虑电动搬运并预留；主流程按确认顺序深化。')
    html=html.replace('</ul></nav>',f'<li><a href="可编辑SVG/{new_name}">{new_name}</a></li></ul><p><a href="人工与未来电动_双工况核对表.csv">人工与未来电动双工况核对表</a></p></nav>')
    html=html.replace('</html>',f'<section><img src="预览/{new_name[:-4]}.png" alt="人工使用与电动预留"></section></html>')
    (OUT/'打开地面物流方案.html').write_text(html)
    readme=previous_files['先读说明.md'].decode('utf-8').replace('V2.9',VERSION).replace('7页','8页')
    readme+='\n## 本次用户确认与更新\n\n当前人工周转车；未来考虑电动搬运车，需要预留。来料交接→装配→测试/老化→包装→成品交接按用户确认深化；老化按各工单实际适用。新增第8页预留关系及双工况CSV。未来电动车型、货梯口、实际尺寸、控制包络、混行规则和是否设充电/换电设施均未确认。当前人工作业与未来电动作业分别核定，不能假定现有车位、路宽或地贴直接通用。\n\n定性参考：[HSE通道](https://www.hse.gov.uk/workplacetransport/trafficroutes.htm)、[HSE人车分流](https://www.hse.gov.uk/workplacetransport/separating.htm)，只辅助考虑表面、交叉和人员分流，不作为本地法规、数值或批准依据。\n'
    (OUT/'先读说明.md').write_text(readme)
    base.dump(OUT/'FM-01_针对性审查.json',dict(revision=REV,decision='Refine',template_code='FM-01',preserve='V2.9 six marking details and eight sticker styles; no orange floor markings',changes=['记录用户确认的人工周转车及主流程','补未来电动考虑与空间预留关系','补两种工况测量口径；不设虚构尺寸或充电点'],source_render='交付_8楼/地面物流规划_V2.9/预览/01_物流关系总图.png',production_release=False))
    print(json.dumps(dict(revision=REV,pages=len(manifest['pages']),output=str(OUT)),ensure_ascii=False))

if __name__=='__main__':main()

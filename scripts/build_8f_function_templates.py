"""Six same-size, editable functional proposals; keep existing source revisions intact."""
from pathlib import Path
import hashlib
import html
import json
import xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'design/v2/point_effects_2026-10-26/templates'
REV='V3.3-FUNCTION-DRAFT'
K='#000000';W='#FFFFFF';O='#FF6600';G='#3E3A39';L='#D8D8D8'
FONT='PingFang SC, Noto Sans CJK SC, Microsoft YaHei, sans-serif'
def esc(s):return html.escape(str(s),quote=True)
def rect(x,y,w,h,fill=W,stroke=None):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{fill}"'+(f' stroke="{stroke}" stroke-width="1"' if stroke else '')+'/>'
def text(x,y,t,size=24,fill=K,weight=400):
    return f'<text x="{x}" y="{y}" font-size="{size}" fill="{fill}" font-weight="{weight}">{esc(t)}</text>'
def rule(x,y,w,fill=L):return rect(x,y,w,1,fill)
def field(x,y,label,w,size=24,value='待填'):
    return text(x,y,label,size,G)+rect(x,y+16,w,62,W,L)+text(x+12,y+59,value,size,G)
def header(w,title,subtitle,right):
    return rect(0,0,w,155,K)+rect(0,0,12,155,O)+text(50,80,title,57,W,700)+text(52,124,subtitle,22,W)+text(w-430,88,right,27,O,600)

def build():
    OUT.mkdir(parents=True,exist_ok=True)
    originals=json.loads((ROOT/'reports/point_effects_2026-10-26/template_inputs.json').read_text())
    arts={};changes={}
    arts['WF-02']=rect(0,0,1200,400,K)+rect(0,0,12,400,O)+text(50,90,'8F',63,O,700)+text(50,151,'楼层 / FLOOR',17,W)+rect(245,48,1,266,G)+text(300,144,'锂电泵装配',79,W,700)+text(304,205,'ELECTRIC PUMP ASSEMBLY',25,W)+rule(304,239,832,O)+text(304,292,'区域ID：待确认',30,W,600)+text(304,337,'名称为基线提案；区域边界与安装面待核',19,W)+text(48,382,'WF-02 / 功能识别草案 · 无实际指向',13,W)
    changes['WF-02']=['保留8F、用途与区域ID三种不同字段；功能标题优先。','缩减品牌占比，固定识别和可换区域信息有清楚分界；不加入未核箭头。']
    arts['WF-04']=rect(0,0,360,1100,W)+rect(0,0,360,245,K)+rect(0,0,9,245,O)+text(33,145,'8F',110,O,700)+text(34,200,'楼层 / FLOOR',18,W)+text(30,340,'锂电泵装配',40,K,700)+text(32,379,'ELECTRIC PUMP ASSEMBLY',12,G)+rule(30,415,300,O)+field(30,476,'区域 / AREA',300,21,'区域待核')+field(30,661,'柱号 / COLUMN',300,21,'P-待填')+text(30,850,'朝向按图纸与现场确认',20,G)+rect(0,954,360,146,K)+text(30,1010,'WF-04 / 位置识别草案',18,W,600)+text(30,1060,'不以区域号替代永久柱号',17,W)
    changes['WF-04']=['区域信息只出现一次，减少重复待核字样。','区域号、永久柱号各设独立可换填写区，保留原有身份与朝向约束。']
    arts['WH-01']=rect(0,0,200,100,W,K)+rect(0,0,200,17,K)+rect(0,0,3,17,O)+text(8,11.5,'库位 / LOCATION',6.2,W,700)+text(8,38,'8F-__-__-__-__',13.8,K,700)+text(8,49,'楼层 / 区 / 排 / 列 / 层',5.2,G)+rule(8,55,134)+text(8,66,'容量 / 载荷：批准后填写',5.2,G)+text(8,77,'物料、批次使用可换卡',5.1,K)+text(8,88,'编码结构示意，非已登记库位',4.2,G)+rect(150,27,42,42,W,G)+text(154,43,'编码待生成',4.5,G)+text(157,54,'非扫码图',4.5,G)+text(150,81,'库位ID一致后',4.2,G)+text(150,90,'再生成并实扫',4.2,G)
    changes['WH-01']=['保留固定库位地址，物料与批次继续使用独立可换卡。','编码区和主地址对齐；不生成示例条码，不把备品或标签库存当安装量。']
    a=rect(0,0,2400,1200,W)+header(2400,'生产运行看板','PRODUCTION CONTROL','8F / 线号待填')
    metrics=[('计划合格产出','锁定计划 / 版次待填'),('实际合格产出','同工序、同时段、同计量单位'),('累计差异','实际 - 计划')]
    for i,(name,note) in enumerate(metrics):
        x=50+i*500;a+=text(x,225,name,32,K,600)+rect(x,250,450,125,W,L)+text(x+18,327,'待填',54,G)+text(x,414,note,21,G)
    a+=field(1600,222,'当前工单 / 产品版本',750,27,'待填 / Rev.待填')+field(1600,366,'班次 / 更新人 / 更新时间',750,27)
    a+=text(50,510,'时段进度',35,K,700)+text(1250,510,'异常接单与下一步',35,K,700)
    def table(x,y,width,headers,rows):
        col=width/len(headers);s=rect(x,y,width,62,K)
        for i,h in enumerate(headers):s+=text(x+i*col+16,y+41,h,24,W,600)
        for r in range(rows):
            top=y+62+r*95;s+=rule(x,top+95,width)
            for i in range(len(headers)):s+=text(x+i*col+16,top+58,'待填',22,G)
        return s
    a+=table(50,540,1100,['时段','计划','实际','差异','原因'],4)+table(1250,540,1100,['事件 / 首次时间','接手人','下一步','预计完成'],3)
    for x,name,note in [(50,'首件 / 换型','批准记录：待填'),(650,'一次通过率','首次通过 / 首检总数：待填'),(1250,'WIP / 批准上限','当前 / 上限 / 单位：待填'),(1850,'安全 / 6S','未闭环问题：待填')]:
        a+=text(x,1080,name,29,K,600)+text(x,1130,note,22,G)
    a+=text(50,1180,'无数据保持待填；差异 = 实际 - 计划；更新延迟须显示原因，不显示假正常。',19,G)
    arts['PM-01']=a
    changes['PM-01']=['保留计划/实际/差异、时段表、异常接单和四项控制字段。','数据框改成可写/可换模块；空值不伪装绩效，异常接手在独立近读区。']
    a=rect(0,0,2400,1200,W)+header(2400,'班组日常管理','SQDCP / DAILY MANAGEMENT','8F / 班组待填')
    cols=[('S','安全','隐患闭环 / 防护点检'),('Q','品质','首次通过 / 缺陷闭环'),('D','交付','锁定计划 / 待交工单'),('C','成本','报废金额 / 返工工时'),('P','人员','关键工位 / 授权覆盖')]
    for i,(letter,title,note) in enumerate(cols):
        x=50+i*470;a+=text(x,245,letter,66,K,700)+text(x+93,235,title,37,K,700)+rule(x,274,425,O)+text(x,318,note,22,G)
        for n,label in enumerate(['口径 / 周期','目标 / 单位','当前 / 趋势','更新人 / 时间']):a+=field(x,375+n*103,label,425,21)
    a+=text(50,853,'跨部门行动清单',36,K,700)+text(1460,850,'风险、责任、期限、验证证据一起闭环',24,G)
    a+=table(50,884,2300,['问题 / 类别','接手人','临时措施','到期 / 下一步','验证证据 / 状态'],2)
    a+=text(50,1178,'阈值经批准后使用颜色提示；报废金额与返工工时分列；个人评价不朝向访客。',19,G)
    arts['PM-02']=a
    changes['PM-02']=['保留SQDCP五项口径/目标/当前/更新和跨部门行动字段。','数据卡与行动卡采用统一可换框，保留成本口径和隐私边界。']
    a=rect(0,0,600,450,W,K)+rect(0,0,600,85,K)+rect(0,0,5,85,O)+text(24,40,'在制品限量',29,W,700)+text(24,67,'WIP LIMIT / FIFO',12,W)+text(390,40,'8F / 工序待核',15,O,600)+text(390,65,'工序关系待核',11,W)
    a+=field(24,121,'当前占用',260,16)+field(316,121,'批准上限',260,16,'待批准')+text(24,220,'计量单位：待核（车 / 箱 / 件分开记录）',13,G)
    a+=text(24,257,'每容器标准数量：待填',14,K)+text(316,257,'批准依据 / 版次：待填',13,K)+text(24,286,'允许物料 / 版本：待填',14,K)+text(316,286,'更新人 / 时间：待填',13,K)
    a+=rect(24,311,552,80,K)+text(38,343,'满位：停止继续投放，通知班组长',20,W,700)+text(38,374,'取料：按已放行批次与先后顺序执行',14,W)+text(24,418,'冻结品退出正常FIFO；未批准上限不作为增加暂存许可。',10,G)+text(24,440,'FL-01 / 上限、容器与现场容量共同复核',10,G)
    arts['FL-01']=a
    changes['FL-01']=['保留批准上限、容器、单位、允许版本、依据、更新与满位动作。','两个大数据框与黑底动作区分开，状态控制不靠橙色或假容量。']
    records=[]
    for row in originals:
        code=row['code'];w,h=row['size'];src=ROOT/row['path'];codepath=OUT/(code+'_'+REV+'.svg')
        meta={'code':code,'revision':REV,'status':'proposal_pending_review','production_release':False,'physical_size_mm':[w,h],'dimension_scope':'Existing nominal template size retained; site/installation dimensions unknown.','source_path':row['path'],'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'original_text_preserved_in_metadata':row['texts'],'decision':'Refine','changes':changes[code],'external_reference_status':'Initial layouts preceded Xiaohongshu login; subsequently reviewed against 3 observed Xiaohongshu posts and 4 supplementary primary sources. See reference ledger.','reference_ledger':'reports/point_effects_2026-10-26/reference_records.json','quantity_installed':None,'installation_height_mm':None,'approvals':{'content':None,'location':None,'installation':None},'font_files_distributed':False,'path':str(codepath.relative_to(ROOT))}
        svg=f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}mm" height="{h}mm" viewBox="0 0 {w} {h}" role="img"><title>{esc(code+" 功能优化草案")}</title><desc>名义模板，实际内容位置和制作安装待核。</desc><metadata>{esc(json.dumps(meta,ensure_ascii=False))}</metadata><g font-family="{FONT}" style="font-variant-numeric:tabular-nums">{arts[code]}</g></svg>'
        codepath.write_text(svg);codepath.with_suffix('.meta.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2)+'\n');ET.parse(codepath);records.append(meta)
    (OUT/'manifest.json').write_text(json.dumps({'revision':REV,'status':'draft','production_release':False,'templates':records},ensure_ascii=False,indent=2)+'\n')
    print('Generated six same-size functional proposals; existing SVGs and template registry unchanged.')

if __name__=='__main__':build()

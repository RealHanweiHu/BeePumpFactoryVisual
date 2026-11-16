"""Document the reviewed design adaptations and generate SVG before/after navigation."""
from pathlib import Path
import html
import json
import os
from build_8f_point_gallery import FOCUS

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'design/v2/point_effects_2026-10-26'
REPORT=ROOT/'reports/point_effects_2026-10-26'
def read(p): return json.loads(p.read_text())
def esc(s): return html.escape(str(s),quote=True)

def main():
    specs=read(BASE/'prompts.json')['prompts']
    refs=read(REPORT/'reference_records.json')
    templates=read(BASE/'templates/manifest.json')['templates']
    assets=read(BASE/'manifest.json')['assets']
    doc='''# 8F逐项视觉优化说明

版本：8F-POINT-EFFECTS-2026-10-26-DRAFT。方案评审草案，未制作安装放行。

[打开逐项效果图库](../交付_8楼/逐点效果与功能优化_2026-10-26/打开这里.html) · [六款模板前后对照](../reports/point_effects_2026-10-26/templates_compare.html) · [逐图清单与哈希](../design/v2/point_effects_2026-10-26/manifest.json)

本轮把21项已有功能需求逐项表达，并补充用户指定的老化/充电管理条件项。22个预览场景不等于22个实物安装点；同一功能可以对应多个真实点位，踏勘后另建point_id。图中建筑、设备、道具和数量为生成示意，不能当成本厂照片或CAD还原。

## 六处优先看的方案

| 场景 | 主识别与近读内容 | 阅读后动作 | 本轮采用 | 现场收口 |
|---|---|---|---|---|
| D14 维修台 | 上方维修身份；工具定置与任务卡；对象对应的品质卡 | 对工具归位、接手维修和复检；不良/冻结由品质规则另控 | 工具轮廓与实际工具相配，普通进度采用中性样式，待判/维修中/待复检不借用品质色 | 真实工具清单、普通返修边界、复检交接、固定面 |
| D04 流水线头 | 生产运行标题；计划/实际/差异；工单版次；异常接手 | 同口径更新产出，异常有接手和下一步 | PM-01改可写/可换模块；空值留待填，异常不藏在装饰图表中 | 时段/单位/计划锁定口径、数据责任、驻足与通行关系 |
| D02 装配区 | 远读区域吊牌；近读区域/柱号、受控作业文件和线边地址 | 到对区域、读对版本、按已核进入条件作业 | WF-02与WF-04建立阅读层级，楼层/区域/永久柱号分开 | 实际区域名、边界、柱号、视线、安装面和适用工位 |
| D11 测试区 | 测试任务/受控项目、记录、结论；品质放行另位 | 对应工单执行受控测试，结果与放行分开记录 | 只表达外侧管理，图中设备保持概括示意 | 机型适用、真实设备与项目、工艺和专业条件 |
| U01 老化/充电管理 | 工单、项目、开始/结束、接手；品质放行独立 | 先核工艺和设施，再用真实受控任务卡管理 | 新增外侧信息管理概念，标明设施与工艺待核；不据图确定接线、电源、温度或时长 | 设备/工艺/电气/环境/消防条件及批准依据；按实际工单适用 |
| D06 物料超市 | 大功能名；固定库位；可换物料/批次卡；补料卡回收位 | 按地址取放，信号回收后按已核规则补料 | WH-01地址独立、扫码位先留待生成；不把物料名写死在固定地址牌 | 实物地址、容器、上限、补料触发、物流接手 |

## 参考案例怎样转化

小红书由用户授权只读访问并自行完成扫码登录。实际查看3篇正文及注明的图片，不以搜索缩略图、点赞量或作者说法证明管理效果。链接可能要求登录。

'''
    for r in refs['sources']:
        doc+=f"- [{r['title']}]({r['url']})"+(f"（{r['author']}）" if r.get('author') else '')+f"：{r['application']}\n"
    doc+='''
小红书实际浏览范围：入口案例图1/4；库区货架案例图1/3、2/3；安装现场案例图1/5。正文和图片中可见的版式与空间关系已分别记录在[来源台账](../reports/point_effects_2026-10-26/reference_records.json)。未复制案例图片、他厂品牌、编码、尺寸、安全图形或承载参数。其余四项为独立的补充一手资料。

六款SVG的初稿与部分图片在登录前依据项目规则和补充资料制作，登录后再与实际案例逐项核对；每张图片的提示词和元数据区分是否在生成时加入小红书文字参考，不追溯虚构创作来源。

## 保留与调整

- 保留黑白橙品牌、8F楼层身份、既有模板代码、源文件原文和来源哈希。橙色只用于牌面品牌层；地面维持灰底黄边物流、白色人行及普通定置的当前提案。
- 保留蓝待检、绿放行、红不合格、黄冻结的品质语义；卡上继续有对象/范围/签发及相应动作。操作进度、设备许可和品质放行分别表达。
- 将固定身份与频繁变化的信息分开；字大的是功能，近读卡说明对象、版本、记录或下一步。工具影形须按真实工具，不能照概念图采购工具。
- 新SVG保留原名义尺寸；实际制作尺寸、高度、安装位置、数量、材质/固定和审批均未知。六款新增稿不覆盖既有A/B/C选择，不修改模板注册表。

## 六款可编辑模板

| 模板 | 本轮调整 | 新稿 |
|---|---|---|
'''
    for r in templates:
        doc+=f"| {r['code']} | {' '.join(r['changes'])} | [SVG](../{r['path']}) |\n"
    doc+='''
原SVG完整保留，新稿元数据保存原文及来源哈希。图片只评审场景关系，印刷文字与控制规则以可编辑SVG和受控文本为准。生成图中文字、设备轮廓不作为生产文件。

## 全部功能覆盖

| 预览 | 场景 | 拟优化 | 待核 |
|---|---|---|---|
'''
    for s in specs:
        change,pending=FOCUS[s['key']]
        doc+=f"| [{s['key']}](../交付_8楼/逐点效果与功能优化_2026-10-26/打开这里.html#{s['id']}) | {s['title']} | {change} | {pending} |\n"
    doc+=f'''
当前保存{len(assets)}张独立生成图；完整提示词、原始生成文件路径、分辨率与SHA-256在manifest及逐图meta内。项目输入、CAD、文档和参考图片未上传。

## 下一步与未放行事项

先按图库评审各处功能与文字，沿用原V2.8选型页导出真实偏好。然后在同次现场核对真实安装面、朝向、尺寸/高度、遮挡、固定、材料及实际数量。与安全或专业设施相关的条件项须对应角色复核；本轮不添加批准或签名。

底图图身“八层”/图签“三层”的身份冲突、单位与两向校准仍未闭合，P02/P05继续阻塞真实坐标及可核量点位。D15/D18/D20尚未定位。未勘测的点位数组保持空，不解释为零需求。
'''
    (ROOT/'docs/8F_逐项视觉优化说明.md').write_text(doc)
    pairs=[]
    for r in templates:
        figures=[]
        for kind,label,p in [('before','原稿',r['source_path']),('after','功能优化草案',r['path'])]:
            img='template_render/'+r['code']+'_'+kind+'.png'
            href=os.path.relpath(ROOT/p,REPORT)
            figures.append(f'<figure><figcaption>{label} · <a href="{esc(href)}">打开SVG</a></figcaption><a href="{esc(img)}"><img src="{esc(img)}" alt="{esc(r["code"]+label)}"></a></figure>')
        pairs.append(f'<section><h2>{r["code"]}</h2><p>{esc(" ".join(r["changes"]))}</p><div class="pair">'+''.join(figures)+'</div></section>')
    page='''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>8F六款功能模板前后对照</title><style>body{font:16px/1.7 system-ui,"PingFang SC",sans-serif;color:#3E3A39;margin:0}main{max-width:1500px;padding:30px;margin:auto}h1,h2{color:#000}a{color:inherit}section{border-top:1px solid #aaa;margin-top:35px;padding-top:20px}.pair{display:grid;grid-template-columns:1fr 1fr;gap:20px}figure{margin:0;min-width:0}img{display:block;width:100%;height:550px;object-fit:contain;border:1px solid #ddd;background:#fff}figcaption{padding:12px 0}@media(max-width:700px){main{padding:20px 15px}.pair{grid-template-columns:1fr}img{height:auto;max-height:750px}}a:focus-visible{outline:3px solid #FF6600}</style></head><body><main><p><a href="../../交付_8楼/逐点效果与功能优化_2026-10-26/打开这里.html">← 返回逐项效果图</a></p><h1>六款核心模板 · 前后对照</h1><p>V3.3-FUNCTION-DRAFT。旧稿保留；新稿仅为功能与版式提案，名义尺寸沿用原模板，真实安装/制作尺寸、数量与批准未核。下列为本地librsvg实际渲染，点击打开PNG或SVG。</p>__PAIRS__<footer>未经制作安装确认。原文与来源哈希保留在各新稿的metadata和meta.json内。</footer></main></body></html>'''.replace('__PAIRS__',''.join(pairs))
    (REPORT/'templates_compare.html').write_text(page)
    print('Documented 22 concepts and six template comparisons.')

if __name__=='__main__':main()

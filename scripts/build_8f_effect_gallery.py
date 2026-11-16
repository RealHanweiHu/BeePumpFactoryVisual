#!/usr/bin/env python3
"""Publish locally saved concept renders into a local review gallery."""
from pathlib import Path
import html
import json
import os

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT/'design/v2/effect_previews_2026-10-26'
OUT = ROOT/'交付_8楼/效果预览_2026-10-26'

def main():
    manifest = json.loads((SOURCE/'manifest.json').read_text())
    OUT.mkdir(parents=True, exist_ok=True)
    esc=lambda s: html.escape(str(s), quote=True)
    sections=[]
    for row in manifest['assets']:
        image=ROOT/row['path']
        if not image.is_file():raise ValueError('Missing preview: '+row['path'])
        src=os.path.relpath(image, OUT)
        notes=''.join('<li>'+esc(s)+'</li>' for s in row['review_focus'])
        sections.append(f'''<section id="{esc(row['id'])}"><p class="number">{esc(row['id'])} / 概念评审</p><h2>{esc(row['title'])}</h2><p>{esc(row['caption'])}</p><figure><a href="{esc(src)}"><img src="{esc(src)}" alt="{esc(row['title'])}，空间与设备为示意" width="{row['width_px']}" height="{row['height_px']}"></a><figcaption>AI生成的局部概念场景，图片内空间、设备、数量及安装条件为示意。<a href="{esc(src)}" download>保存原图</a></figcaption></figure><ul>{notes}</ul></section>''')
    metadata=json.dumps({'revision':manifest['revision'],'status':'draft_concept_preview','production_release':False,'source_manifest':'design/v2/effect_previews_2026-10-26/manifest.json'},ensure_ascii=False).replace('<','\\u003c')
    page='''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>BeePump｜8楼概念效果预览</title><style>*{box-sizing:border-box}body{margin:0;color:#3E3A39;background:#fff;font:17px/1.75 system-ui,-apple-system,"PingFang SC",sans-serif}main{max-width:1400px;margin:auto;padding:28px 32px 60px}header{border-bottom:2px solid #000;padding-bottom:25px}h1,h2{color:#000;line-height:1.35}h1{font-size:36px;margin:14px 0}h2{font-size:28px;margin:6px 0}.number{font-size:13px;font-weight:700;letter-spacing:.08em}a{color:inherit;text-underline-offset:4px}a:focus-visible{outline:3px solid #FF6600;outline-offset:4px}.note{border-left:4px solid #FF6600;background:#f5f5f5;padding:14px 18px}nav{display:flex;gap:22px;flex-wrap:wrap;margin-top:22px}section{margin-top:40px;padding-top:26px;border-top:1px solid #ccc}figure{margin:20px 0}img{display:block;width:100%;height:auto;background:#eee}figcaption,footer{font-size:13px}figcaption{padding-top:8px}ul{padding-left:22px}footer{border-top:2px solid #000;padding-top:18px;margin-top:36px}@media(max-width:700px){main{padding:20px 16px 40px}h1{font-size:28px}h2{font-size:24px}nav{gap:12px 20px}}@media print{main{padding:0}section{break-before:page}img{max-height:75vh;object-fit:contain}nav{display:none}}</style><script type="application/json" id="artifact-metadata">__META__</script></head><body><main><header><p><a href="../打开这里.html">← 返回8楼当前方案</a></p><p class="number">BEEPUMP · 8F · 2026-10-26</p><h1>8楼概念效果预览</h1><p>看现有黑橙品牌、物理牌面和地面配色进入空间后的观感。</p><p class="note">三张为文字方案生成的局部概念场景，不是本厂实景或CAD还原。黑橙按既有基线示意，不代表A/B/C最终选型；真实墙体、设备布置、尺寸、数量、材料与安装面仍待现场确认。</p><nav aria-label="效果图"><a href="#E01">装配作业区</a><a href="#E02">地面物流与定置</a><a href="#E03">访客到层导览</a></nav></header>__SECTIONS__<footer>8F-EFFECT-PREVIEW-2026-10-26-DRAFT · 未经制作安装确认。原始图纸未上传；使用内置image_gen，三份完整提示词及元数据保存在项目内。<br><a href="../../design/v2/effect_previews_2026-10-26/prompts.json">完整提示词</a> · <a href="../../design/v2/effect_previews_2026-10-26/manifest.json">来源与文件清单</a> · <a href="../../reports/effect_previews_2026-10-26/交付记录.md">检查与限制</a></footer></main></body></html>'''
    page=page.replace('__META__',metadata).replace('__SECTIONS__',''.join(sections))
    (OUT/'打开效果预览.html').write_text(page)
    print(OUT/'打开效果预览.html')

if __name__=='__main__':main()

#!/usr/bin/env python3
"""Optional QA: requires Playwright and an existing Chromium browser.
Uses set_content only; no server, uploads, system installs, or external assets.
Run after scripts/project.py build-preview.
"""
from pathlib import Path
import json, os, shutil

from playwright.sync_api import sync_playwright
r=Path(__file__).resolve().parents[1]
shots=r/'reports/preview_checks';shots.mkdir(exist_ok=True)
checks=[]

with sync_playwright() as p:
 b=p.chromium.launch(executable_path=os.environ.get('CHROMIUM_EXECUTABLE') or shutil.which('chromium') or shutil.which('google-chrome'),headless=True,args=['--no-sandbox'])
 for filename in ['index.html','single_file_review.html']:
  page=b.new_page(viewport={'width':1440,'height':1050}, device_scale_factor=1)
  errors=[];external=[]
  page.on('pageerror',lambda err:errors.append(str(err)))
  page.on('request',lambda req:external.append(req.url) if req.url.startswith(('http:','https:')) else None)
  content=(r/'preview'/filename).read_text()
  if filename=='index.html':
   content=content.replace('<link rel="stylesheet" href="style.css">','<style>'+(r/'preview/style.css').read_text()+'</style>')
   content=content.replace('<script src="data.js"></script>','<script>'+(r/'preview/data.js').read_text()+'</script>')
   content=content.replace('<script src="app.js"></script>','<script>'+(r/'preview/app.js').read_text()+'</script>')
  page.set_content(content,wait_until='load');page.screenshot(path=str(shots/(filename+'.overview.png')),full_page=True)
  assert page.locator('.template-tile').count()==6
  page.locator('nav [data-view="templates"]').click()
  assert page.locator('.template-tile').count()==36
  page.locator('#search').fill('WF-02')
  assert page.locator('.template-tile').count()==1
  page.locator('[data-template="WF-02"]').click();assert page.locator('dialog[open]').count()==1
  assert page.locator('#dialog-title').is_visible()
  page.screenshot(path=str(shots/(filename+'.dialog.png')),full_page=False)
  page.keyboard.press('Escape');assert page.locator('dialog[open]').count()==0
  page.locator('#search').fill('unknownunlikelycode');assert page.locator('.empty-results').count()==1
  page.get_by_role('button',name='清除筛选').click();assert page.locator('.template-tile').count()==36
  page.locator('#category').select_option('导视');assert page.locator('.template-tile').count()==5
  page.get_by_role('button',name='楼层与图纸').click();page.locator('[data-floor="3F"]').click()
  assert page.locator('.bigfloor').inner_text()=='3F';assert page.locator('.empty-plan').is_visible()
  page.get_by_role('button',name='执行任务',exact=True).click();assert page.locator('.task-row').count()==10
  page.get_by_role('button',name='点位与工程量',exact=True).click();assert page.get_by_role('heading',name='尚未布点，不生成零工程量。').is_visible()
  assert page.evaluate('document.documentElement.scrollWidth <= window.innerWidth')
  page.set_viewport_size({'width':390,'height':844});page.get_by_role('button',name='项目总览',exact=True).click()
  page.screenshot(path=str(shots/(filename+'.mobile.png')),full_page=True)
  assert page.evaluate('document.documentElement.scrollWidth <= window.innerWidth')
  page.locator('nav [data-view="templates"]').click();page.locator('#search').fill('WF-02');page.locator('[data-template="WF-02"]').click()
  assert page.locator('dialog[open]').is_visible();assert page.evaluate('document.documentElement.scrollWidth <= window.innerWidth')
  page.get_by_role('button',name='关闭模板详情').click()
  checks.append({'page':filename,'desktop':'pass','mobile':'pass','tabs_search_filter_dialog':'pass','page_errors':errors,'external_requests':external})
  assert not errors,errors
  assert not external,external
  page.close()
 b.close()
(r/'reports/preview_qa.json').write_text(json.dumps({'engine':'local Chromium / Playwright set_content (file:// and loopback navigation blocked by environment policy)' ,'checks':checks,'scope':'Starter UI only; does not validate site drawing or V2 artwork.'},ensure_ascii=False,indent=2))
print(json.dumps(checks,ensure_ascii=False,indent=2))

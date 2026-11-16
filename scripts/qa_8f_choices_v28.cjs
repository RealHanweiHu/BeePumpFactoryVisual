const fs=require('fs'),path=require('path'),assert=require('assert');
const {chromium}=require('/Users/huhanwei/.npm/_npx/31e32ef8478fbf80/node_modules/playwright');
const root=path.resolve(__dirname,'..'),out=path.join(root,'交付_8楼/多方案选择_V2.8'),reportDir=path.join(root,'reports/options_v2.8');
const origin='http://beepump.local.review';
const manifest=JSON.parse(fs.readFileSync(path.join(root,'design/v2/options_v2.8/style_manifest.json'),'utf8'));
const cat=JSON.parse(fs.readFileSync(path.join(out,'方案目录.json'),'utf8'));
const cleanSvg=s=>s.replace(/<\?xml[^>]*>/,'');
let browser;
(async()=>{
 fs.mkdirSync(path.join(reportDir,'style_render'),{recursive:true});fs.mkdirSync(path.join(out,'逐项对比图'),{recursive:true});fs.mkdirSync(path.join(out,'output/pdf'),{recursive:true});
 browser=await chromium.launch({headless:true,executablePath:'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',args:['--disable-background-networking']});
 const context=await browser.newContext({viewport:{width:1560,height:1120},deviceScaleFactor:1});
 const report={revision:cat.revision,external_requests:[],page_errors:[],style_artboards:[],checks:[],sheet_layout:[]};
 const localRoute=async route=>{
  const u=new URL(route.request().url());
  if(u.protocol==='data:'||u.protocol==='about:')return route.continue();
  if(u.origin!==origin){report.external_requests.push(u.href);return route.abort();}
  const local=path.resolve(root,'交付_8楼',decodeURIComponent(u.pathname).replace(/^\//,''));
  if(!local.startsWith(path.join(root,'交付_8楼')+path.sep)||!fs.existsSync(local))return route.fulfill({status:404,body:'not found'});
  const types={'.html':'text/html; charset=utf-8','.svg':'image/svg+xml','.png':'image/png','.json':'application/json'};
  await route.fulfill({status:200,contentType:types[path.extname(local)]||'application/octet-stream',body:fs.readFileSync(local)});
 };
 await context.route('**/*',localRoute);
 const p=await context.newPage();p.on('pageerror',e=>report.page_errors.push(String(e)));
 const grouped=new Map();
 const reuseStyles=process.argv.includes('--ui-only')&&fs.existsSync(path.join(reportDir,'style_layout.json'));
 if(reuseStyles)report.style_artboards=JSON.parse(fs.readFileSync(path.join(reportDir,'style_layout.json'),'utf8'));
 for(const v of reuseStyles?[]:manifest.variants){
  const svg=cleanSvg(fs.readFileSync(path.join(root,v.path),'utf8'));
  await p.setContent('<style>body{margin:0;background:white}svg{display:block;width:1500px;height:1000px}</style>'+svg);
  await p.evaluate(()=>document.fonts.ready);
  const bounds=await p.evaluate(()=>{const s=document.querySelector('svg'),v=s.viewBox.baseVal;return [...s.querySelectorAll('text')].flatMap(t=>{const b=t.getBBox();return b.x<-.1||b.y<-.1||b.x+b.width>v.width+.1||b.y+b.height>v.height+.1?[{text:t.textContent,bbox:[b.x,b.y,b.width,b.height]}]:[];});});
  const shot=path.join(reportDir,'style_render',v.code+'_'+v.style_id+'.png');
  await p.screenshot({path:shot});report.style_artboards.push({code:v.code,style_id:v.style_id,text_outside_canvas:bounds});
  const k=path.basename(v.source_path);if(!grouped.has(k))grouped.set(k,[]);grouped.get(k).push({...v,svg});
 }
 const groups=[...grouped.values()];
 for(let i=0;i<groups.length;i+=2){
  const cards=groups.slice(i,i+2).flatMap(g=>g.sort((a,b)=>a.style_id.localeCompare(b.style_id)));
  await p.setViewportSize({width:1560,height:1140});await p.setContent('<style>body{margin:0;font-family:PingFang SC,Arial}.grid{display:grid;grid-template-columns:repeat(3,1fr);gap:10px}.card{height:555px;border:1px solid #ccc;padding:10px}h2{font-size:23px;margin:0}svg{width:100%;height:505px}</style><div class="grid">'+cards.map(v=>'<div class="card"><h2>'+v.code+' / '+v.style_id+'</h2>'+v.svg+'</div>').join('')+'</div>');
  await p.evaluate(()=>document.fonts.ready);await p.screenshot({path:path.join(reportDir,'style_render','contact-'+String(i/2+1)+'.png'),fullPage:true});
 }
 const url=origin+'/多方案选择_V2.8/START_HERE.html';
 fs.writeFileSync(path.join(reportDir,'style_layout.json'),JSON.stringify(report.style_artboards,null,2));
 console.log('Opening local choice page');
 await p.goto(url);await p.evaluate(()=>{const imgs=[...document.images].filter(i=>i.getAttribute('src'));for(const i of imgs)i.loading='eager';return Promise.race([Promise.all(imgs.map(i=>i.complete?Promise.resolve():new Promise(r=>{i.onload=r;i.onerror=r;}))),new Promise(r=>setTimeout(r,15000))]);});
 console.log('Checking image readiness');
 assert.equal(await p.locator('.req').count(),21);assert.equal(await p.locator('.style-card').count(),63);assert.equal(await p.locator('.location-card').count(),63);assert.equal(await p.locator('input[type=radio]:checked').count(),0);
 assert.deepEqual(await p.evaluate(()=>[...document.images].filter(i=>i.getAttribute('src')&&(!i.complete||!i.naturalWidth)).map(i=>i.src)),[]);report.checks.push('21 requirements / 63 style groups / 63 placement options / no default choice / all images loaded');
 for(const r of cat.requirements){const s=p.locator('[data-req="'+r.requirement_id+'"]');await s.locator('input[data-kind=style][value=B]').check();await s.locator('input[data-kind=placement][value=P2]').check();}
 await p.locator('#note-D01').fill('测试备注：B + P2');assert.equal(await p.locator('input:checked').count(),42);assert((await p.locator('#progress').innerText()).includes('21 / 21'));
 await p.reload();assert.equal(await p.locator('input:checked').count(),42);assert.equal(await p.locator('#note-D01').inputValue(),'测试备注：B + P2');report.checks.push('independent choices and notes retained on reload');
 console.log('Choice persistence passed');
 let [download]=await Promise.all([p.waitForEvent('download'),p.locator('#export-json').click()]);const exportPath=path.join(reportDir,'test_selection.json');await download.saveAs(exportPath);const exported=JSON.parse(fs.readFileSync(exportPath,'utf8'));assert.equal(exported.choices.length,21);assert(exported.choices.every(r=>r.style==='B'&&r.placement==='P2'));assert.strictEqual(exported.production_release,false);
 [download]=await Promise.all([p.waitForEvent('download'),p.locator('#export-csv').click()]);await download.saveAs(path.join(reportDir,'test_selection.csv'));report.checks.push('JSON and CSV export contain all 21 preferences, without release');
 await p.locator('#import-file').setInputFiles(path.join(out,'空白选择清单.json'));await p.waitForFunction(()=>document.querySelectorAll('input[type=radio]:checked').length===0);
 await p.locator('#import-file').setInputFiles(exportPath);await p.waitForFunction(()=>document.querySelectorAll('input[type=radio]:checked').length===42);report.checks.push('blank and saved choices import correctly');
 const wrong={...exported,catalogue_sha256:'wrong'};const wrongPath=path.join(reportDir,'wrong_catalogue.json');fs.writeFileSync(wrongPath,JSON.stringify(wrong));await p.locator('#import-file').setInputFiles(wrongPath);await p.waitForFunction(()=>document.querySelector('#notice').textContent.includes('导入失败'));assert.equal(await p.locator('input[type=radio]:checked').count(),42);report.checks.push('mismatched catalogue import rejected without replacing choices');
 await p.evaluate(()=>localStorage.setItem('beepump-8f-options-v28',JSON.stringify({catalogue_sha256:'old',choices:{}})));await p.reload();assert.equal(await p.locator('input[type=radio]:checked').count(),0);assert((await p.locator('#notice').innerText()).includes('旧选择没有自动套用'));report.checks.push('changed catalogue does not silently reuse old local choices');
 await p.locator('#search').fill('D10');assert.equal(await p.locator('.req:visible').count(),1);await p.locator('#search').fill('');await p.locator('#group').selectOption('UNLOCATED');assert.equal(await p.locator('.req:visible').count(),3);await p.locator('#group').selectOption('');report.checks.push('search and unlocated filter');
 await p.locator('[data-req="REQ-8F-01"] [data-zoom]').first().click();assert(await p.locator('dialog[open]').isVisible());await p.keyboard.press('Escape');assert.equal(await p.locator('dialog[open]').count(),0);
 await p.evaluate(()=>window.scrollTo(0,0));await p.screenshot({path:path.join(reportDir,'desktop.png')});await p.setViewportSize({width:390,height:844});assert(await p.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));await p.screenshot({path:path.join(reportDir,'mobile.png')});report.checks.push('image zoom / Escape / mobile no horizontal overflow');
 const printPage=await browser.newPage({viewport:{width:1560,height:1120},deviceScaleFactor:2});await printPage.route('**/*',localRoute);
 await printPage.goto(origin+'/多方案选择_V2.8/print_book.html');await printPage.evaluate(()=>document.fonts.ready);await printPage.evaluate(()=>Promise.all([...document.images].map(i=>i.complete?Promise.resolve():new Promise(r=>{i.onload=r;i.onerror=r;}))));assert.equal(await printPage.locator('.sheet').count(),23);
 console.log('Rendering 23 print sheets');
 for(let i=0;i<23;i++){
  const sheet=printPage.locator('.sheet').nth(i);const layout=await sheet.evaluate(s=>{const box=s.getBoundingClientRect(),footer=s.querySelector('footer').getBoundingClientRect();const paper=s.querySelector('.paper-choice');return {scroll_height:s.scrollHeight,client_height:s.clientHeight,paper_bottom:paper?paper.getBoundingClientRect().bottom-box.y:null,footer_top:footer.top-box.y};});report.sheet_layout.push({page:i+1,...layout});
  const filename=i<2?'cover-'+String(i+1)+'.png':cat.requirements[i-2].detail_id+'.png';await sheet.screenshot({path:path.join(out,'逐项对比图',filename)});
 }
 await printPage.close();report.checks.push('23 comparison sheets rendered at 2x for local PDF assembly');
 report.passed=report.external_requests.length===0&&report.page_errors.length===0&&report.style_artboards.every(a=>a.text_outside_canvas.length===0)&&report.sheet_layout.every(s=>s.scroll_height<=s.client_height+1&&(!s.paper_bottom||s.paper_bottom<s.footer_top));
 fs.writeFileSync(path.join(reportDir,'browser_qa.json'),JSON.stringify(report,null,2));console.log(JSON.stringify({passed:report.passed,style_count:report.style_artboards.length,checks:report.checks,outside:report.style_artboards.filter(a=>a.text_outside_canvas.length),sheet_overflow:report.sheet_layout.filter(s=>s.scroll_height>s.client_height+1||s.paper_bottom>s.footer_top),external_requests:report.external_requests,page_errors:report.page_errors},null,2));
 await browser.close();if(!report.passed)process.exitCode=1;
})().catch(async e=>{console.error(e);if(browser)await browser.close();process.exitCode=1});

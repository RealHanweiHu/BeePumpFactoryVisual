const fs=require('fs');const path=require('path');
const root=path.resolve(__dirname,'..');
// Existing npm-cached Playwright and installed Chrome; no package download or installation.
const {chromium}=require('/Users/huhanwei/.npm/_npx/31e32ef8478fbf80/node_modules/playwright');
(async()=>{
 const out=path.join(root,'reports/v2_render');fs.mkdirSync(out,{recursive:true});fs.mkdirSync(path.join(root,'output/pdf'),{recursive:true});
 const result={browser:'Installed Google Chrome, cached Playwright',externalRequests:[],pageErrors:[],artboards:[],preview:{},pdf:{}};
 const b=await chromium.launch({headless:true,executablePath:'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',args:['--disable-background-networking']});
 const p=await b.newPage({viewport:{width:1440,height:1050}});
 p.on('pageerror',e=>result.pageErrors.push(String(e)));
 await p.route(/^https?:/,route=>{result.externalRequests.push(route.request().url());route.abort()});
 const manifest=JSON.parse(fs.readFileSync(path.join(root,'design/v2/revision_manifest.json')));
 for(const m of manifest){
  const svg=fs.readFileSync(path.join(root,m.path),'utf8');
  await p.setContent('<html lang="zh-CN"><meta charset="utf-8"><style>body{margin:24px;background:#e9e9e9}svg{display:block;max-width:1360px;width:auto;max-height:1050px;height:auto;margin:auto;background:white}</style>'+svg+'</html>');
  await p.evaluate(()=>document.fonts.ready);
  const check=await p.evaluate(()=>{
   const s=document.querySelector('svg'),v=s.viewBox.baseVal;
   return {fontAvailable:document.fonts.check('16px "PingFang SC"'),sizeMM:[s.getAttribute('width'),s.getAttribute('height')],textChecks:[...s.querySelectorAll('text')].map(t=>{let r=t.getBBox(),c=getComputedStyle(t);let ctx=document.createElement('canvas').getContext('2d');const em=Number(t.getAttribute('font-size'));ctx.font=c.fontStyle+' '+c.fontWeight+' '+em+'px '+c.fontFamily;const ink=ctx.measureText(t.textContent);return {text:t.textContent,nominalEmMM:em,inkHeightMM:ink.actualBoundingBoxAscent+ink.actualBoundingBoxDescent,inkMeasurementMethod:'Canvas font explicitly set to SVG user-unit em; installed font only, not printed physical approval',bbox:{x:r.x,y:r.y,w:r.width,h:r.height},inside:r.x>=-0.1&&r.y>=-0.1&&r.x+r.width<=v.width+0.1&&r.y+r.height<=v.height+0.1}})};
  });
  await p.locator('svg').screenshot({path:path.join(out,m.code+'.png')});
  result.artboards.push({code:m.code,...check});
 }
 const candidate=fs.readFileSync(path.join(root,'outputs/drawings/8F_source_candidate_partial.svg'),'utf8');
 await p.setContent('<style>body{margin:0}svg{width:1400px;height:auto;display:block}</style>'+candidate,{waitUntil:'domcontentloaded'});
 try {await p.locator('svg').screenshot({path:path.join(out,'8F_partial_source.png'),timeout:55000});} catch(e) {result.sourcePreviewScreenshotWarning=String(e);}
 await p.goto('file://'+path.join(root,'START_HERE.html'));
 await p.screenshot({path:path.join(out,'desktop_overview.png')});
 const selected=[];
 for(const m of manifest){
  await p.locator('[data-code="'+m.code+'"]').click();
  const images=p.locator('#comparison img');
  if(await images.count()!==2)throw new Error('Comparison missing for '+m.code);
  if(await p.locator('[data-code="'+m.code+'"]').getAttribute('aria-pressed')!=='true')throw new Error('Selected state missing');
  selected.push(m.code);
 }
 await p.locator('[data-code="WF-02"]').click();await p.locator('#comparison img').nth(1).click();
 result.preview.modalOpened=await p.locator('#zoom').evaluate(e=>e.open);await p.locator('#zoom .close').click();
 result.preview.modalClosed=!(await p.locator('#zoom').evaluate(e=>e.open));
 await p.locator('[data-row="0"][data-field="qty"]').fill('2');await p.locator('[data-row="0"][data-field="price"]').fill('100');await p.locator('[data-row="0"][data-field="install"]').fill('20');
 result.preview.budgetValid=await p.locator('#budget-result').innerText();if(!result.preview.budgetValid.includes('240.00'))throw new Error('Budget calculation incorrect');
 await p.locator('[data-row="0"][data-field="qty"]').fill('1.5');result.preview.budgetInvalid=await p.locator('#budget-result').innerText();if(!result.preview.budgetInvalid.includes('整数'))throw new Error('Fractional pieces allowed');
 for(const input of await p.locator('.budget input').all())await input.fill('');
 result.preview.budgetBlank=await p.locator('#budget-result').innerText();
 result.preview.selected=selected;result.preview.desktopOverflow=await p.evaluate(()=>document.documentElement.scrollWidth>window.innerWidth);
 result.preview.links=await p.locator('a[href]').evaluateAll(a=>a.map(x=>x.getAttribute('href')).filter(x=>!x.startsWith('#')));
 result.preview.missingLinks=result.preview.links.filter(x=>!fs.existsSync(path.resolve(root,x))&&!x.endsWith('BeePump_V2.1_Draft_Review.pdf'));
 await p.setViewportSize({width:390,height:844});await p.evaluate(()=>window.scrollTo(0,0));await p.screenshot({path:path.join(out,'mobile_overview.png')});result.preview.mobileOverflow=await p.evaluate(()=>document.documentElement.scrollWidth>window.innerWidth);
 await p.setViewportSize({width:1440,height:1050});await p.goto('file://'+path.join(root,'review/review_print.html'));
 result.pdf.pages=await p.locator('.page').count();
 result.pdf.layout=await p.locator('.page').evaluateAll(pages=>pages.map((e,i)=>{const body=e.querySelector('.body').getBoundingClientRect(),foot=e.querySelector('footer').getBoundingClientRect();return {page:i+1,bodyBottom:body.bottom-e.getBoundingClientRect().top,footerTop:foot.top-e.getBoundingClientRect().top,noFooterCollision:body.bottom<foot.top-4,horizontalOverflow:e.scrollWidth>e.clientWidth+1}}));
 await p.pdf({path:path.join(root,'output/pdf/BeePump_V2.1_Draft_Review.pdf'),printBackground:true,preferCSSPageSize:true,displayHeaderFooter:false});
 result.passed=result.pageErrors.length===0&&result.externalRequests.length===0&&!result.preview.desktopOverflow&&!result.preview.mobileOverflow&&result.preview.missingLinks.length===0&&result.artboards.every(a=>a.textChecks.every(t=>t.inside))&&result.pdf.layout.every(p=>p.noFooterCollision&&!p.horizontalOverflow);
 fs.writeFileSync(path.join(root,'reports/v2_render_qa.json'),JSON.stringify(result,null,2));
 console.log(JSON.stringify({passed:result.passed,pages:result.pdf.pages,artboardOverflow:result.artboards.flatMap(a=>a.textChecks.filter(t=>!t.inside).map(t=>({code:a.code,...t}))),pdfIssues:result.pdf.layout.filter(p=>!p.noFooterCollision||p.horizontalOverflow),preview:result.preview,externalRequests:result.externalRequests,pageErrors:result.pageErrors},null,2));
 await b.close();
})().catch(e=>{console.error(e);process.exitCode=1});

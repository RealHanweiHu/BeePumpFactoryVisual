const fs=require('fs'),path=require('path');
const {chromium}=require('/Users/huhanwei/.npm/_npx/31e32ef8478fbf80/node_modules/playwright');
const root=path.resolve(__dirname,'..'),out=path.join(root,'reports/installation_render');
const pdf='output/pdf/BeePump_Installation_Concept_Review_V2.2.pdf';
(async()=>{
 fs.mkdirSync(out,{recursive:true});fs.mkdirSync(path.dirname(path.join(root,pdf)),{recursive:true});
 const r={externalRequests:[],pageErrors:[],svgs:[],preview:{},pdf:{},data:{}};
 const b=await chromium.launch({headless:true,executablePath:'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',args:['--disable-background-networking']});
 const p=await b.newPage({viewport:{width:1440,height:1050}});
 p.on('pageerror',e=>r.pageErrors.push(String(e)));
 await p.route(/^https?:/,route=>{r.externalRequests.push(route.request().url());route.abort()});
 for(const name of ['安装选址_相对关系示意','8F候选原图_核查引线']){
  await p.goto('file://'+path.join(root,'outputs/installation_review',name+'.svg'));
  await p.evaluate(()=>{const s=document.documentElement;s.style.width='1400px';s.style.height='auto';s.style.display='block'});
  await p.evaluate(()=>document.fonts.ready);
  const checks=await p.evaluate(()=>{const s=document.documentElement,v=s.viewBox.baseVal;return [...s.querySelectorAll(':scope > g > text')].map(t=>{const z=t.getBBox();return {text:t.textContent,inside:z.x>=0&&z.y>=0&&z.x+z.width<=v.width&&z.y+z.height<=v.height}})});
  await p.locator('svg').first().screenshot({path:path.join(out,name+'.png')});r.svgs.push({name,textChecks:checks});
 }
 await p.goto('file://'+path.join(root,'INSTALLATION_REVIEW.html'));
 const decoded=await p.evaluate(async()=>{await document.fonts.ready;return Promise.all([...document.images].filter(i=>i.hasAttribute('src')).map(async i=>{try{await i.decode();return {src:i.getAttribute('src'),ok:true}}catch(e){return {src:i.getAttribute('src'),ok:false,error:String(e)}}}))});
 console.log(JSON.stringify({decoded}));
 r.preview.images=await p.locator('img.zoomable').evaluateAll(xs=>xs.map(x=>({src:x.getAttribute('src'),loaded:x.complete&&x.naturalWidth>0})));
 r.preview.modalChecks=[];
 for(let i=0;i<await p.locator('img.zoomable').count();i++){
  await p.locator('img.zoomable').nth(i).click();const opened=await p.locator('#zoom').evaluate(e=>e.open);await p.locator('#close').click();
  r.preview.modalChecks.push({index:i,opened,closed:!(await p.locator('#zoom').evaluate(e=>e.open))});
 }
 await p.locator('img.zoomable').first().focus();await p.keyboard.press('Enter');r.preview.keyboardModalOpened=await p.locator('#zoom').evaluate(e=>e.open);await p.keyboard.press('Escape');r.preview.escapeClosed=!(await p.locator('#zoom').evaluate(e=>e.open));
 await p.evaluate(()=>window.scrollTo(0,0));await p.screenshot({path:path.join(out,'desktop.png')});
 r.preview.desktopOverflow=await p.evaluate(()=>document.documentElement.scrollWidth>innerWidth);
 await p.setViewportSize({width:390,height:844});await p.evaluate(()=>window.scrollTo(0,0));await p.screenshot({path:path.join(out,'mobile.png')});
 r.preview.mobileOverflow=await p.evaluate(()=>document.documentElement.scrollWidth>innerWidth);
 await p.setViewportSize({width:1588,height:1123});await p.goto('file://'+path.join(root,'outputs/installation_review/installation_print.html'));
 const printDecoded=await p.evaluate(async()=>{await document.fonts.ready;return Promise.all([...document.images].map(async i=>{try{await i.decode();return {src:i.getAttribute('src').slice(0,40),ok:true}}catch(e){return {src:i.getAttribute('src').slice(0,40),ok:false,error:String(e)}}}))});
 r.pdf.images=printDecoded;
 r.pdf.pages=await p.locator('.page').count();
 r.pdf.layout=await p.locator('.page').evaluateAll(xs=>xs.map((e,i)=>{const z=e.getBoundingClientRect(),body=e.querySelector('.body').getBoundingClientRect(),f=e.querySelector('footer').getBoundingClientRect();return {page:i+1,bodyBottom:body.bottom-z.top,footerTop:f.top-z.top,noFooterCollision:body.bottom<f.top-4,horizontalOverflow:e.scrollWidth>e.clientWidth+1}}));
 await p.pdf({path:path.join(root,pdf),printBackground:true,preferCSSPageSize:true,displayHeaderFooter:false});
 await p.goto('file://'+path.join(root,'INSTALLATION_REVIEW.html'));
 r.preview.links=await p.locator('a[href]').evaluateAll(xs=>xs.map(x=>x.getAttribute('href')).filter(x=>!x.startsWith('#')));
 r.preview.missingLinks=r.preview.links.filter(x=>!fs.existsSync(path.resolve(root,x)));
 await p.goto('file://'+path.join(root,'START_HERE.html'));
 r.preview.mainIndexLinksReview=await p.locator('a[href="INSTALLATION_REVIEW.html"]').count()===1;
 const points=JSON.parse(fs.readFileSync(path.join(root,'data/points.json'))),d=JSON.parse(fs.readFileSync(path.join(root,'outputs/installation_review/安装选址评审台账.json')));
 r.data.actualPointCount=points.points.length;r.data.groups=d.length;
 r.data.noInventedFields=d.every(x=>x.position_world===null&&x.point_id===null&&x.quantity===null&&x.installation_height_mm===null&&Object.values(x.approvals).every(a=>a===null));
 r.passed=r.externalRequests.length===0&&r.pageErrors.length===0&&r.svgs.every(s=>s.textChecks.every(t=>t.inside))&&r.preview.images.every(i=>i.loaded)&&r.preview.modalChecks.every(m=>m.opened&&m.closed)&&r.preview.keyboardModalOpened&&r.preview.escapeClosed&&!r.preview.desktopOverflow&&!r.preview.mobileOverflow&&r.preview.missingLinks.length===0&&r.preview.mainIndexLinksReview&&r.pdf.pages===8&&r.pdf.images.every(x=>x.ok)&&r.pdf.layout.every(x=>x.noFooterCollision&&!x.horizontalOverflow)&&r.data.actualPointCount===0&&r.data.groups===7&&r.data.noInventedFields;
 fs.writeFileSync(path.join(root,'reports/installation_qa.json'),JSON.stringify(r,null,2));
 console.log(JSON.stringify({passed:r.passed,pages:r.pdf.pages,svgIssues:r.svgs.flatMap(s=>s.textChecks.filter(t=>!t.inside).map(t=>({name:s.name,...t}))),pdfIssues:r.pdf.layout.filter(x=>!x.noFooterCollision||x.horizontalOverflow),preview:r.preview,data:r.data,pageErrors:r.pageErrors,externalRequests:r.externalRequests},null,2));
 await b.close();if(!r.passed)process.exitCode=1;
})().catch(e=>{console.error(e);process.exitCode=1});

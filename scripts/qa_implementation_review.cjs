const fs=require('fs'),path=require('path');
const {chromium}=require('/Users/huhanwei/.npm/_npx/31e32ef8478fbf80/node_modules/playwright');
const root=path.resolve(__dirname,'..'),out=path.join(root,'reports/implementation_render');
(async()=>{
 fs.mkdirSync(out,{recursive:true});fs.mkdirSync(path.join(root,'output/pdf'),{recursive:true});
 const r={externalRequests:[],pageErrors:[],diagrams:[],preview:{},pdfs:[]};
 const b=await chromium.launch({headless:true,executablePath:'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',args:['--disable-background-networking']});
 const p=await b.newPage({viewport:{width:1440,height:1050}});
 p.on('pageerror',e=>r.pageErrors.push(String(e)));
 await p.route(/^https?:/,route=>{r.externalRequests.push(route.request().url());route.abort()});
 const mf=JSON.parse(fs.readFileSync(path.join(root,'outputs/implementation_v2.4/review_manifest.json')));
 for(const file of mf.figures){
  await p.goto('file://'+path.join(root,file));await p.evaluate(()=>{document.documentElement.style.width='1400px';document.documentElement.style.height='auto'});await p.evaluate(()=>document.fonts.ready);
  const checks=await p.evaluate(()=>{const v=document.documentElement.viewBox.baseVal;return [...document.querySelectorAll('text')].map(t=>{const z=t.getBBox();return {text:t.textContent,inside:z.x>=0&&z.y>=0&&z.x+z.width<=v.width&&z.y+z.height<=v.height,box:{x:z.x,y:z.y,w:z.width,h:z.height}}})});
  await p.locator('svg').screenshot({path:path.join(out,path.basename(file,'.svg')+'.png')});r.diagrams.push({file,checks});
 }
 for(const [input,output,key] of [['implementation_print.html','BeePump_1F_8F_Implementation_Design_V2.4.pdf','design'],['forms_print.html','BeePump_1F_8F_SettingOut_Acceptance_Forms_V2.4.pdf','forms']]){
  await p.setViewportSize({width:key==='design'?1588:794,height:1123});await p.goto('file://'+path.join(root,'outputs/implementation_v2.4',input));await p.evaluate(()=>document.fonts.ready);
  const images=await p.evaluate(async()=>Promise.all([...document.images].map(async x=>{try{await x.decode();return true}catch(e){return false}})));
  const layout=await p.locator('.page').evaluateAll(xs=>xs.map((e,i)=>{const z=e.getBoundingClientRect(),bd=e.querySelector('.body'),f=e.querySelector('footer').getBoundingClientRect();const bottom=Math.max(bd.getBoundingClientRect().bottom,...[...bd.querySelectorAll('*')].map(x=>x.getBoundingClientRect().bottom));return {page:i+1,title:e.querySelector('h1').textContent,bodyBottom:bottom-z.top,footerTop:f.top-z.top,noFooterCollision:bottom<f.top-4,horizontalOverflow:e.scrollWidth>e.clientWidth+1}}));
  fs.writeFileSync(path.join(out,key+'_layout.json'),JSON.stringify({images,layout},null,2));
  await p.waitForTimeout(500);
  if(key==='design'){
   const chunks=path.join(root,'tmp/pdfs/implementation_chunks');fs.mkdirSync(chunks,{recursive:true});const files=[];
   for(let start=1;start<=layout.length;start+=8){const file=path.join(chunks,`pages_${start}.pdf`);await p.pdf({path:file,printBackground:true,preferCSSPageSize:true,displayHeaderFooter:false,pageRanges:`${start}-${Math.min(start+7,layout.length)}`,timeout:120000});files.push(file)}
   require('child_process').execFileSync('swift',['-module-cache-path','/tmp/beepump-swift-module-cache',path.join(root,'scripts/merge_review_pdf.swift'),path.join(root,'output/pdf',output),...files]);
  }else await p.pdf({path:path.join(root,'output/pdf',output),printBackground:true,preferCSSPageSize:true,displayHeaderFooter:false,timeout:120000});
  r.pdfs.push({key,output,pages:layout.length,images,layout});
 }
 await p.setViewportSize({width:1440,height:1050});await p.goto('file://'+path.join(root,'IMPLEMENTATION_1F_8F.html'));await p.evaluate(()=>document.fonts.ready);
 r.preview.images=await p.evaluate(async()=>Promise.all([...document.images].filter(x=>x.hasAttribute('src')).map(async x=>{try{await x.decode();return true}catch(e){return false}})));
 r.preview.all=await p.locator('.requirement:visible').count();
 for(const f of ['1F','8F','all']){await p.locator('#floor-filter').selectOption(f);r.preview[f]=await p.locator('.requirement:visible').count()}
 r.preview.filterPassed=r.preview['1F']===19&&r.preview['8F']===21&&r.preview.all===40;
 const first=p.locator('main img').first();await first.focus();await p.keyboard.press('Enter');r.preview.keyboardZoom=await p.locator('#zoom').evaluate(x=>x.open);await p.keyboard.press('Escape');r.preview.escapeClosed=!(await p.locator('#zoom').evaluate(x=>x.open));
 await p.locator('summary').first().click();r.preview.detailsWorks=await p.locator('details').first().evaluate(x=>x.open);await p.locator('summary').first().click();
 await p.evaluate(()=>window.scrollTo(0,0));await p.screenshot({path:path.join(out,'desktop.png')});r.preview.desktopOverflow=await p.evaluate(()=>document.documentElement.scrollWidth>innerWidth);
 const links=await p.locator('a[href]').evaluateAll(xs=>xs.map(x=>x.getAttribute('href')).filter(x=>!x.startsWith('#')&&!x.startsWith('http')));
 r.preview.localLinks=links.length;r.preview.missingLinks=links.filter(x=>!fs.existsSync(path.resolve(root,x)));
 await p.setViewportSize({width:390,height:844});await p.evaluate(()=>window.scrollTo(0,0));await p.waitForTimeout(250);await p.screenshot({path:path.join(out,'mobile.png')});r.preview.mobileOverflow=await p.evaluate(()=>document.documentElement.scrollWidth>innerWidth);
 await b.close();
 r.passed=r.pageErrors.length===0&&r.externalRequests.length===0&&r.diagrams.every(x=>x.checks.every(t=>t.inside))&&r.preview.images.every(Boolean)&&r.pdfs.every(x=>x.images.every(Boolean)&&x.layout.every(y=>y.noFooterCollision&&!y.horizontalOverflow))&&!r.preview.mobileOverflow&&!r.preview.desktopOverflow&&r.preview.filterPassed&&r.preview.keyboardZoom&&r.preview.escapeClosed&&r.preview.detailsWorks;
 fs.writeFileSync(path.join(root,'reports/implementation_qa.json'),JSON.stringify(r,null,2));
 console.log(JSON.stringify({passed:r.passed,pages:r.pdfs.map(x=>[x.key,x.pages]),layoutIssues:r.pdfs.flatMap(x=>x.layout.filter(y=>!y.noFooterCollision||y.horizontalOverflow).map(y=>({key:x.key,...y}))),diagramIssues:r.diagrams.flatMap(x=>x.checks.filter(t=>!t.inside).map(t=>({file:x.file,...t}))),preview:r.preview},null,2));process.exit(r.passed?0:2);
})().catch(e=>{console.error(e);process.exit(1)});

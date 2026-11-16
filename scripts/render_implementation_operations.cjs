const fs = require('fs');
const path = require('path');
const { chromium } = require('/Users/huhanwei/.npm/_npx/31e32ef8478fbf80/node_modules/playwright');
const root = path.resolve(__dirname, '..');
const out = path.join(root, 'reports/implementation_operations_render');
const mpath = path.join(root,'outputs/implementation_v2.4/operations_template_manifest.json');
const hash = p => require('crypto').createHash('sha256').update(fs.readFileSync(p)).digest('hex');
(async () => {
  fs.mkdirSync(path.join(out,'v1'), {recursive:true});
  const browser = await chromium.launch({headless:true, executablePath:'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',args:['--disable-background-networking']});
  const page = await browser.newPage({viewport:{width:1600,height:1400}});
  const result = {browser:'Installed Chrome / cached Playwright',externalRequests:[],pageErrors:[],artboards:[]};
  await page.route(/^https?:/, route => {result.externalRequests.push(route.request().url()); return route.abort();});
  page.on('pageerror', e=>result.pageErrors.push(String(e)));
  const manifest = JSON.parse(fs.readFileSync(mpath));
  for (const m of manifest) {
    for (const stage of ['v1','v2']) {
      const input = path.join(root,stage==='v1'?m.source_path:m.path);
      await page.goto('file://'+input);
      await page.evaluate(()=>document.fonts.ready);
      await page.evaluate(()=>{if(document.body)document.body.style.margin='0'; const s=document.querySelector('svg'),v=s.viewBox.baseVal;const scale=Math.min(1500/v.width,1300/v.height);s.style.width=(v.width*scale)+'px';s.style.height=(v.height*scale)+'px';s.style.display='block';});
      const checks=await page.evaluate(()=>{
        const s=document.querySelector('svg'),v=s.viewBox.baseVal;
        const texts=[...s.querySelectorAll('text')].map(t=>{const r=t.getBBox(); return {text:t.textContent,bbox:{x:r.x,y:r.y,w:r.width,h:r.height},nominalEmMM:Number(t.getAttribute('font-size')),inside:r.x>=-0.1&&r.y>=-0.1&&r.x+r.width<=v.width+0.1&&r.y+r.height<=v.height+0.1};});
        const collisions=[];
        for(let i=0;i<texts.length;i++)for(let j=i+1;j<texts.length;j++) {const a=texts[i].bbox,b=texts[j].bbox; const ix=Math.min(a.x+a.w,b.x+b.w)-Math.max(a.x,b.x),iy=Math.min(a.y+a.h,b.y+b.h)-Math.max(a.y,b.y); if(ix>0.5&&iy>0.5)collisions.push({a:texts[i].text,b:texts[j].text,overlap:[ix,iy]});}
        return {fontAvailable:document.fonts.check('16px "PingFang SC"'),viewBox:[v.width,v.height],textChecks:texts,collisions};
      });
      const png=path.join(out,stage==='v1'?'v1':'',m.code+'.png');
      await page.locator('svg').screenshot({path:png});
      result.artboards.push({code:m.code,stage,source:stage==='v1'?m.source_path:m.path,png:path.relative(root,png),...checks});
      if(stage==='v2') {m.render_png_sha256=hash(png);m.render_qa_path='reports/implementation_operations_render/render_qa.json';m.render_review_status='pending_pixel_review';}
    }
  }
  result.passed=result.externalRequests.length===0&&result.pageErrors.length===0&&result.artboards.filter(a=>a.stage==='v2').every(a=>a.textChecks.every(t=>t.inside)&&a.collisions.length===0);
  fs.writeFileSync(path.join(out,'render_qa.json'),JSON.stringify(result,null,2)+'\n');
  fs.writeFileSync(mpath,JSON.stringify(manifest,null,2)+'\n');
  console.log(JSON.stringify({passed:result.passed,artboards:result.artboards.length,issues:result.artboards.filter(a=>a.stage==='v2'&&(!a.textChecks.every(t=>t.inside)||a.collisions.length)).map(a=>({code:a.code,overflow:a.textChecks.filter(t=>!t.inside),collisions:a.collisions})),externalRequests:result.externalRequests,pageErrors:result.pageErrors},null,2));
  // Local contact sheets preserve full card aspect ratios and are never site evidence.
  await page.goto('about:blank');
  for(const stage of ['v1','v2'])for(let start=0;start<manifest.length;start+=5) {
    const group=manifest.slice(start,start+5);
    const cards=group.map(m=>{const p=path.join(out,stage==='v1'?'v1':'',m.code+'.png');const image='data:image/png;base64,'+fs.readFileSync(p).toString('base64');return `<article><h2>${m.code} ${m.name}</h2><div>${m.w} × ${m.h} mm · ${stage==='v1'?'V1':m.revision}</div><img src="${image}"></article>`;}).join('');
    await page.setViewportSize({width:1800,height:1460});
    await page.setContent(`<html lang="zh-CN"><meta charset="utf-8"><style>body{margin:16px;background:#ddd;font:16px "PingFang SC",sans-serif}main{display:grid;grid-template-columns:repeat(3,1fr);gap:16px}article{background:white;padding:18px;min-height:650px}h2{margin:0 0 10px}img{width:100%;height:570px;object-fit:contain}</style><main>${cards}</main></html>`);
    await page.screenshot({path:path.join(out,`${stage}_contact_${Math.floor(start/5)+1}.png`),fullPage:true});
  }
  await browser.close();
  if(!result.passed)process.exitCode=1;
})().catch(e=>{console.error(e);process.exitCode=1;});

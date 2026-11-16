const fs=require('fs');
const path=require('path');
const {chromium}=require('/Users/huhanwei/.npm/_npx/31e32ef8478fbf80/node_modules/playwright');
const root=path.resolve(__dirname,'..');
const out=path.join(root,'reports/implementation_template_render');
const originals=process.argv.includes('--originals');
(async()=>{
 fs.mkdirSync(out,{recursive:true});
 const codes=['BE-01','BE-02','WF-01','WF-02','EQ-01','EQ-03','SW-01','SW-02','QC-05','BE-04'];
 const manifest=originals ? JSON.parse(fs.readFileSync(path.join(root,'data/templates.json'),'utf8')).filter(t=>t.revision==='V1.0'&&codes.includes(t.code)) : JSON.parse(fs.readFileSync(path.join(root,'outputs/implementation_v2.4/template_manifest.json'),'utf8'));
 const target=originals?path.join(out,'v1'):out;
 fs.mkdirSync(target,{recursive:true});
 const browser=await chromium.launch({headless:true,executablePath:'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',args:['--disable-background-networking']});
 const page=await browser.newPage({viewport:{width:1600,height:1300},deviceScaleFactor:1});
 const result={browser:'Installed Chrome, cached Playwright; no installation',external_requests:[],page_errors:[],stage:originals?'V1-before-edit':'V2.4-proposal',artboards:[]};
 page.on('pageerror',e=>result.page_errors.push(String(e)));
 await page.route(/^https?:/,route=>{result.external_requests.push(route.request().url());route.abort()});
 for(const m of manifest){
  const id=originals?m.code:(m.variant_id||m.code);
  const svg=fs.readFileSync(path.join(root,m.path),'utf8');
  await page.setContent('<html lang="zh-CN"><meta charset="utf-8"><style>body{margin:18px;background:#e9e9e9}svg{display:block;max-width:1500px;width:auto;max-height:1200px;height:auto;margin:auto;background:white}</style>'+svg+'</html>');
  await page.evaluate(()=>document.fonts.ready);
  const qa=await page.evaluate(()=>{
   const s=document.querySelector('svg'),v=s.viewBox.baseVal;
   const txt=[...s.querySelectorAll('text')].map(t=>{const b=t.getBBox(),c=getComputedStyle(t);return{text:t.textContent,bbox:{x:b.x,y:b.y,width:b.width,height:b.height},inside:b.x>=-0.05&&b.y>=-0.05&&b.x+b.width<=v.width+0.05&&b.y+b.height<=v.height+0.05,fill:c.fill,font:c.fontFamily,nominal_em_mm:Number(t.getAttribute('font-size'))}});
   const overlaps=[];
   for(let i=0;i<txt.length;i++)for(let j=i+1;j<txt.length;j++){
    const a=txt[i].bbox,b=txt[j].bbox;
    const x=Math.min(a.x+a.width,b.x+b.width)-Math.max(a.x,b.x),y=Math.min(a.y+a.height,b.y+b.height)-Math.max(a.y,b.y);
    if(x>0.08&&y>0.08)overlaps.push({a:txt[i].text,b:txt[j].text,intersection:[x,y]});
   }
   return{nominal_dimensions:[s.getAttribute('width'),s.getAttribute('height')],viewbox:[v.x,v.y,v.width,v.height],font_available:document.fonts.check('16px "PingFang SC"'),text_checks:txt,overlap_candidates:overlaps};
  });
  await page.locator('svg').screenshot({path:path.join(target,id+'.png')});
  result.artboards.push({id,path:m.path,render_png:path.relative(root,path.join(target,id+'.png')),...qa});
 }
 result.passed=result.external_requests.length===0&&result.page_errors.length===0&&result.artboards.every(a=>a.text_checks.every(t=>t.inside)&&a.overlap_candidates.length===0);
 fs.writeFileSync(path.join(out,originals?'v1_render_qa.json':'render_qa.json'),JSON.stringify(result,null,2));
 console.log(JSON.stringify({passed:result.passed,count:result.artboards.length,outside:result.artboards.flatMap(a=>a.text_checks.filter(t=>!t.inside).map(t=>({id:a.id,...t}))),overlap:result.artboards.filter(a=>a.overlap_candidates.length).map(a=>({id:a.id,overlap:a.overlap_candidates})),external_requests:result.external_requests,page_errors:result.page_errors},null,2));
 await browser.close();
})().catch(e=>{console.error(e);process.exitCode=1});

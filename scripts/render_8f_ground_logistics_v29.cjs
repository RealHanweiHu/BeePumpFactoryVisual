// Render local SVG review pages and print a vector A3 PDF without network access.
const fs=require('fs'),path=require('path');
const {chromium}=require('/Users/huhanwei/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const version=process.argv[2]||'V2.9';
if(!/^V\d+\.\d+(?:\.\d+)?$/.test(version))throw new Error('Invalid revision');
const root=path.resolve(__dirname,'..'),src=path.join(root,'design/v2/ground_logistics_'+version.toLowerCase()),out=path.join(root,'交付_8楼/地面物流规划_'+version);
(async()=>{
  fs.mkdirSync(path.join(out,'预览'),{recursive:true});
  const browser=await chromium.launch({headless:true,executablePath:'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',args:['--disable-background-networking']});
  const page=await browser.newPage({viewport:{width:1680,height:1188},deviceScaleFactor:1});
  const report={revision:version+'-GROUND-LOGISTICS-DRAFT',external_requests:[],errors:[],pages:[],artworks:[]};
  page.on('pageerror',e=>report.errors.push(String(e)));
  await page.route(/^https?:/,r=>{report.external_requests.push(r.request().url());return r.abort()});
  const files=fs.readdirSync(src).filter(n=>n.endsWith('.svg')).sort();
  const all=[];
  async function render(name,folder,target,list){
    const svg=fs.readFileSync(path.join(folder,name),'utf8');
    await page.setContent('<html lang="zh-CN"><meta charset="utf-8"><style>body{margin:0;background:white}svg{display:block}</style>'+svg+'</html>');
    await page.evaluate(()=>document.fonts.ready);
    await page.evaluate(()=>Promise.all([...document.querySelectorAll('image')].map(i=>new Promise((resolve,reject)=>{const im=new Image;im.onload=resolve;im.onerror=reject;im.src=i.getAttribute('href')}))));
    const bounds=await page.evaluate(()=>{
      const s=document.querySelector('svg'),v=s.viewBox.baseVal;
      return [...s.querySelectorAll(':scope > g > text')].flatMap(t=>{const b=t.getBBox();return b.x<0||b.y<0||b.x+b.width>v.width||b.y+b.height>v.height?[{text:t.textContent,bbox:[b.x,b.y,b.width,b.height]}]:[]});
    });
    await page.locator('body > svg').screenshot({path:target});
    list.push({name,text_outside_canvas:bounds});
    return svg;
  }
  for(const name of files)all.push(await render(name,src,path.join(out,'预览',name.replace('.svg','.png')),report.pages));
  const styles=path.join(src,'地贴样式');
  fs.mkdirSync(path.join(out,'预览/地贴样式'),{recursive:true});
  for(const name of fs.readdirSync(styles).filter(n=>n.endsWith('.svg')).sort())await render(name,styles,path.join(out,'预览/地贴样式',name.replace('.svg','.png')),report.artworks);
  await page.setContent('<!doctype html><html lang="zh-CN"><meta charset="utf-8"><title>8F 地面物流与地标规划 '+version+' 评审稿</title><style>@page{size:420mm 297mm;margin:0}body{margin:0}.page{width:420mm;height:297mm;break-after:page}.page:last-child{break-after:auto}.page>svg{width:420mm;height:297mm;display:block}</style>'+all.map(s=>'<section class="page">'+s+'</section>').join('')+'</html>');
  await page.evaluate(()=>document.fonts.ready);
  await page.pdf({path:path.join(out,'8F_地面物流与地标规划_评审稿.pdf'),preferCSSPageSize:true,printBackground:true,margin:{top:0,right:0,bottom:0,left:0}});
  report.revision=JSON.parse(await page.locator('section.page > svg > metadata').first().textContent()).revision;
  report.passed=report.external_requests.length===0&&report.errors.length===0&&[...report.pages,...report.artworks].every(p=>p.text_outside_canvas.length===0);
  fs.writeFileSync(path.join(out,'渲染检查.json'),JSON.stringify(report,null,2));
  console.log(JSON.stringify(report,null,2));
  await browser.close();if(!report.passed)process.exitCode=1;
})().catch(e=>{console.error(e);process.exit(1)});

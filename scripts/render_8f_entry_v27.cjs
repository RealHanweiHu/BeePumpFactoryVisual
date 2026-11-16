// Render repo-native SVG overlays with the existing local Chrome installation.
const fs = require('fs');
const path = require('path');
const {chromium} = require('/Users/huhanwei/.npm/_npx/31e32ef8478fbf80/node_modules/playwright');
const root = path.resolve(__dirname, '..');
const source = path.join(root, 'design/v2/entry_v2.7');
const out = path.join(root, '交付_8楼/客梯入口修订_V2.7');
(async () => {
  const browser = await chromium.launch({headless:true,
    executablePath:'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
    args:['--disable-background-networking']});
  const page = await browser.newPage({viewport:{width:3400,height:2450},deviceScaleFactor:1});
  const report = {revision:'V2.7-ENTRY-CORRECTION-DRAFT',external_requests:[],errors:[],artboards:[]};
  page.on('pageerror',e=>report.errors.push(String(e)));
  await page.route(/^https?:/,r=>{report.external_requests.push(r.request().url());return r.abort();});
  for(const name of fs.readdirSync(source).filter(n=>n.endsWith('.svg')).sort()){
    const svg=fs.readFileSync(path.join(source,name),'utf8').replace(/<\?xml[^>]*>/,'');
    await page.setContent('<html lang="zh-CN"><meta charset="utf-8"><style>body{margin:0}svg{display:block}</style>'+svg+'</html>',{waitUntil:'load'});
    await page.evaluate(()=>document.fonts.ready);
    const bounds=await page.evaluate(()=>{
      const s=document.querySelector('svg'),v=s.viewBox.baseVal;
      return [...s.querySelectorAll('text')].flatMap(t=>{
        const b=t.getBBox();
        return b.x < 0 || b.y < 0 || b.x+b.width > v.width || b.y+b.height > v.height ? [{text:t.textContent,bbox:[b.x,b.y,b.width,b.height]}] : [];
      });
    });
    await page.locator('svg').screenshot({path:path.join(out,name.replace('.svg','.png'))});
    report.artboards.push({name,text_outside_canvas:bounds});
  }
  report.passed=report.errors.length===0 && report.external_requests.length===0 && report.artboards.every(a=>!a.text_outside_canvas.length);
  fs.writeFileSync(path.join(out,'渲染检查_V2.7.json'),JSON.stringify(report,null,2));
  console.log(JSON.stringify(report,null,2));
  await browser.close();
  if(!report.passed) process.exitCode=1;
})().catch(e=>{console.error(e);process.exitCode=1;});

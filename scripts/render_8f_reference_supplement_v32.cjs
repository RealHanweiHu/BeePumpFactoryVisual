// Render the four standalone review sheets and verify the local review entry.
const fs = require('node:fs');
const path = require('node:path');
const crypto = require('node:crypto');
const {pathToFileURL, fileURLToPath} = require('node:url');
const {chromium} = require('playwright');

const root = path.resolve(__dirname, '..');
const source = path.join(root, 'design/v2/8f_reference_supplement_v3.2');
const output = path.join(root, '交付_8楼/点位补充_V3.2');
const results = path.join(root, 'reports/8f_reference_supplement_v3.2');
const pdfPath = path.join(output, 'output/pdf/8F_点位补充与踏勘图_V3.2.pdf');
const files = fs.readdirSync(source).filter(name => name.endsWith('.svg')).sort();

async function main() {
  fs.mkdirSync(path.dirname(pdfPath), {recursive:true});
  fs.mkdirSync(results, {recursive:true});
  const browser = await chromium.launch({
    channel: 'chrome',
    args: ['--disable-background-networking'],
  });
  try {
    const page = await browser.newPage({viewport:{width:1680,height:1188}});
    const report = {pages:[], errors:[], externalRequests:[]};
    page.on('pageerror', error => report.errors.push(String(error)));
    await page.route(/^https?:/, route => {
      report.externalRequests.push(route.request().url());
      return route.abort();
    });
    const sheets = files.map(name => fs.readFileSync(path.join(source,name),'utf8'));
    if (sheets.length !== 4) throw new Error('Expected four review sheets');
    await page.setContent(`<!doctype html><html lang="zh-CN"><meta charset="utf-8">
<title>8F 点位补充与踏勘图 · V3.2</title><style>
@page{size:A3 landscape;margin:0}body{margin:0}section{width:420mm;height:297mm;break-after:page}
section:last-child{break-after:auto}section>svg{width:420mm;height:297mm;display:block}
</style>${sheets.map(sheet => '<section>' + sheet + '</section>').join('')}`);
    await page.evaluate(() => document.fonts.ready);
    report.pages = await page.locator('section > svg').evaluateAll(svgs => svgs.map(svg => {
      const {width,height} = svg.viewBox.baseVal;
      return {
        title: svg.getAttribute('aria-label'),
        markers: svg.querySelectorAll('g[id^="K"]').length,
        outside: Array.from(svg.querySelectorAll(':scope > g > text')).filter(node => {
          const box = node.getBBox();
          return box.x < 0 || box.y < 0 || box.x+box.width > width || box.y+box.height > height;
        }).map(node => node.textContent),
      };
    }));
    await page.pdf({path:pdfPath, preferCSSPageSize:true, printBackground:true});
    report.pdfSha256 = crypto.createHash('sha256').update(fs.readFileSync(pdfPath)).digest('hex');

    const reviewUrl = pathToFileURL(path.join(output, '打开这里.html')).href;
    await page.goto(pathToFileURL(path.join(root, '交付_8楼/打开这里.html')).href);
    await page.locator('#reference-supplement .primary').click();
    await page.waitForURL(reviewUrl);
    await page.evaluate(() => document.fonts.ready);
    const internal = await page.locator('a[href], img[src]').evaluateAll(elements => elements.map(node => ({
      url: node.href || node.src, imageLoaded: node.tagName !== 'IMG' || node.complete && node.naturalWidth > 0,
    })));
    report.linksChecked = internal.length;
    report.badLinks = [];
    for (const {url,imageLoaded} of internal) {
      const target = new URL(url);
      const onCurrentPage = target.hash && target.href.split('#')[0] === reviewUrl;
      if (onCurrentPage) {
        const found = await page.evaluate(hash => Boolean(document.getElementById(decodeURIComponent(hash.slice(1)))), target.hash);
        if (!found) report.badLinks.push(url);
      } else if (target.protocol !== 'file:' || !fs.existsSync(fileURLToPath(target)) || !imageLoaded) {
        report.badLinks.push(url);
      }
    }
    await page.locator('#crosswalk a[href="#K04"]').click();
    await page.waitForFunction(() => location.hash === '#K04' && document.getElementById('K04').open,
      undefined, {timeout:5000});
    report.crosswalkRevealsDetail = true;
    await page.setViewportSize({width:390,height:844});
    await page.goto(reviewUrl);
    await page.evaluate(() => document.fonts.ready);
    report.mobileFits = await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth);
    await page.screenshot({path:path.join(results, '离线入口_移动端.png')});

    fs.writeFileSync(path.join(results,'render-and-links.json'), JSON.stringify(report,null,2)+'\n');
    console.log(JSON.stringify(report,null,2));
    if (report.pages.some(sheet => sheet.outside.length) || report.errors.length || report.badLinks.length ||
        report.externalRequests.length || !report.crosswalkRevealsDetail || !report.mobileFits) {
      throw new Error('Review rendering or link verification failed');
    }
  } finally {
    await browser.close();
  }
}

main().catch(error => { console.error(error); process.exitCode = 1; });

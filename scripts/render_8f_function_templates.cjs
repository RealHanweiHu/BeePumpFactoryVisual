// Deterministic SVG rasterization, entirely local; no browser or network.
const fs=require('fs'),path=require('path');
const sharp=require('/Users/huhanwei/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/sharp');
const root=path.resolve(__dirname,'..'),dir=path.join(root,'reports/point_effects_2026-10-26/template_render');
fs.mkdirSync(dir,{recursive:true});
const manifest=JSON.parse(fs.readFileSync(path.join(root,'design/v2/point_effects_2026-10-26/templates/manifest.json')));
(async()=>{
 const rows=[];
 for(const t of manifest.templates){
  for(const [stage,file] of [['before',t.source_path],['after',t.path]]){
   let svg=fs.readFileSync(path.join(root,file),'utf8');const tag=svg.match(/<svg\b[^>]*>/)[0];
   const [w,h]=t.physical_size_mm,scale=Math.min(1600/w,1100/h);
   const resizedTag=tag.replace(/\bwidth="[^"]*"/,'width="'+Math.round(w*scale)+'"').replace(/\bheight="[^"]*"/,'height="'+Math.round(h*scale)+'"');
   svg=svg.replace(tag,resizedTag);
   const dest=path.join(dir,t.code+'_'+stage+'.png');
   await sharp(Buffer.from(svg)).png().toFile(dest);
   rows.push({code:t.code,stage,source:file,path:path.relative(root,dest)});
  }
 }
 fs.writeFileSync(path.join(dir,'render_record.json'),JSON.stringify({engine:'local sharp/librsvg; no browser or network access',rows,status:'rendered_pending_pixel_review'},null,2));
 console.log('Rendered '+rows.length+' SVG previews using local librsvg.');
})().catch(e=>{console.error(e);process.exit(1)});

"""Partial read-only SVG rendering for source review, never a construction base."""
from pathlib import Path
import json, math, html, collections
R=Path(__file__).resolve().parents[1];P=R/'outputs/drawings'
es=json.loads((P/'cad_entities.json').read_text());bs=json.loads((P/'cad_blocks.json').read_text())
window=[1000000,967000,1135000,1070000];xmin,ymin,xmax,ymax=window
scale=2000/(xmax-xmin);W=2000;H=(ymax-ymin)*scale
seen=collections.Counter();omitted=collections.Counter();fragments=[]
def one(e,c,d=None):return next((v for k,v in e if k==c),d)
def num(e,c,d=0):
 try:return float(one(e,c,d))
 except (ValueError,TypeError):return d
def p(e,c):return num(e,c),num(e,c+10)
def tr(pt,m):x,y=pt;a,b,c,d,tx,ty=m;return a*x+c*y+tx,b*x+d*y+ty
def compose(m,n):
 a,b,c,d,x,y=m;A,B,C,D,X,Y=n
 return [a*A+c*B,b*A+d*B,a*C+c*D,b*C+d*D,a*X+c*Y+x,b*X+d*Y+y]
def display(pt):return (pt[0]-xmin)*scale,(ymax-pt[1])*scale
def visible(pts):return max(x for x,y in pts)>=xmin and min(x for x,y in pts)<=xmax and max(y for x,y in pts)>=ymin and min(y for x,y in pts)<=ymax
def path(pts,closed=False):
 if not pts or not visible(pts):return
 ps=[display(pt) for pt in pts]
 d='M'+' L'.join(f'{x:.3f},{y:.3f}' for x,y in ps)+(' Z' if closed else '')
 fragments.append('<path d="'+d+'"/>')
def render(e,m,depth=0):
 if depth>10:return
 k=one(e,0);seen[k]+=1
 if k=='LINE':path([tr(p(e,10),m),tr(p(e,11),m)])
 elif k=='LWPOLYLINE':
  pts=[];current=None
  for c,v in e:
   if c==10:current=[float(v),0];pts.append(current)
   elif c==20 and current is not None:current[1]=float(v)
  if any(c==42 and abs(float(v))>1e-10 for c,v in e):omitted['polyline_bulge_approximated_as_chord']+=1
  path([tr(pt,m) for pt in pts],bool(int(num(e,70))&1))
 elif k in ('CIRCLE','ARC'):
  x,y=p(e,10);r=num(e,40);a=num(e,50) if k=='ARC' else 0;z=num(e,51) if k=='ARC' else 360
  if z<a:z+=360
  pts=[tr((x+r*math.cos(math.radians(a+(z-a)*i/80)),y+r*math.sin(math.radians(a+(z-a)*i/80))),m) for i in range(81)]
  path(pts,k=='CIRCLE')
 elif k in ('SOLID','TRACE'):path([tr(p(e,c),m) for c in (10,11,13,12)],True)
 elif k=='INSERT':
  name=one(e,2);block=bs.get(name)
  if not block:omitted['missing_block']+=1;return
  a=math.radians(num(e,50));sx=num(e,41,1);sy=num(e,42,1);x,y=p(e,10);bx,by=block['base'][:2]
  n=[sx*math.cos(a),sx*math.sin(a),-sy*math.sin(a),sy*math.cos(a),x-bx*sx*math.cos(a)+by*sy*math.sin(a),y-bx*sx*math.sin(a)-by*sy*math.cos(a)]
  for child in block['entities']:render(child,compose(m,n),depth+1)
 elif k=='DIMENSION':
  block=bs.get(one(e,2))
  if block:
   for child in block['entities']:render(child,m,depth+1)
 elif k in ('TEXT','MTEXT','ATTRIB','ATTDEF'):
  pt=tr(p(e,10),m)
  if not xmin<=pt[0]<=xmax or not ymin<=pt[1]<=ymax:return
  raw=''.join(v for c,v in e if c==3)+str(one(e,1,''));s=raw.replace('\\P',' ')
  s=__import__('re').sub(r'\\[A-Za-z][^;]*;','',s).replace('{','').replace('}','')
  if not s:return
  x,y=display(pt);height=num(e,40,200)*scale*math.hypot(m[0],m[1]);angle=-num(e,50)-math.degrees(math.atan2(m[1],m[0]))
  fragments.append(f'<text x="{x:.3f}" y="{y:.3f}" font-size="{height:.3f}" transform="rotate({angle:.3f},{x:.3f},{y:.3f})">{html.escape(s)}</text>')
 elif k not in ('SEQEND','POINT'):omitted[k]+=1
for e in es:render(e,[1,0,0,1,0,0])
meta={'status':'partial_source_preview_not_calibrated','window_world':window,'world_to_display':[scale,0,0,-scale,-xmin*scale,ymax*scale],'unit':'unverified CAD world units, not mm','rendered_primitives':len(fragments),'unsupported_or_approximation_counts_global':dict(omitted),'warnings':['Partial renderer omits hatch, spline and ellipse entities; polylines with bulges use chords','Text uses installed system CJK fallback; CAD fonts were missing','Display is for title/structure review only; not point placement or measurement','8F body title conflicts with 3F title block']}
svg=f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}px" height="{H}px" viewBox="0 0 {W} {H}"><title>8F source candidate - partial geometry review</title><metadata>{html.escape(json.dumps(meta,ensure_ascii=False))}</metadata><rect width="100%" height="100%" fill="white"/><defs><clipPath id="crop"><rect width="{W}" height="{H}"/></clipPath></defs><g clip-path="url(#crop)" fill="none" stroke="#000000" stroke-width="0.65">'+''.join(fragments)+'</g><style>text{stroke:none;fill:black;font-family:PingFang SC,Arial,sans-serif}</style></svg>'
(P/'8F_source_candidate_partial.svg').write_text(svg)
(P/'8F_render_limitations.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2))
print('Partial source SVG:',len(fragments),'primitives. Calibration and approvals remain pending.')

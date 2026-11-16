"""Read-only ASCII DXF inventory. Does not approve geometry or units."""
from pathlib import Path
import json, re, collections, csv
ROOT=Path(__file__).resolve().parents[1]
DXF=ROOT/'outputs/drawings/factory_converted.dxf'
OUT=ROOT/'outputs/drawings'
def decode(s):
    return re.sub(r'\\U\+([0-9A-Fa-f]{4})',lambda m:chr(int(m[1],16)),s)
def one(e,c,default=None):
    return next((v for k,v in e if k==c),default)
def num(e,c,default=0):
    try:return float(one(e,c,default))
    except (ValueError,TypeError):return default
def point(e,c):return [num(e,c),num(e,c+10),num(e,c+20)]
def records():
    with DXF.open(encoding='utf-8',errors='strict') as f:
        row=[]
        while True:
            a=f.readline()
            if not a:break
            b=f.readline().rstrip('\r\n')
            c=int(a.strip())
            if c==0 and row:
                yield row;row=[]
            row.append((c,decode(b)))
        if row:yield row
section='';counts=collections.Counter();layercounts=collections.Counter()
layers=[];styles=[];blocks={};entities=[];texts=[];dims=[];layouts=[];header={};blockname=None
for e in records():
    kind=one(e,0)
    if kind=='SECTION':
        section=one(e,2)
        if section=='HEADER':
            key=None
            for c,v in e:
                if c==9:key=v;header[key]=[]
                elif key:header[key].append([c,v])
        continue
    if kind=='ENDSEC':section='';continue
    if section=='HEADER':
        key=None
        for c,v in e:
            if c==9:key=v;header[key]=[]
            elif key:header[key].append([c,v])
    elif section=='TABLES':
        if kind=='LAYER':layers.append({'name':one(e,2),'flags':num(e,70),'color':num(e,62),'linetype':one(e,6)})
        elif kind=='STYLE':styles.append({'name':one(e,2),'font':one(e,3),'bigfont':one(e,4),'flags':num(e,70)})
    elif section=='BLOCKS':
        if kind=='BLOCK':
            blockname=one(e,2);blocks[blockname]={'base':point(e,10),'flags':int(num(e,70)),'xref_path':one(e,1),'entities':[]}
        elif kind=='ENDBLK':blockname=None
        elif blockname:blocks[blockname]['entities'].append(e)
    elif section=='OBJECTS' and kind=='LAYOUT':
        names=[v for c,v in e if c==1]
        layouts.append({'name':names[-1] if names else None,'handle':one(e,5),'tab_order':num(e,71),'all_names':[v for c,v in e if c in (1,2)]})
    elif section=='ENTITIES':
        counts[kind]+=1;layercounts[one(e,8,'0')]+=1;entities.append(e)
        if kind in ('TEXT','MTEXT','ATTRIB','ATTDEF'):
            s=''.join(v for c,v in e if c==3)+str(one(e,1,''))
            texts.append({'handle':one(e,5),'type':kind,'layer':one(e,8),'text':s,'position':point(e,10),'height':num(e,40),'rotation':num(e,50),'style':one(e,7)})
        if kind=='DIMENSION':
            p1=point(e,13);p2=point(e,14)
            dims.append({'handle':one(e,5),'layer':one(e,8),'label':one(e,1),'measurement':num(e,42,None),'definition_1':p1,'definition_2':p2,'position':point(e,10),'rotation':num(e,50),'type':int(num(e,70))%8,'block':one(e,2),'style':one(e,3)})
titlepat=re.compile(r'(?:[一二三四五六七八九十]|\d{1,2})\s*[层樓]|[1-9]\s*[Ff]|平面图|平面圖')
candidates=[t for t in texts if titlepat.search(t['text'])]
xrefs=[{'name':k,'flags':v['flags'],'path':v['xref_path']} for k,v in blocks.items() if v['flags']&12]
inventory={'source_drawing_sha256':'d368c39f3f5c9fdd2b783c8fc2949b6d1a744b03d5e9cafd172b17bc60a76918','converter':'Installed AutoCAD 2026 native Core Console','geometry_decoded':True,'geometry_status':'decoded_pending_font_and_unit_check','header':{k:header.get(k) for k in ['$ACADVER','$INSUNITS','$MEASUREMENT','$EXTMIN','$EXTMAX']},'entity_counts':dict(counts),'layer_entity_counts':dict(layercounts),'layers':layers,'styles':styles,'layouts':layouts,'block_count':len(blocks),'xref_blocks':xrefs,'text_count':len(texts),'dimension_count':len(dims),'title_candidates':candidates,'warnings':['Native CAD substituted missing fonts; see reports/mac_native_cad_export.txt','INSUNITS is not yet a verified physical unit','Model extents include very large or invalid Z; never use global extents as a floor crop','Block and layout inventory is not a floor identity mapping']}
for name,data in [('cad_inventory.json',inventory),('cad_texts.json',texts),('cad_dimensions.json',dims),('cad_entities.json',entities),('cad_blocks.json',blocks)]:
    (OUT/name).write_text(json.dumps(data,ensure_ascii=False,indent=2))
with (OUT/'title_candidates.csv').open('w',encoding='utf-8-sig',newline='') as f:
    w=csv.DictWriter(f,fieldnames=['handle','type','layer','text','position','height','rotation','style']);w.writeheader();w.writerows(candidates)
print(json.dumps({'entities':sum(counts.values()),'types':dict(counts),'layers':len(layers),'blocks':len(blocks),'xrefs':len(xrefs),'texts':len(texts),'dimensions':len(dims),'layouts':layouts,'title_candidates':candidates[:80]},ensure_ascii=False,indent=2))

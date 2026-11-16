#!/usr/bin/env python3
"""Local-only CAD intake. DWG requires an independently installed ODA converter."""
from __future__ import annotations
import argparse, hashlib, json, os, shutil, sys
from pathlib import Path
from collections import Counter
ROOT=Path(__file__).resolve().parents[1]


def inspect_header(path: Path):
    b=path.read_bytes()
    return {'file':str(path),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest(),
            'header_ascii':b[:6].decode('ascii',errors='replace'),
            'read_level':'header_only','geometry_decoded':False,'floor_count':None,
            'converter_in_path':shutil.which('ODAFileConverter'),
            'notice':'Header identification does not establish layout count, floor identity, units or geometry.'}


def protect_output(src: Path,dst: Path):
    if src.resolve()==dst.resolve(): raise ValueError('Refusing to overwrite input')
    if dst.resolve().is_relative_to((ROOT/'inputs').resolve()): raise ValueError('inputs/ is immutable')
    if dst.exists(): raise FileExistsError(f'Choose a new revision filename: {dst}')
    dst.parent.mkdir(parents=True,exist_ok=True)


def convert_dwg(src: Path,dst: Path,executable: str|None=None):
    if src.suffix.lower()!='.dwg' or dst.suffix.lower()!='.dxf': raise ValueError('Expected DWG input and new DXF output')
    protect_output(src,dst)
    try:
        import ezdxf
        from ezdxf.addons import odafc
    except ImportError as exc: raise RuntimeError('Install requirements-cad.txt in a local virtual environment first') from exc
    if executable:
        p=Path(executable).expanduser().resolve()
        if not p.is_file() or not os.access(p,os.X_OK): raise ValueError('ODA executable must be an existing executable file')
        key='win_exec_path' if sys.platform=='win32' else 'unix_exec_path'
        ezdxf.options.set('odafc-addon',key,str(p))
    if not odafc.is_installed():
        raise RuntimeError('ODA File Converter not found. Use an already licensed local CAD tool or install ODA with explicit permission. No geometry was generated.')
    before=hashlib.sha256(src.read_bytes()).hexdigest()
    # audit=False avoids silently repairing the conversion input; audit separately and report.
    odafc.convert(src,dst,version='R2018',audit=False,replace=False)
    if not dst.is_file() or not dst.stat().st_size: raise RuntimeError('Converter did not create a nonempty DXF')
    if before!=hashlib.sha256(src.read_bytes()).hexdigest(): raise RuntimeError('Source changed during conversion')
    # Confirm structure exists, not visual equivalence.
    doc=ezdxf.readfile(dst)
    receipt={'source_sha256':before,'output_sha256':hashlib.sha256(dst.read_bytes()).hexdigest(),
             'output':str(dst),'output_dxf_version':doc.dxfversion,
             'status':'converted_needs_native_CAD_visual_review','floor_mapping':'not_verified'}
    dst.with_suffix('.conversion.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n')
    return receipt


def inventory_dxf(path: Path):
    import ezdxf
    doc=ezdxf.readfile(path)
    layouts=[];texts=[];block_texts=[];limit=3000
    for layout in doc.layouts:
        counts=Counter();captured=0
        for e in layout:
            kind=e.dxftype();counts[kind]+=1
            if kind in ('TEXT','MTEXT','ATTRIB','ATTDEF'):
                txt=e.plain_text() if kind=='MTEXT' else e.dxf.get('text','')
                if len(texts)<limit:
                    at=e.dxf.get('insert',(0,0,0))
                    texts.append({'space':layout.name,'type':kind,'handle':e.dxf.handle,'layer':e.dxf.layer,
                                  'text':txt,'insert_raw':[float(v) for v in at],
                                  'coordinate_space':'entity_OCS_or_layout_space_NOT_verified_world',
                                  'extrusion_raw':[float(v) for v in e.dxf.get('extrusion',(0,0,1))]})
                    captured+=1
        layouts.append({'name':layout.name,'entity_counts':dict(counts),'total':sum(counts.values()),'captured_texts':captured})
    xrefs=[];blocks=[]
    for b in doc.blocks:
        flags=b.block.dxf.get('flags',0)
        if flags&4 or flags&8: xrefs.append({'name':b.name,'path':b.block.dxf.get('xref_path',''),'status':'needs_resolution_review'})
        blocks.append({'name':b.name,'entity_count':len(b),'flags':flags})
        for e in b:
            if e.dxftype() in ('TEXT','MTEXT','ATTDEF') and len(block_texts)<limit:
                txt=e.plain_text() if e.dxftype()=='MTEXT' else e.dxf.get('text','')
                block_texts.append({'block':b.name,'handle':e.dxf.handle,'text':txt,'coordinate_space':'block_definition_NOT_world'})
    return {'source':str(path),'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'dxf_version':doc.dxfversion,
            'insunits_raw':doc.header.get('$INSUNITS',0),'units_verified':False,
            'layouts':layouts,'layers':[{'name':l.dxf.name,'color':l.dxf.color,'flags':l.dxf.flags} for l in doc.layers],
            'fonts':[{'style':s.dxf.name,'font':s.dxf.get('font',''),'bigfont':s.dxf.get('bigfont',''),'availability':'not_checked'} for s in doc.styles],
            'blocks':blocks,'xrefs':xrefs,'text_entities':texts,'block_texts':block_texts,
            'text_capture_limit':limit,'text_capture_limit_reached':len(texts)>=limit or len(block_texts)>=limit,
            'floor_count':None,'floor_mapping':'not_verified','warning':'Layouts and block definitions are not floors. INSERT transforms, dependencies, proxy graphics and native CAD rendering must be checked before use.'}


def render_layout(path: Path,dst: Path,name: str):
    import ezdxf
    from ezdxf.addons.drawing import Frontend,RenderContext,layout,svg
    from ezdxf.addons.drawing.config import Configuration,ColorPolicy,BackgroundPolicy
    protect_output(path,dst)
    doc=ezdxf.readfile(path)
    if name not in doc.layouts.names(): raise ValueError(f'Unknown layout: {name}')
    out=svg.SVGBackend()
    conf=Configuration(color_policy=ColorPolicy.BLACK,background_policy=BackgroundPolicy.WHITE)
    Frontend(RenderContext(doc),out,config=conf).draw_layout(doc.layouts.get(name))
    dst.write_text(out.get_string(layout.Page(0,0)),encoding='utf-8')
    meta={'source_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'layout':name,'status':'preview_only',
          'units_verified':False,'world_to_svg':None,'notice':'Do not place or measure from this rendered SVG until its transform, fonts and geometry are checked.'}
    dst.with_suffix('.render.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2)+'\n')
    return meta


def main():
    p=argparse.ArgumentParser(description=__doc__);sub=p.add_subparsers(dest='command',required=True)
    a=sub.add_parser('inspect');a.add_argument('source',type=Path);a.add_argument('--out',type=Path)
    a=sub.add_parser('convert');a.add_argument('source',type=Path);a.add_argument('dest',type=Path);a.add_argument('--oda-executable')
    a=sub.add_parser('inventory');a.add_argument('source',type=Path);a.add_argument('--out',type=Path,required=True)
    a=sub.add_parser('render');a.add_argument('source',type=Path);a.add_argument('dest',type=Path);a.add_argument('--layout',required=True)
    args=p.parse_args()
    try:
        if args.command=='inspect': result=inspect_header(args.source)
        elif args.command=='convert': result=convert_dwg(args.source,args.dest,args.oda_executable)
        elif args.command=='inventory': result=inventory_dxf(args.source)
        else: result=render_layout(args.source,args.dest,args.layout)
        if getattr(args,'out',None):
            if args.out.resolve().is_relative_to((ROOT/'inputs').resolve()): raise ValueError('inputs/ is immutable')
            args.out.parent.mkdir(parents=True,exist_ok=True);args.out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
            print(args.out)
        else: print(json.dumps(result,ensure_ascii=False,indent=2))
        return 0
    except Exception as exc:
        print(f'CAD BLOCKED: {type(exc).__name__}: {exc}',file=sys.stderr);return 3

if __name__=='__main__': raise SystemExit(main())

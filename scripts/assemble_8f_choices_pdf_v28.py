#!/usr/bin/env python3
"""Assemble the visually checked 2x comparison pages into an A3 review PDF."""
import hashlib
import json
from pathlib import Path
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A3, landscape
from reportlab.lib.units import mm
from pypdf import PdfReader

root=Path(__file__).resolve().parents[1]
out=root/'交付_8楼/多方案选择_V2.8'
images=out/'逐项对比图'
files=[images/'cover-1.png',images/'cover-2.png']+[images/f'D{i:02}.png' for i in range(1,22)]
assert len(files)==23 and all(p.is_file() for p in files)
pdf=out/'output/pdf/BeePump_8F_Options_V2.8.pdf'
pdf.parent.mkdir(parents=True,exist_ok=True)
w,h=landscape(A3);margin=12*mm
c=canvas.Canvas(str(pdf),pagesize=(w,h),pageCompression=1)
c.setTitle('BeePump 8F Options V2.8 - Design preference review')
c.setSubject('23-page image-based review; editable text and vector templates are supplied in HTML/SVG. No production release.')
for p in files:
    c.drawImage(str(p),margin,margin,width=w-2*margin,height=h-2*margin,preserveAspectRatio=True,anchor='c')
    c.showPage()
c.save()
reader=PdfReader(str(pdf));assert len(reader.pages)==23
assert all(abs(float(p.mediabox.width)-w)<.1 and abs(float(p.mediabox.height)-h)<.1 for p in reader.pages)
record={'revision':'V2.8-OPTIONS-DRAFT','representation':'image_based_review_booklet; HTML/SVG remain editable','pages':23,'page_size':'A3 landscape','source_png_scale':2,'pdf_sha256':hashlib.sha256(pdf.read_bytes()).hexdigest(),'production_release':False,'source_pages':[{'file':str(p.relative_to(out)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in files]}
(root/'reports/options_v2.8/pdf_assembly.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'pdf':str(pdf),'pages':23,'bytes':pdf.stat().st_size,'sha256':record['pdf_sha256']}))

import os
import glob
from pypdf import PdfReader, PdfWriter, PageObject, Transformation
from pypdf.generic import FloatObject

out_path = os.path.join("output", "_Characters_Printable_Singles.pdf")
pdf_files = [f for f in glob.glob(os.path.join("output", "*.pdf")) if os.path.basename(f) != "_Characters_Printable.pdf"]

all_pages = []
for f in pdf_files:
    all_pages.extend(PdfReader(f).pages)

writer = PdfWriter()

for p in all_pages:
    new_page = PageObject.create_blank_page(width=612, height=792)
    
    w, h = float(p.mediabox.width), float(p.mediabox.height)
    s = min(612 / w, 396 / h)
    tx = (612 - (w * s)) / 2
    ty = 396 + (396 - (h * s)) / 2
    
    p.mediabox.lower_left = (0, 0)
    p.mediabox.upper_right = (612, 792)
    if "/CropBox" in p:
        p.cropbox.lower_left = (0, 0)
        p.cropbox.upper_right = (612, 792)
    
    p.add_transformation(Transformation().scale(s, s).translate(tx, ty))
    
    if "/Annots" in p:
        for a in p["/Annots"]:
            obj = a.get_object()
            if "/Rect" in obj:
                r = obj["/Rect"]
                for k in range(4):
                    r[k] = FloatObject(float(r[k]) * s + (tx if k % 2 == 0 else ty))
                    
    new_page.merge_page(p)
    writer.add_page(new_page)

with open(out_path, "wb") as f:
    writer.write(f)
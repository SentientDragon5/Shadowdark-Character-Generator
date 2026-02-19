import os
from pypdf import PdfReader, PdfWriter, PageObject, Transformation

def main():
    if not os.path.exists("output"):
        return
    
    files = [f for f in os.listdir("output") if f.endswith(".pdf") and f != "_Characters_Printable.pdf"]
    if not files:
        return

    pages = []
    for f in files:
        for p in PdfReader(os.path.join("output", f)).pages:
            pages.append(p)
            
    writer = PdfWriter()
    w, h, hh = 612.0, 792.0, 396.0
    
    for i in range(0, len(pages), 2):
        blank = PageObject.create_blank_page(width=w, height=h)
        
        p1 = pages[i]
        pw1, ph1 = float(p1.mediabox.width), float(p1.mediabox.height)
        s1 = min(w / pw1, hh / ph1)
        p1.add_transformation(Transformation().scale(s1, s1).translate((w - pw1 * s1) / 2, hh + (hh - ph1 * s1) / 2))
        blank.merge_page(p1)
        
        if i + 1 < len(pages):
            p2 = pages[i+1]
            pw2, ph2 = float(p2.mediabox.width), float(p2.mediabox.height)
            s2 = min(w / pw2, hh / ph2)
            p2.add_transformation(Transformation().scale(s2, s2).translate((w - pw2 * s2) / 2, (hh - ph2 * s2) / 2))
            blank.merge_page(p2)
            
        writer.add_page(blank)
        
    with open(os.path.join("output", "_Characters_Printable.pdf"), "wb") as out:
        writer.write(out)

if __name__ == "__main__":
    main()
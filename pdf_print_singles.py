import os
import glob
import json
import io
import textwrap
from pypdf import PdfReader, PdfWriter, PageObject, Transformation
from pypdf.generic import FloatObject
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

pdfmetrics.registerFont(TTFont('JBLACK', './fonts/JBLACK.TTF'))
pdfmetrics.registerFont(TTFont('OldNewsPaper', './fonts/Old Newspaper Font.ttf'))
pdfmetrics.registerFont(TTFont('Montserrat-Regular', './fonts/Montserrat-Regular.ttf'))

with open("spells.json", "r") as f:
    all_spells = json.load(f)["spells"]

with open("elixirs.json", "r") as f:
    all_elixirs = json.load(f)["elixirs"]

out_path = os.path.join("output", "_Characters_Printable_Singles.pdf")
pdf_files = [f for f in glob.glob(os.path.join("output", "*.pdf")) if not os.path.basename(f).startswith("_")]

writer = PdfWriter()

for f in pdf_files:
    json_path = f.replace("_Filled.pdf", ".json")
    char_spells_names = []
    char_elixir_names = []
    
    if os.path.exists(json_path):
        with open(json_path, 'r') as jf:
            cdata = json.load(jf)
            char_spells_names = cdata.get("spells", [])
            char_elixir_names = cdata.get("elixirs", [])
            for t in cdata.get("talents", []):
                if str(t).startswith("Spell: "):
                    char_spells_names.append(str(t).replace("Spell: ", ""))
                elif str(t).startswith("Recipe: "):
                    char_elixir_names.append(str(t).replace("Recipe: ", ""))
                    
    char_spells = [s for s in all_spells if s["name"] in char_spells_names]
    char_elixirs = [e for e in all_elixirs if e["name"] in char_elixir_names]

    reader = PdfReader(f)
    for p in reader.pages:
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

        if char_spells or char_elixirs:
            packet = io.BytesIO()
            c = canvas.Canvas(packet, pagesize=(612, 792))
            x, y = 30, 370
            
            if char_spells:
                c.setFont("JBLACK", 16)
                c.drawString(x, y, "Spells")
                y -= 20
                
                for spell in char_spells:
                    if y < 40:
                        x += 185
                        y = 370
                    
                    c.setFont("OldNewsPaper", 12)
                    c.drawString(x, y, spell['name'])
                    y -= 14
                    
                    c.setFont("Montserrat-Regular", 8)
                    text = f"(Tier {spell['tier']} {', '.join(spell['class'])}): {spell['description']}"
                    for line in textwrap.wrap(text, width=48):
                        if y < 30:
                            x += 185
                            y = 370
                        c.drawString(x, y, line)
                        y -= 10
                    y -= 8
            
            if char_elixirs:
                if y < 60:
                    x += 185
                    y = 370
                else:
                    y -= 10
                
                c.setFont("JBLACK", 16)
                c.drawString(x, y, "Elixirs")
                y -= 20
                
                for elixir in char_elixirs:
                    if y < 40:
                        x += 185
                        y = 370
                    
                    c.setFont("OldNewsPaper", 12)
                    c.drawString(x, y, elixir['name'])
                    y -= 14
                    
                    c.setFont("Montserrat-Regular", 8)
                    text = f"({elixir['type']} - {elixir['ingredient']}): {elixir['description']}"
                    for line in textwrap.wrap(text, width=48):
                        if y < 30:
                            x += 185
                            y = 370
                        c.drawString(x, y, line)
                        y -= 10
                    y -= 8
                    
            c.save()
            packet.seek(0)
            
            text_page = PdfReader(packet).pages[0]
            new_page.merge_page(text_page)
        
        writer.add_page(new_page)

with open(out_path, "wb") as out_f:
    writer.write(out_f)
import json
import os
import glob
import argparse
import io
from pypdf import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

def wrap_text(text, font_name, font_size, max_width):
    lines = []
    for paragraph in text.split('\n'):
        words = paragraph.split(' ')
        current_line = []
        for word in words:
            test_line = ' '.join(current_line + [word]) if current_line else word
            width = pdfmetrics.stringWidth(test_line, font_name, font_size)
            if width <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                    current_line = [word]
                else:
                    lines.append(word)
                    current_line = []
        if current_line:
            lines.append(' '.join(current_line))
    return lines

def get_fitting_font_size(text, font_name, start_size, max_width, max_height):
    size = start_size
    min_size = 4
    while size > min_size:
        lines = wrap_text(text, font_name, size, max_width)
        total_height = len(lines) * (size + 2)
        if total_height <= max_height:
            return size, lines
        size -= 0.5
    return min_size, wrap_text(text, font_name, min_size, max_width)

def generate_pdf(json_path, output_path):
    pdf_path = "ShadowDark Character Sheet Fillable.pdf"

    if not os.path.exists(json_path):
        raise FileNotFoundError(f"JSON missing: {json_path}")
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"PDF missing: {pdf_path}")

    with open(json_path, 'r') as f:
        data = json.load(f)

    font_path = './fonts/Montserrat-Regular.ttf'
    if os.path.exists(font_path):
        pdfmetrics.registerFont(TTFont('Montserrat', font_path))
        font_name = 'Montserrat'
    else:
        font_name = 'Helvetica'

    s = data.get("stats", {})
    attacks_list = [
        f"{atk.get('name', '')} | Atk: {atk.get('atk', '')} | Dmg: {atk.get('damage', '')} | {atk.get('range', '')}, {atk.get('properties', '')}".strip(" |,")
        for atk in data.get("attacks", [])
    ]

    ts = []
    talents = data.get("talents", [])
    spells = [str(t).replace("Spell: ", "") for t in talents if str(t).startswith("Spell: ")]
    recipes = [str(t).replace("Recipe: ", "") for t in talents if str(t).startswith("Recipe: ")]
    pure_talents = [t for t in talents if (not str(t).startswith("Spell: ") or not str(t).startswith("Recipe: "))]

    if pure_talents: ts.append(f"{', '.join(pure_talents)}\n")
    if spells: ts.append(f"{', '.join(spells)}\n")
    if recipes: ts.append(f"{', '.join(recipes)}\n")
    if data.get("languages"): ts.append(f"{', '.join(data['languages'])}\n")
    if data.get("traits"): ts.append(f"{', '.join(data['traits'])}\n")

    gold_val = float(data.get("gold", 0))
    total_cp = int(round(gold_val * 100))

    fields = {
        "Name": data.get("name", ""),
        "Race": data.get("ancestry", ""),
        "Class": data.get("class", ""),
        "Level": str(data.get("level", "")),
        "Title": data.get("title", ""),
        "Alignment": data.get("alignment", ""),
        "Background": data.get("background", ""),
        "Deity": data.get("deity", ""),
        "Hit Points": str(data.get("hp", {}).get("max", "")),
        "Armor Class": str(data.get("ac", "")),
        "Gold Pieces": str(total_cp // 100),
        "Silver Pieces": str((total_cp % 100) // 10),
        "Copper Pieces": str(total_cp % 10),
        "Talents / Spells": "".join(ts).strip(),
        "Attacks": "\n".join(attacks_list),
        "Free To Carry": "\n".join(data.get("free_to_carry", [])),
        "Strength Total": str(s.get("STR", {}).get("score", "")),
        "Strength Modifier": f"{s.get('STR', {}).get('modifier', 0):+}",
        "Dexterity Total": str(s.get("DEX", {}).get("score", "")),
        "Dexterity Modifier": f"{s.get('DEX', {}).get('modifier', 0):+}",
        "Constitution Total": str(s.get("CON", {}).get("score", "")),
        "Constitution Modifier": f"{s.get('CON', {}).get('modifier', 0):+}",
        "Intelligence Total": str(s.get("INT", {}).get("score", "")),
        "Intelligence Modifier": f"{s.get('INT', {}).get('modifier', 0):+}",
        "Wisdom Total": str(s.get("WIS", {}).get("score", "")),
        "Wisdom Modifier": f"{s.get('WIS', {}).get('modifier', 0):+}",
        "Charisma Total": str(s.get("CHA", {}).get("score", "")),
        "Charisma Modifier": f"{s.get('CHA', {}).get('modifier', 0):+}"
    }

    for i, item in enumerate(data.get("inventory", [])[:20], 1):
        fields[f"Gear {i}"] = item

    for i in range(data.get("max_inventory", 20) + 1, 21):
        fields[f"Gear {i}"] = "X"

    reader = PdfReader(pdf_path)
    writer = PdfWriter()
    page = reader.pages[0]

    packet = io.BytesIO()
    c = canvas.Canvas(packet, pagesize=(float(page.mediabox.width), float(page.mediabox.height)))

    if "/Annots" in page:
        for annot in page["/Annots"]:
            obj = annot.get_object()
            if "/T" in obj:
                field_name = obj["/T"]
                if field_name in fields:
                    val = str(fields[field_name])
                    rect = obj["/Rect"]
                    
                    da = obj.get("/DA", "")
                    initial_size = 10
                    if da:
                        da_str = da.get_object() if hasattr(da, "get_object") else da
                        parts = str(da_str).split()
                        if "Tf" in parts:
                            try:
                                initial_size = float(parts[parts.index("Tf") - 1])
                            except (ValueError, IndexError):
                                pass
                    
                    x = float(rect[0]) + 2
                    max_width = float(rect[2]) - float(rect[0]) - 4
                    max_height = float(rect[3]) - float(rect[1]) - 4
                    
                    actual_size, wrapped_lines = get_fitting_font_size(val, font_name, initial_size, max_width, max_height)
                    
                    y = float(rect[3]) - actual_size - 2
                    c.setFont(font_name, actual_size)
                    
                    for line in wrapped_lines:
                        c.drawString(x, y, line)
                        y -= (actual_size + 2)

    c.save()
    packet.seek(0)
    overlay = PdfReader(packet).pages[0]
    page.merge_page(overlay)
    
    if "/Annots" in page:
        del page["/Annots"]

    writer.add_page(page)

    with open(output_path, "wb") as f:
        writer.write(f)

def fill_sheet(filename):
    out_dir = "output"
    json_path = os.path.join(out_dir, f"{filename}.json")
    output_path = os.path.join(out_dir, f"{filename}_Filled.pdf")
    generate_pdf(json_path, output_path)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("json_path", type=str, nargs='?')
    parser.add_argument("--all", action="store_true")
    args = parser.parse_args()
    
    if args.all:
        for json_file in glob.glob("./output/*.json"):
            if os.path.basename(json_file).startswith("_"): continue
            generate_pdf(json_file, json_file.replace(".json", "_Filled.pdf"))
    elif args.json_path:
        generate_pdf(args.json_path, args.json_path.replace(".json", "_Filled.pdf"))
    else:
        parser.print_help()
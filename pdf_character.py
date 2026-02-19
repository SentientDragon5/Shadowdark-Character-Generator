import json
import os
from pypdf import PdfReader, PdfWriter
from pypdf.generic import NameObject

def fill_sheet(filename):
    out_dir = "output"
    json_path = os.path.join(out_dir, f"{filename}.json")
    pdf_path = "ShadowDark Character Sheet Fillable.pdf"
    output_path = os.path.join(out_dir, f"{filename}_Filled.pdf")

    if not os.path.exists(json_path) or not os.path.exists(pdf_path):
        return

    with open(json_path, 'r') as f:
        data = json.load(f)

    reader = PdfReader(pdf_path)
    writer = PdfWriter()
    writer.append_pages_from_reader(reader)

    if "/AcroForm" in reader.root_object:
        writer.root_object.update({
            NameObject("/AcroForm"): reader.root_object["/AcroForm"]
        })

    s = data.get("stats", {})

    attacks_list = []
    for atk in data.get("attacks", []):
        props = f"{atk.get('range', '')}, {atk.get('properties', '')}".strip(", ")
        attack_str = f"{atk.get('name', '')} | Atk: {atk.get('atk', '')} | Dmg: {atk.get('damage', '')} | {props}".strip(" |")
        attacks_list.append(attack_str)

    ts = []
    if data.get("talents"):
        ts.extend(["- Talents -"] + data["talents"])
    if data.get("languages"):
        ts.extend(["- Languages -"] + data["languages"])
    if data.get("traits"):
        ts.extend(["- Traits -"] + data["traits"])
    if data.get("proficiencies"):
        ts.append("- Proficiencies -")
        ts.extend([f"{k.capitalize()}: {v}" for k, v in data["proficiencies"].items()])

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
        "Gold Pieces": str(data.get("gold", "")),
        "Talents / Spells": "\n".join(ts),
        "Attacks": "\n".join(attacks_list),
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

    writer.update_page_form_field_values(writer.pages[0], fields)

    with open(output_path, "wb") as f:
        writer.write(f)

if __name__ == "__main__":
    pass
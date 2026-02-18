import json
import os
from pypdf import PdfReader, PdfWriter
from pypdf.generic import NameObject

def fill_sheet(filename):
    out_dir = "output"
    json_path = os.path.join(out_dir, f"{filename}.json")
    pdf_path = "ShadowDark Character Sheet Fillable.pdf"
    output_path = os.path.join(out_dir, f"{filename}_Filled.pdf")

    with open(json_path, 'r') as f:
        data = json.load(f)

    reader = PdfReader(pdf_path)
    writer = PdfWriter()
    writer.append_pages_from_reader(reader)
    
    if "/AcroForm" in reader.root_object:
        writer.root_object.update({
            NameObject("/AcroForm"): reader.root_object["/AcroForm"]
        })

    s = data["stats"]
    fields = {
        "Name": data["name"],
        "Race": data["ancestry"],
        "Class": data["class"],
        "Level": str(data["level"]),
        "Title": data["title"],
        "Alignment": data["alignment"],
        "Background": data["background"],
        "Deity": data["deity"],
        "Hit Points": str(data["hp"]["max"]),
        "Armor Class": str(data["ac"]),
        "Gold Pieces": str(data["gold"]),
        "Talents / Spells": "\n".join(data["talents"]),
        "Strength Total": str(s["STR"]["score"]),
        "Strength Modifier": f"{s['STR']['modifier']:+}",
        "Dexterity Total": str(s["DEX"]["score"]),
        "Dexterity Modifier": f"{s['DEX']['modifier']:+}",
        "Constitution Total": str(s["CON"]["score"]),
        "Constitution Modifier": f"{s['CON']['modifier']:+}",
        "Intelligence Total": str(s["INT"]["score"]),
        "Intelligence Modifier": f"{s['INT']['modifier']:+}",
        "Wisdom Total": str(s["WIS"]["score"]),
        "Wisdom Modifier": f"{s['WIS']['modifier']:+}",
        "Charisma Total": str(s["CHA"]["score"]),
        "Charisma Modifier": f"{s['CHA']['modifier']:+}"
    }

    for i, item in enumerate(data["inventory"][:20], 1):
        fields[f"Gear {i}"] = item

    writer.update_page_form_field_values(writer.pages[0], fields)

    with open(output_path, "wb") as f:
        writer.write(f)

if __name__ == "__main__":
    fill_sheet("Brielle_Fighter_1")
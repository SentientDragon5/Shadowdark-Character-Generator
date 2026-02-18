import json
import os
from pypdf import PdfReader, PdfWriter
from pypdf.generic import NameObject

def fill_sheet(filename):
    out_dir = "output"
    json_path = os.path.join(out_dir, f"{filename}.json")
    pdf_path = "ShadowDark Character Sheet Fillable.pdf"
    output_path = os.path.join(out_dir, f"{filename}_Filled.pdf")

    if not os.path.exists(json_path):
        print(f"Error: JSON file not found at {json_path}")
        return
    if not os.path.exists(pdf_path):
        print(f"Error: PDF template not found at {pdf_path}")
        return

    with open(json_path, 'r') as f:
        data = json.load(f)

    reader = PdfReader(pdf_path)
    writer = PdfWriter()
    writer.append_pages_from_reader(reader)

    # Preserve AcroForm
    if "/AcroForm" in reader.root_object:
        writer.root_object.update({
            NameObject("/AcroForm"): reader.root_object["/AcroForm"]
        })

    s = data["stats"]

    # 1. Base Fields
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

    # 2. Inventory (Gear 1, Gear 2, etc.)
    for i, item in enumerate(data["inventory"][:20], 1):
        fields[f"Gear {i}"] = item

    # 3. Attacks Mapping
    # Maps internal keys to standard Shadowdark PDF field names.
    attacks = data.get("attacks", [])
    
    # We loop through the first 4 attacks (standard sheet limit)
    for i, atk in enumerate(attacks[:4], 1):
        # Construct the property string (Range + Properties)
        props = f"{atk['range']}, {atk['properties']}".strip(", ")
        
        # Standard field names often found in these PDFs
        fields[f"Weapon {i}"] = atk['name']
        fields[f"Atk Bonus {i}"] = atk['atk']
        fields[f"Damage {i}"] = atk['damage']
        fields[f"Properties {i}"] = props

    writer.update_page_form_field_values(writer.pages[0], fields)

    with open(output_path, "wb") as f:
        writer.write(f)
        
    print(f"PDF created: {output_path}")

if __name__ == "__main__":
    pass
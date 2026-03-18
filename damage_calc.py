import json
import os
import re
import argparse
import glob
import matplotlib.pyplot as plt

def roll_avg(die_str, level=1):
    if not die_str: return 0
    die_str = die_str.replace("(HL)", str(max(1, level // 2))).replace("(LV)", str(level))
    parts = re.findall(r'(\d+)d(\d+)', die_str)
    avg = sum(int(n) * (int(s) + 1) / 2 for n, s in parts)
    flat = re.search(r'([+-])(\d+)(?!d)', die_str)
    if flat:
        op, val = flat.groups()
        avg = avg + int(val) if op == '+' else avg - int(val)
    elif not parts and re.match(r'^\d+$', die_str):
        avg = int(die_str)
    return avg

def calculate_dpr(atk, target_ac, target_save_mod):
    avg_dmg = roll_avg(atk.get("damage", "1d4"), atk.get("level", 1))
    is_spell = atk.get("type") == "spell_save" or "dc" in atk
    
    if is_spell:
        dc = int(atk.get("dc", 12))
        needed = max(1, min(20, dc - target_save_mod))
        fail_chance = (needed - 1) / 20.0
        return (fail_chance * avg_dmg) + ((1.0 - fail_chance) * (avg_dmg * 0.5))
    else:
        atk_mod = int(str(atk.get("atk", "+0")).replace("+", ""))
        needed = max(2, min(20, target_ac - atk_mod))
        hit_chance = (21 - needed) / 20.0
        if "advantage" in atk.get("description", "").lower():
            hit_chance = 1 - (1 - hit_chance)**2
        return hit_chance * avg_dmg

def get_damage_sources(char_data, spell_db, elixir_db):
    sources = []
    level = char_data.get("level", 1)
    
    # 1. Weapons
    for atk in char_data.get("attacks", []):
        atk["level"] = level
        sources.append(atk)
        
    # 2. Spells (from spells list or talents)
    spell_names = char_data.get("spells", [])
    for t in char_data.get("talents", []):
        if str(t).startswith("Spell: "): spell_names.append(t.replace("Spell: ", ""))
            
    for name in spell_names:
        if name in spell_db:
            s = spell_db[name].copy()
            dmg_match = re.search(r'(\d+d\d+)', s.get("description", ""))
            if dmg_match:
                s["damage"] = dmg_match.group(1)
                s["type"] = "spell_save"
                mod = char_data["stats"]["INT"]["modifier"] if "wizard" in s["class"] else char_data["stats"]["WIS"]["modifier"]
                s["dc"] = 10 + mod
                s["level"] = level
                sources.append(s)

    # 3. Elixirs
    elixir_names = []
    for t in char_data.get("talents", []):
        if str(t).startswith("Recipe: "): elixir_names.append(t.replace("Recipe: ", ""))
            
    for name in elixir_names:
        if name in elixir_db:
            e = elixir_db[name].copy()
            dmg_match = re.search(r'(\d+d\d+)', e.get("description", "").replace("(HL)", "1").replace("(LV)", "1"))
            if dmg_match:
                e["damage"] = e["description"].split("deal ")[1].split(" ")[0] if "deal " in e["description"] else dmg_match.group(1)
                e["atk"] = char_data["stats"]["DEX"]["modifier"]
                e["level"] = level
                sources.append(e)
                
    return sources

def process_stats(paths):
    spell_db = {s["name"]: s for s in (json.load(open("spells.json"))["spells"] if os.path.exists("spells.json") else [])}
    elixir_db = {e["name"]: e for e in (json.load(open("elixirs.json"))["elixirs"] if os.path.exists("elixirs.json") else [])}
    
    target_range = list(range(10, 23))
    all_stats = []
    
    # Identify all sources first to determine the total count for colors
    all_sources = []
    for path in paths:
        if "damage_stats.json" in path: continue
        with open(path, 'r') as f:
            data = json.load(f)
            char_sources = get_damage_sources(data, spell_db, elixir_db)
            all_sources.append((data, char_sources))

    total_plots = sum(len(srcs) for _, srcs in all_sources)
    
    # Use a colormap to generate unique colors
    # 'nipy_spectral' or 'gist_rainbow' are good for 20+ unique lines
    colormap = plt.cm.get_cmap('nipy_spectral', total_plots)
    color_idx = 0

    plt.figure(figsize=(12, 7))

    for data, sources in all_sources:
        char_entry = {"name": data["name"], "class": data["class"], "level": data["level"], "outputs": []}
        
        for src in sources:
            dpr_series = [calculate_dpr(src, val, val - 10) for val in target_range]
            char_entry["outputs"].append({
                "label": src["name"],
                "avg_dmg": roll_avg(src.get("damage"), data["level"]),
                "dpr": dict(zip(target_range, [round(d, 2) for d in dpr_series]))
            })
            
            # Apply the unique color from the colormap
            plt.plot(target_range, dpr_series, marker='o', 
                     label=f"{data['name']}: {src['name']}", 
                     color=colormap(color_idx))
            color_idx += 1
        
        all_stats.append(char_entry)

    with open("output/damage_stats.json", "w") as f:
        json.dump(all_stats, f, indent=2)

    plt.title("Expected Damage vs. Target Difficulty (AC/Saves)")
    plt.xlabel("Enemy AC (Save Bonus = AC - 10)")
    plt.ylabel("Damage Per Turn")
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.tight_layout()
    plt.savefig("output/damage_chart.png")
    plt.show()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--all", action="store_true")
    args = parser.parse_args()
    files = glob.glob("output/*.json") if args.all else []
    if files: process_stats(files)
import json
import random
import os
import importlib
import argparse
import pdf_character

def roll(n, d): return sum(random.randint(1, d) for _ in range(n))

def get_mod(score):
    if score >= 18: return 4
    if score >= 16: return 3
    if score >= 14: return 2
    if score >= 12: return 1
    if score >= 10: return 0
    if score >= 8: return -1
    if score >= 6: return -2
    if score >= 4: return -3
    return -4

def load_json(path):
    try:
        with open(path, 'r') as f: return json.load(f)
    except FileNotFoundError: return {}

def calculate_ac(character, gear_data):
    inventory = character.get('inventory', [])
    dex_mod = character['stats']['DEX']['modifier']
    talents = character.get('talents', [])
    armor_lookup = {item['item']: item for item in gear_data.get('armor', [])}
    
    best_base_ac = 10 + dex_mod
    bonus_ac = 0
    
    for item_name in inventory:
        if item_name in armor_lookup:
            effect = armor_lookup[item_name].get('ac_effect', '')
            if effect.startswith("+"): bonus_ac += int(effect)
            else:
                current = 0
                if "DEX" in effect:
                    base = int(effect.split('+')[0].strip())
                    current = base + dex_mod
                else:
                    try: current = int(effect.strip())
                    except: pass
                if current > best_base_ac: best_base_ac = current

    for t in talents:
        if "+1 AC" in t: bonus_ac += 1
    return best_base_ac + bonus_ac

def ensure_backpack(character):
    if len(character['inventory']) > 2 and "Backpack" not in character['inventory']:
        character['inventory'].append("Backpack")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-l", "--level", type=int, default=1)
    parser.add_argument("-c", "--class", type=str, dest="char_class", default=None)
    parser.add_argument("-a", "--ancestry", type=str, default=None)
    args = parser.parse_args()
    target_level = max(1, min(10, args.level))

    available_classes = ['fighter', 'priest', 'wizard', 'thief']
    if args.char_class:
        c = args.char_class.lower()
        if c in ['p', 'priest']: chosen_class = 'priest'
        elif c in ['f', 'fighter']: chosen_class = 'fighter'
        elif c in ['w', 'wizard']: chosen_class = 'wizard'
        elif c in ['t', 'thief']: chosen_class = 'thief'
        else: chosen_class = random.choice(available_classes)
    else:
        chosen_class = random.choice(available_classes)

    available_ancestries = ['Human', 'Elf', 'Dwarf', 'Halfling', 'Half-Orc', 'Goblin']
    ancestry_map = {
        'hu': 'Human', 'human': 'Human',
        'e': 'Elf', 'elf': 'Elf',
        'd': 'Dwarf', 'dwarf': 'Dwarf',
        'ha': 'Halfling', 'halfling': 'Halfling',
        'ho': 'Half-Orc', 'half-orc': 'Half-Orc', 'halforc': 'Half-Orc',
        'g': 'Goblin', 'goblin': 'Goblin'
    }
    
    if args.ancestry:
        a = args.ancestry.lower()
        ancestry = ancestry_map.get(a, random.choice(available_ancestries))
    else:
        ancestry = random.choice(available_ancestries)

    gear_data = load_json('gear.json')
    names_data = load_json('names.json')
    deities_data = load_json('deities.json')
    backgrounds_data = load_json('backgrounds.json')
    
    stats_keys = ['STR', 'DEX', 'CON', 'INT', 'WIS', 'CHA']
    stats = {k: roll(3, 6) for k in stats_keys}
    mods = {k: get_mod(v) for k, v in stats.items()}
    
    name_key = ancestry.lower().replace('-', '_')
    names = names_data.get('names', {}).get(name_key, ["Unknown"])
    name = random.choice(names)

    alignments = ['Lawful', 'Neutral', 'Chaotic']
    align = random.choice(alignments)
    valid_deities = [d['name'] for d in deities_data.get('deities', []) if d.get('alignment') == align]
    deity = random.choice(valid_deities) if valid_deities else "None"
    
    bg_list = backgrounds_data.get('backgrounds', [])
    bg = random.choice(bg_list) if bg_list else "Unknown"

    character = {
        "name": name, "ancestry": ancestry, "class": "", "level": target_level,
        "title": "", "alignment": align, "background": bg, "deity": deity,
        "stats": {k: {"score": stats[k], "modifier": mods[k]} for k in stats_keys},
        "hp": {"max": 0, "current": 0}, "ac": 10, "languages": ["Common"],
        "traits": [], "talents": [], "spells": [], "inventory": [], "attacks": [], "gold": 0
    }

    try:
        mod = importlib.import_module(f"ancestry.{name_key}")
        mod.apply_effects(character)
    except Exception:
        pass

    class_mod = importlib.import_module(f"classes.{chosen_class}")
    class_mod.apply_effects(character, gear_data)

    character['gold'] = roll(2, 6) * 5
    basic_gear = gear_data.get('basic_gear', [])
    if basic_gear:
        count = roll(1, 6) + (target_level - 1)
        for _ in range(count):
            character['inventory'].append(random.choice(basic_gear)['item'])

    ensure_backpack(character)
    character['ac'] = calculate_ac(character, gear_data)
    
    max_inv = max(10, character['stats']['STR']['score'])
    if any("Hauler" in t for t in character.get('traits', [])):
        con_mod = character['stats']['CON']['modifier']
        if con_mod > 0: max_inv += con_mod
    character['max_inventory'] = max_inv
    
    os.makedirs('output', exist_ok=True)
    file_base = f"{character['name']}_{character['class']}_{character['level']}"
    json_path = f"output/{file_base}.json"
    
    with open(json_path, 'w') as f: 
        json.dump(character, f, indent=2)
    print(f"JSON created: {json_path}")
    
    pdf_character.fill_sheet(file_base)

if __name__ == "__main__": 
    main()
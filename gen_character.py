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

def get_cost_cp(cost_str):
    try:
        a, u = cost_str.lower().split()
        return int(a) * {'gp': 100, 'sp': 10, 'cp': 1}.get(u, 0)
    except: return 0

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

def roll_stats():
    stats_keys = ['STR', 'DEX', 'CON', 'INT', 'WIS', 'CHA']
    stats = {k: roll(3, 6) for k in stats_keys}
    mods = {k: get_mod(v) for k, v in stats.items()}
    return stats, mods

def create_base_character(name, ancestry, chosen_class, level, align, bg, deity, stats, mods):
    return {
        "name": name, "ancestry": ancestry, "class": chosen_class, "level": level,
        "title": "", "alignment": align, "background": bg, "deity": deity,
        "stats": {k: {"score": stats[k], "modifier": mods[k]} for k in stats.keys()},
        "hp": {"max": 0, "current": 0}, "ac": 10, "languages": ["Common"],
        "traits": [], "talents": [], "spells": [], "inventory": [], "free_to_carry": [], "attacks": [], "gold": 0
    }

def apply_ancestry_and_class(character, gear_data):
    name_key = character['ancestry'].lower().replace('-', '_')
    chosen_class = character['class'].lower()
    
    try:
        mod = importlib.import_module(f"ancestry.{name_key}")
        mod.apply_effects(character)
    except Exception:
        pass

    try:
        class_mod = importlib.import_module(f"classes.{chosen_class}")
        class_mod.apply_effects(character, gear_data)
    except Exception:
        pass

def finalize_inventory_and_ac(character, gear_data, funds_cp):
    character['gold'] = round(funds_cp / 100, 2)

    if len(character['inventory']) > 2 and "Backpack" not in character['inventory']:
        character['inventory'].append("Backpack")

    if "Backpack" in character['inventory']:
        character['inventory'].remove("Backpack")
        character['free_to_carry'].append("Backpack")

    for tool in ["Thieves' tools", "Thieves tools", "Thieves' Tools"]:
        if tool in character['inventory']:
            character['inventory'].remove(tool)
            character['free_to_carry'].append(tool)
    
    extra_coins = max(0, int(character['gold']) - 100)
    coin_slots = (extra_coins + 99) // 100
    for _ in range(coin_slots):
        character['inventory'].append("100 Coins")

    character['ac'] = calculate_ac(character, gear_data)
    
    max_inv = max(10, character['stats']['STR']['score'])
    if any("Hauler" in t for t in character.get('traits', [])):
        con_mod = character['stats']['CON']['modifier']
        if con_mod > 0: max_inv += con_mod
    character['max_inventory'] = max_inv

def save_character(character):
    os.makedirs('output', exist_ok=True)
    file_base = f"{character['name']}_{character['class']}_{character['level']}"
    json_path = f"output/{file_base}.json"
    
    with open(json_path, 'w') as f: 
        json.dump(character, f, indent=2)
    print(f"JSON created: {json_path}")
    
    pdf_character.fill_sheet(file_base)

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-l", "--level", type=int, default=1)
    parser.add_argument("-c", "--class", type=str, dest="char_class", default=None)
    parser.add_argument("-a", "--ancestry", type=str, default=None)
    parser.add_argument("-q", "--quantity", type=int, default=1)
    args = parser.parse_args()
    
    target_level = max(1, min(10, args.level))
    quantity = max(1, args.quantity)
    
    chosen_class = None
    if args.char_class:
        c = args.char_class.lower()
        if c in ['p', 'priest']: chosen_class = 'priest'
        elif c in ['f', 'fighter']: chosen_class = 'fighter'
        elif c in ['w', 'wizard']: chosen_class = 'wizard'
        elif c in ['t', 'thief']: chosen_class = 'thief'

    ancestry = None
    if args.ancestry:
        a = args.ancestry.lower()
        ancestry_map = {
            'hu': 'Human', 'human': 'Human',
            'e': 'Elf', 'elf': 'Elf',
            'd': 'Dwarf', 'dwarf': 'Dwarf',
            'ha': 'Halfling', 'halfling': 'Halfling',
            'ho': 'Half-Orc', 'half-orc': 'Half-Orc', 'halforc': 'Half-Orc',
            'g': 'Goblin', 'goblin': 'Goblin'
        }
        ancestry = ancestry_map.get(a)
        
    return target_level, chosen_class, ancestry, quantity
import json
import random
import os
import importlib
import argparse

# Import the class module directly
import classes.fighter as fighter_class
import pdf_character

def roll(n, d):
    return sum(random.randint(1, d) for _ in range(n))

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
        with open(path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: Could not find {path}")
        return {}

def calculate_ac(character, gear_data):
    """
    Calculates AC based on inventory (armor/shields), DEX mod, and Talents.
    """
    inventory = character.get('inventory', [])
    dex_mod = character['stats']['DEX']['modifier']
    talents = character.get('talents', [])
    
    armor_lookup = {item['item']: item for item in gear_data.get('armor', [])}
    
    best_base_ac = 10 + dex_mod
    bonus_ac = 0
    
    for item_name in inventory:
        if item_name in armor_lookup:
            effect = armor_lookup[item_name].get('ac_effect', '')
            if effect.startswith("+"):
                bonus_ac += int(effect)
            else:
                current_armor_ac = 0
                if "DEX" in effect:
                    base_val = int(effect.split('+')[0].strip())
                    current_armor_ac = base_val + dex_mod
                else:
                    try:
                        current_armor_ac = int(effect.strip())
                    except ValueError:
                        pass
                if current_armor_ac > best_base_ac:
                    best_base_ac = current_armor_ac

    talent_bonus = 0
    for t in talents:
        if "+1 AC" in t:
            talent_bonus += 1

    return best_base_ac + bonus_ac + talent_bonus

def ensure_backpack(character):
    inventory = character.get('inventory', [])
    if len(inventory) > 2 and "Backpack" not in inventory:
        inventory.append("Backpack")
        character['inventory'] = inventory

def main():
    # --- ARGUMENT PARSING ---
    parser = argparse.ArgumentParser(description="Generate a random Shadowdark character.")
    parser.add_argument("--level", type=int, default=1, help="Level of the character (default: 1)")
    args = parser.parse_args()
    target_level = max(1, min(10, args.level)) # Clamp level between 1 and 10

    # --- 1. LOAD DATA ---
    gear_data = load_json('gear.json')
    names_data = load_json('names.json')
    deities_data = load_json('deities.json')
    backgrounds_data = load_json('backgrounds.json')
    
    # --- 2. STATS --- [cite: 181-199]
    stats_keys = ['STR', 'DEX', 'CON', 'INT', 'WIS', 'CHA']
    stats = {k: roll(3, 6) for k in stats_keys}
    mods = {k: get_mod(v) for k, v in stats.items()}
    
    # --- 3. ANCESTRY & NAME --- [cite: 201-230, 424]
    ancestries = ['Human', 'Elf', 'Dwarf', 'Halfling', 'Half-Orc', 'Goblin']
    ancestry_name = random.choice(ancestries)
    
    name_key = ancestry_name.lower().replace('-', '_')
    available_names = names_data.get('names', {}).get(name_key, ["Unknown"])
    name = random.choice(available_names)

    # --- 4. ALIGNMENT --- [cite: 323-338]
    alignments = ['Lawful', 'Neutral', 'Chaotic']
    alignment = random.choice(alignments)
    
    # --- 5. DEITY --- [cite: 346-373]
    valid_deities = [
        d['name'] for d in deities_data.get('deities', []) 
        if d.get('alignment') == alignment
    ]
    deity = random.choice(valid_deities) if valid_deities else "None"

    # --- 6. BACKGROUND --- [cite: 175-180]
    background_list = backgrounds_data.get('backgrounds', [])
    background = random.choice(background_list) if background_list else "Unknown"

    # --- 7. INITIALIZE CHARACTER OBJECT ---
    character = {
        "name": name,
        "ancestry": ancestry_name,
        "class": "", 
        "level": target_level,
        "title": "",
        "alignment": alignment,
        "background": background,
        "deity": deity,
        "stats": {k: {"score": stats[k], "modifier": mods[k]} for k in stats_keys},
        "hp": {"max": 0, "current": 0},
        "ac": 10,
        "languages": ["Common"],
        "traits": [],
        "talents": [],
        "inventory": [],
        "gold": 0
    }

    # --- 8. APPLY ANCESTRY EFFECTS --- [cite: 201-230]
    try:
        ancestry_module = importlib.import_module(f"ancestries.{name_key}")
        ancestry_module.apply_effects(character)
    except ImportError:
        print(f"Warning: Could not load ancestry module for {ancestry_name}")

    # --- 9. APPLY CLASS (FIGHTER) --- [cite: 231-245]
    fighter_class.apply_effects(character)

    # --- 10. GOLD & RANDOM GEAR --- [cite: 172, 1100-1102]
    # Gold scales slightly with level for realism in this generator (house rule for higher level starts),
    # or strictly stick to rules: "2d6 x 5 gold pieces" is for starting (Level 1).
    # We will stick to the base rule but maybe give them more gear rolls.
    character['gold'] = roll(2, 6) * 5
    
    basic_gear_list = gear_data.get('basic_gear', [])
    if basic_gear_list:
        # Higher levels might have accumulated more junk
        num_random_items = roll(1, 6) + (target_level - 1)
        for _ in range(num_random_items):
            item = random.choice(basic_gear_list)
            character['inventory'].append(item['item'])

    # --- 11. POST-GENERATION CHECKS ---
    ensure_backpack(character)
    character['ac'] = calculate_ac(character, gear_data)

    # --- 12. OUTPUT ---
    os.makedirs('output', exist_ok=True)
    file_base = f"{character['name']}_{character['class']}_{character['level']}"
    json_filename = f"output/{file_base}.json"
    
    with open(json_filename, 'w') as f:
        json.dump(character, f, indent=2)
    
    print(f"JSON Character created: {json_filename}")
    
    print("Generating PDF...")
    pdf_character.fill_sheet(file_base)

if __name__ == "__main__":
    main()
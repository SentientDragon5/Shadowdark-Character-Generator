import json
import random
import os
import datetime
import importlib

# Helper Functions
def roll(n, d):
    return sum(random.randint(1, d) for _ in range(n))

def roll_advantage(n, d):
    roll1 = roll(n, d)
    roll2 = roll(n, d)
    return max(roll1, roll2)

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

def parse_talent(roll_val, table):
    for entry in table:
        r = entry['roll']
        if '-' in r:
            low, high = map(int, r.split('-'))
            if low <= roll_val <= high:
                return entry['effect']
        elif int(r) == roll_val:
            return entry['effect']
    return table[-1]['effect']

def main():
    # Load Data
    gear_data = load_json('gear.json')
    fighter_data = load_json('classes/fighter.json')
    names_data = load_json('names.json')
    
    if not fighter_data or not names_data:
        return

    # --- STATS ---
    stats_keys = ['STR', 'DEX', 'CON', 'INT', 'WIS', 'CHA']
    stats = {k: roll(3, 6) for k in stats_keys}
    mods = {k: get_mod(v) for k, v in stats.items()}
    
    # --- ANCESTRY SELECTION ---
    ancestries = ['Human', 'Elf', 'Dwarf', 'Halfling', 'Half-Orc', 'Goblin']
    ancestry_name = random.choice(ancestries)
    
    # Name Selection
    name_key = ancestry_name.lower().replace('-', '_')
    available_names = names_data.get('names', {}).get(name_key, ["Unknown"])
    name = random.choice(available_names)

    # --- BASE CHARACTER OBJECT ---
    character = {
        "name": name,
        "ancestry": ancestry_name,
        "class": fighter_data.get('class_name', 'Fighter'),
        "level": 1,
        "title": "Warrior",
        "alignment": "",
        "background": "",
        "deity": "",
        "stats": {k: {"score": stats[k], "modifier": mods[k]} for k in stats_keys},
        "hp": {"max": 0, "current": 0},
        "ac": 10 + mods['DEX'],
        "languages": ["Common"],
        "traits": [],
        "talents": [],
        "inventory": [],
        "gold": 0
    }

    # --- APPLY ANCESTRY EFFECTS ---
    # Dynamically import the correct ancestry module
    try:
        # Assuming files are in a folder named 'ancestries' with an __init__.py
        ancestry_module = importlib.import_module(f"ancestries.{name_key}")
        ancestry_module.apply_effects(character)
    except ImportError as e:
        print(f"Warning: Could not load ancestry module for {ancestry_name}. {e}")

    # --- HIT POINTS ---
    # [cite_start]Fighter uses d8[cite: 235]. 
    # Dwarf 'Stout' trait (advantage) is applied here logic-wise
    hp_die_str = fighter_data.get('hit_points', '1d8')
    hp_die = int(hp_die_str.split('d')[1].split()[0])
    
    if ancestry_name == 'Dwarf':
        raw_hp = roll_advantage(1, hp_die) # [cite: 205]
    else:
        raw_hp = roll(1, hp_die)

    final_hp = max(1, raw_hp + mods['CON'])
    
    # Add to existing HP (Dwarf module might have already added +2)
    character['hp']['max'] += final_hp
    character['hp']['current'] += final_hp

    # --- TALENTS ---
    # [cite_start]Human 'Ambitious' trait gives +1 roll [cite: 229]
    talent_rolls = 2 if ancestry_name == 'Human' else 1
    
    for _ in range(talent_rolls):
        r = roll(2, 6)
        effect = parse_talent(r, fighter_data.get('talent_table', []))
        character['talents'].append(effect)
        
    # --- CLASS FEATURES ---
    class_features = fighter_data.get('features', [])
    for feature in class_features:
        if feature['name'] == 'Weapon Mastery':
             weapons = ["Bastard sword", "Greataxe", "Greatsword", "Longsword", "Shortsword", "Warhammer"]
             character['talents'].append(f"Weapon Mastery: {random.choice(weapons)}")
        elif feature['name'] == 'Grit':
             character['talents'].append(f"Grit: {random.choice(['Strength', 'Dexterity'])}")
        else:
             character['talents'].append(f"{feature['name']}: {feature['effect']}")

    # --- ALIGNMENT & DEITY ---
    alignments = ['Lawful', 'Neutral', 'Chaotic']
    character['alignment'] = random.choice(alignments)
    
    deities = {
        'Lawful': ['Saint Terragnis', 'Madeera the Covenant'],
        'Neutral': ['Gede', 'Ord'],
        'Chaotic': ['Memnon', 'Shune the Vile', 'Ramlaat']
    }
    character['deity'] = random.choice(deities[character['alignment']])

    # --- TITLE ---
    # [cite_start]Determine Title based on alignment [cite: 314]
    for t in fighter_data.get('titles', []):
        if t['level'] == '1-2':
            character['title'] = t.get(character['alignment'].lower(), "Warrior")
            break

    # --- BACKGROUND ---
    backgrounds = [
        "Urchin", "Wanted", "Cult Initiate", "Thieves' Guild", "Banished", 
        "Orphaned", "Wizard's Apprentice", "Jeweler", "Herbalist", "Barbarian", 
        "Mercenary", "Sailor", "Acolyte", "Soldier", "Ranger", "Scout", 
        "Minstrel", "Scholar", "Noble", "Chirurgeon"
    ]
    character['background'] = random.choice(backgrounds)

    # --- GEAR ---
    character['gold'] = roll(2, 6) * 5
    
    # Starting Fighter Gear
    character['inventory'].append("Leather armor")
    character['inventory'].append(random.choice(["Longsword", "Greataxe", "Mace", "Shortsword"]))
    
    # Random Gear (1d6 items)
    gear_list = gear_data.get('basic_gear', [])
    if gear_list:
        num_random_items = roll(1, 6)
        for _ in range(num_random_items):
            item = random.choice(gear_list)
            character['inventory'].append(item['item'])

    # --- OUTPUT ---
    os.makedirs('output', exist_ok=True)
    filename = f"output/{character['name']}_{character['class']}_{character['level']}.json"
    
    with open(filename, 'w') as f:
        json.dump(character, f, indent=2)
    
    print(f"Character created: {filename}")

if __name__ == "__main__":
    main()
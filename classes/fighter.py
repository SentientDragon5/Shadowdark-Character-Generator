import random

CLASS_DATA = {
    "name": "Fighter",
    "description": "Blood-soaked gladiators in dented armor, acrobatic duelists with darting swords, or far-eyed elven archers.",
    "hit_dice": "1d8",
    "proficiencies": { "weapons": "All weapons", "armor": "All armor and shields" },
    "titles": [
        {"level": "1-2", "lawful": "Squire", "chaotic": "Knave", "neutral": "Warrior"},
        {"level": "3-4", "lawful": "Cavalier", "chaotic": "Bandit", "neutral": "Barbarian"},
        {"level": "5-6", "lawful": "Knight", "chaotic": "Slayer", "neutral": "Battlerager"},
        {"level": "7-8", "lawful": "Thane", "chaotic": "Reaver", "neutral": "Warchief"},
        {"level": "9-10", "lawful": "Lord/Lady", "chaotic": "Warlord", "neutral": "Chieftain"}
    ],
    "talent_table": [
        {"range": (2, 2), "effect": "Gain Weapon Mastery with one additional weapon type"},
        {"range": (3, 6), "effect": "+1 to melee and ranged attacks"},
        {"range": (7, 9), "effect": "+2 to Strength, Dexterity, or Constitution stat"},
        {"range": (10, 11), "effect": "Choose one kind of armor. You get +1 AC from that armor"},
        {"range": (12, 12), "effect": "Choose a talent or +2 points to distribute to stats"}
    ]
}

def roll_talent():
    roll = random.randint(1, 6) + random.randint(1, 6)
    for entry in CLASS_DATA['talent_table']:
        low, high = entry['range']
        if low <= roll <= high:
            return f"Talent (Roll {roll}): {entry['effect']}"
    return f"Talent (Roll {roll}): +1 to melee and ranged attacks" 

def get_title(level, alignment):
    alignment_key = alignment.lower()
    for entry in CLASS_DATA['titles']:
        low, high = map(int, entry['level'].split('-'))
        if low <= level <= high:
            return entry.get(alignment_key, "Warrior")
    return "Warrior"

def calculate_attack_bonus(weapon, character, gear_data):
    """Calculates to-hit and damage bonuses."""
    name = weapon['item']
    w_type = weapon.get('type', 'M') # M or R
    props = weapon.get('properties', '')
    
    str_mod = character['stats']['STR']['modifier']
    dex_mod = character['stats']['DEX']['modifier']
    level = character['level']
    traits = character.get('traits', [])
    talents = character.get('talents', [])
    
    # 1. Base Attribute Mod [cite: 1820-1823]
    # Finesse (F) uses higher of STR/DEX
    if "F" in props: 
        attr_mod = max(str_mod, dex_mod)
    elif w_type == 'R':
        attr_mod = dex_mod
    else:
        attr_mod = str_mod

    hit_bonus = attr_mod
    dmg_bonus = attr_mod # Damage typically adds same mod in Shadowdark (simplified)

    # 2. Weapon Mastery 
    # "+1 to attack and damage... add half your level to these rolls"
    # We check if the specific weapon name is in the mastery trait string
    is_master = False
    for t in traits:
        if "Weapon Mastery" in t and name in t:
            is_master = True
            break
            
    if is_master:
        mastery_bonus = 1 + (level // 2)
        hit_bonus += mastery_bonus
        dmg_bonus += mastery_bonus

    # 3. Mighty (Half-Orc) 
    # "+1 bonus to attack and damage rolls with melee weapons"
    if w_type == 'M' and any("Mighty" in t for t in traits):
        hit_bonus += 1
        dmg_bonus += 1

    # 4. Talents (Generic +1)
    # Check talents for "+1 to melee and ranged attacks"
    talent_hit_bonus = 0
    for t in talents:
        if "+1 to melee and ranged attacks" in t:
            talent_hit_bonus += 1
    hit_bonus += talent_hit_bonus
    # Note: Talent usually only says "attacks", implies hit, not damage.

    return hit_bonus, dmg_bonus

def apply_effects(character, gear_data):
    level = character['level']
    
    # Basic Class Info
    character['class'] = CLASS_DATA['name']
    character['proficiencies'] = CLASS_DATA['proficiencies']

    # HP Calculation
    con_mod = character['stats']['CON']['modifier']
    is_stout = any("Stout" in t for t in character.get('traits', []))
    total_hp = 0
    for i in range(1, level + 1):
        roll = random.randint(1, 8)
        if is_stout: roll = max(roll, random.randint(1, 8))
        total_hp += max(1, roll + con_mod)
    character['hp']['max'] += total_hp
    character['hp']['current'] += total_hp

    # Features
    if "Hauler" not in character['traits']:
        character['traits'].append("Hauler: Add CON mod (if positive) to gear slots")
    
    weapons_list = gear_data.get('weapons', [])
    if not weapons_list:
        print("Error: No weapons found in gear_data")
        return

    # Weapon Mastery Selection
    if not any("Weapon Mastery" in t for t in character['traits']):
        # Filter for weapons Fighter likely uses
        fighter_weapons = [w['item'] for w in weapons_list] 
        mastery_weapon = random.choice(fighter_weapons)
        character['traits'].append(f"Weapon Mastery: {mastery_weapon} (+1 atk/dmg + half lvl)")

    if "Grit" not in character['traits']:
        grit = random.choice(["Strength", "Dexterity"])
        character['traits'].append(f"Grit: Advantage on {grit} checks")

    # Talents
    talent_count = sum(1 for i in range(1, level + 1) if i % 2 != 0)
    if any("Ambitious" in t for t in character.get('traits', [])):
        talent_count += 1
    for _ in range(talent_count):
        character['talents'].append(roll_talent())

    # Titles
    character['title'] = get_title(level, character['alignment'])

    # Inventory & Attacks
    if "Leather armor" not in character['inventory']:
        character['inventory'].append("Leather armor")

    # Ensure character has their mastery weapon
    mastery_trait = next((t for t in character['traits'] if "Weapon Mastery" in t), "")
    has_weapon = False
    
    # 1. Identify Mastery Weapon Name
    # Extract "Bastard sword" from "Weapon Mastery: Bastard sword (+1..."
    m_name = ""
    if mastery_trait:
        try:
            m_name = mastery_trait.split(':')[1].split('(')[0].strip()
        except:
            pass

    # 2. Add to inventory if missing
    if m_name and m_name not in character['inventory']:
        character['inventory'].append(m_name)

    # 3. Generate Attack Objects for all weapons in inventory
    # Look up weapon data from gear_data
    weapon_lookup = {w['item']: w for w in weapons_list}
    
    for item_name in character['inventory']:
        if item_name in weapon_lookup:
            w_data = weapon_lookup[item_name]
            hit, dmg_mod = calculate_attack_bonus(w_data, character, gear_data)
            
            sign = "+" if hit >= 0 else ""
            dmg_sign = "+" if dmg_mod >= 0 else ""
            
            atk_obj = {
                "name": item_name,
                "atk": f"{sign}{hit}",
                "damage": f"{w_data['damage']}{dmg_sign}{dmg_mod}",
                "range": w_data['range'],
                "properties": w_data['properties']
            }
            character['attacks'].append(atk_obj)
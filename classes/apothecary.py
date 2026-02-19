import random

CLASS_DATA = {
    "name": "Apothecary",
    "description": "Miraculous doctors, mad scientists, or jolly craftsmen who brew elixirs to support their allies or harm their foes.",
    "hit_dice": "1d4",
    "proficiencies": { "weapons": "Club, dagger, staff, crossbow, blowgun, thrown elixirs", "armor": "Leather armor, mithral chainmail" },
    "titles": [
        {"level": "1-2", "lawful": "Chirurgeon", "chaotic": "Thistler", "neutral": "Brewer"},
        {"level": "3-4", "lawful": "Philterist", "chaotic": "Mortifier", "neutral": "Distiller"},
        {"level": "5-6", "lawful": "Purifier", "chaotic": "Toxicant", "neutral": "Potionwright"},
        {"level": "7-8", "lawful": "Balmist", "chaotic": "Baneweaver", "neutral": "Sublimator"},
        {"level": "9-10", "lawful": "Vitalist", "chaotic": "Miasmist", "neutral": "Savant"}
    ],
    "talent_table": [
        {"range": (2, 2), "effect": "Gain advantage on brewing checks for one elixir you know the recipe for"},
        {"range": (3, 6), "effect": "Learn one additional recipe"},
        {"range": (7, 9), "effect": "+2 to Dexterity or Intelligence stat"},
        {"range": (10, 11), "effect": "+1 to brewing checks or to melee and ranged attacks"},
        {"range": (12, 12), "effect": "Choose a talent or +2 points to distribute to stats"}
    ],
    "recipes": [
        "Healing Elixir", "Sealeskin Elixir", "Invisibility Elixir", 
        "Explosive Vial", "Acid Vial", "Alchemical Fire"
    ]
}

def roll_talent():
    roll = random.randint(1, 6) + random.randint(1, 6)
    for entry in CLASS_DATA['talent_table']:
        low, high = entry['range']
        if low <= roll <= high:
            return f"Talent (Roll {roll}): {entry['effect']}"
    return f"Talent (Roll {roll}): Learn one additional recipe"

def get_title(level, alignment):
    alignment_key = alignment.lower()
    for entry in CLASS_DATA['titles']:
        low, high = map(int, entry['level'].split('-'))
        if low <= level <= high:
            return entry.get(alignment_key, "Brewer")
    return "Brewer"

def calculate_attack_bonus(weapon, character, gear_data):
    w_type = weapon.get('type', 'M')
    props = weapon.get('properties', '')
    
    str_mod = character['stats']['STR']['modifier']
    dex_mod = character['stats']['DEX']['modifier']
    traits = character.get('traits', [])
    talents = character.get('talents', [])
    
    if "F" in props: 
        attr_mod = max(str_mod, dex_mod)
    elif w_type == 'R':
        attr_mod = dex_mod
    else:
        attr_mod = str_mod

    hit_bonus = attr_mod
    dmg_bonus = attr_mod

    if w_type == 'M' and any("Mighty" in t for t in traits):
        hit_bonus += 1
        dmg_bonus += 1

    talent_hit_bonus = 0
    for t in talents:
        if "+1 to brewing checks or to melee and ranged attacks" in t:
            talent_hit_bonus += 1
    hit_bonus += talent_hit_bonus

    return hit_bonus, dmg_bonus

def apply_effects(character, gear_data):
    level = character['level']
    character['class'] = CLASS_DATA['name']
    character['proficiencies'] = CLASS_DATA['proficiencies']

    con_mod = character['stats']['CON']['modifier']
    is_stout = any("Stout" in t for t in character.get('traits', []))
    total_hp = 0
    for i in range(1, level + 1):
        roll = random.randint(1, 4)
        if is_stout: roll = max(roll, random.randint(1, 4))
        total_hp += max(1, roll + con_mod)
    character['hp']['max'] += total_hp
    character['hp']['current'] += total_hp

    reagents_count = 2 + level
    character['traits'].append(f"Versatile Reagents ({reagents_count}/rest)")
    character['traits'].append("Quick Brew")
    character['traits'].append("Forager (Advantage)")

    talent_count = sum(1 for i in range(1, level + 1) if i % 2 != 0)
    if any("Ambitious" in t for t in character.get('traits', [])):
        talent_count += 1
    for _ in range(talent_count):
        character['talents'].append(roll_talent())

    recipe_count = 2
    for l in [3, 5, 7, 9]:
        if level >= l:
            recipe_count += 1
            
    for t in character['talents']:
        if "Learn one additional recipe" in t:
            recipe_count += 1
            
    known_recipes = random.sample(CLASS_DATA['recipes'], min(recipe_count, len(CLASS_DATA['recipes'])))
    for r in known_recipes:
        character['talents'].append(f"Recipe: {r}")

    if "Leather armor" not in character['inventory']:
        character['inventory'].append("Leather armor")

    character['title'] = get_title(level, character['alignment'])

    weapons_list = gear_data.get('weapons', [])
    if not weapons_list:
        return

    weapon_lookup = {w['item']: w for w in weapons_list}
    has_weapon = any(item in weapon_lookup for item in character['inventory'])
    if not has_weapon:
        character['inventory'].append(random.choice(["Dagger", "Club", "Staff"]))

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
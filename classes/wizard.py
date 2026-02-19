import random

CLASS_DATA = {
    "name": "Wizard",
    "description": "Rune-tattooed adepts, bespectacled magi, and flame-conjuring witches who dare to manipulate the fell forces of magic.",
    "hit_dice": "1d4",
    "proficiencies": { "weapons": "Dagger, staff", "armor": "None" },
    "titles": [
        {"level": "1-2", "lawful": "Apprentice", "chaotic": "Adept", "neutral": "Shaman"},
        {"level": "3-4", "lawful": "Conjurer", "chaotic": "Channeler", "neutral": "Seer"},
        {"level": "5-6", "lawful": "Arcanist", "chaotic": "Witch/Warlock", "neutral": "Warden"},
        {"level": "7-8", "lawful": "Mage", "chaotic": "Diabolist", "neutral": "Sage"},
        {"level": "9-10", "lawful": "Archmage", "chaotic": "Sorcerer", "neutral": "Druid"}
    ],
    "talent_table": [
        {"range": (2, 2), "effect": "Make one random magic item"},
        {"range": (3, 7), "effect": "+2 to Intelligence stat or +1 to wizard spellcasting checks"},
        {"range": (8, 9), "effect": "Gain advantage on casting one spell you know"},
        {"range": (10, 11), "effect": "Learn one additional wizard spell of any tier you know"},
        {"range": (12, 12), "effect": "Choose a talent or +2 points to distribute to stats"}
    ]
}

def roll_talent():
    roll = random.randint(1, 6) + random.randint(1, 6)
    for entry in CLASS_DATA['talent_table']:
        low, high = entry['range']
        if low <= roll <= high:
            return f"Talent (Roll {roll}): {entry['effect']}"
    return f"Talent (Roll {roll}): +2 to Intelligence stat or +1 to wizard spellcasting checks"

def get_title(level, alignment):
    alignment_key = alignment.lower()
    for entry in CLASS_DATA['titles']:
        low, high = map(int, entry['level'].split('-'))
        if low <= level <= high:
            return entry.get(alignment_key, "Apprentice")
    return "Apprentice"

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
        if "+1 to melee or ranged attacks" in t:
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

    common_langs = ["Dwarvish", "Elf", "Giant", "Goblin", "Merran", "Orcish", "Reptilian", "Sylvan", "Thanian"]
    rare_langs = ["Celestial", "Diabolic", "Draconic", "Primordial"]
    
    if "languages" not in character:
        character["languages"] = ["Common"]
        
    new_commons = random.sample([l for l in common_langs if l not in character["languages"]], 2)
    character["languages"].extend(new_commons)
    
    new_rares = random.sample([l for l in rare_langs if l not in character["languages"]], 2)
    character["languages"].extend(new_rares)

    character["languages"] = list(set(character["languages"]))

    tier_1_spells = ["Alarm", "Burning Hands", "Charm Person", "Detect Magic", "Feather Fall", "Floating Disk", "Hold Portal", "Light", "Mage Armor", "Magic Missile", "Protection From Evil", "Sleep"]
    known_spells = random.sample(tier_1_spells, 3)
    if "spells" not in character:
        character["spells"] = []
    for spell in known_spells:
        character['spells'].append(f"{spell}")

    talent_count = sum(1 for i in range(1, level + 1) if i % 2 != 0)
    if any("Ambitious" in t for t in character.get('traits', [])):
        talent_count += 1
    for _ in range(talent_count):
        character['talents'].append(roll_talent())

    character['title'] = get_title(level, character['alignment'])

    weapons_list = gear_data.get('weapons', [])
    if not weapons_list:
        return

    weapon_lookup = {w['item']: w for w in weapons_list}
    has_weapon = any(item in weapon_lookup for item in character['inventory'])
    if not has_weapon:
        character['inventory'].append(random.choice(["Dagger", "Staff"]))

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
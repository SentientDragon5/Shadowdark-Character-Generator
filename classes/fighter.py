import random

# Fighter Class Data
CLASS_DATA = {
    "name": "Fighter",
    "description": "Blood-soaked gladiators in dented armor, acrobatic duelists with darting swords, or far-eyed elven archers.",
    "hit_dice": "1d8",
    "proficiencies": {
        "weapons": "All weapons",
        "armor": "All armor and shields"
    },
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
    """Rolls on the Fighter talent table (2d6)."""
    roll = random.randint(1, 6) + random.randint(1, 6)
    for entry in CLASS_DATA['talent_table']:
        low, high = entry['range']
        if low <= roll <= high:
            return f"Talent (Roll {roll}): {entry['effect']}"
    return f"Talent (Roll {roll}): +1 to melee and ranged attacks" 

def get_title(level, alignment):
    """Finds the title for the specific level and alignment."""
    alignment_key = alignment.lower()
    for entry in CLASS_DATA['titles']:
        # Parse range "1-2" -> [1, 2]
        low, high = map(int, entry['level'].split('-'))
        if low <= level <= high:
            return entry.get(alignment_key, "Warrior")
    return "Warrior" # Fallback

def apply_effects(character):
    """Applies Fighter class features, HP, talents, and starting gear based on Level."""
    level = character['level']
    
    # 1. Basic Class Info
    character['class'] = CLASS_DATA['name']
    character['proficiencies'] = CLASS_DATA['proficiencies']

    # 2. Hit Points
    # Level 1: 1d8 + CON
    # Level 2+: +1d8 per level (Ref: Level Advancement)
    con_mod = character['stats']['CON']['modifier']
    
    # Check for Dwarf 'Stout' trait (Advantage on HP rolls)
    is_stout = any("Stout" in t for t in character.get('traits', []))
    
    total_hp = 0
    for i in range(1, level + 1):
        roll = random.randint(1, 8)
        if is_stout:
            roll = max(roll, random.randint(1, 8))
        
        # Minimum 1 HP gain per level
        level_hp = max(1, roll + con_mod)
        total_hp += level_hp

    character['hp']['max'] += total_hp
    character['hp']['current'] += total_hp

    # 3. Class Features
    if "Hauler" not in character['traits']:
        character['traits'].append("Hauler: Add CON mod (if positive) to gear slots")
    
    # Weapon Mastery (Only at level 1, unless Talent adds more)
    weapons = ["Bastard sword", "Greataxe", "Greatsword", "Longsword", "Shortsword", "Warhammer", "Longbow", "Crossbow"]
    if not any("Weapon Mastery" in t for t in character['traits']):
        mastery = random.choice(weapons)
        character['traits'].append(f"Weapon Mastery: +1 attack/damage with {mastery}, add half level to rolls")
    
    if "Grit" not in character['traits']:
        grit_stat = random.choice(["Strength", "Dexterity"])
        character['traits'].append(f"Grit: Advantage on {grit_stat} checks to overcome opposing force")

    # 4. Talents
    # Talents are gained at levels 1, 3, 5, 7, 9 (Ref: Advancement Table)
    # Human 'Ambitious' trait adds +1 at Level 1.
    
    talent_count = 0
    
    # Check advancement table
    for i in range(1, level + 1):
        # Levels 1, 3, 5, 7, 9 grant a talent
        if i % 2 != 0: 
            talent_count += 1
            
    if any("Ambitious" in t for t in character.get('traits', [])):
        talent_count += 1
        
    for _ in range(talent_count):
        character['talents'].append(roll_talent())

    # 5. Titles
    character['title'] = get_title(level, character['alignment'])

    # 6. Starting Gear (Level 1 only logic, but kept for higher levels as base kit)
    if "Leather armor" not in character['inventory']:
        character['inventory'].append("Leather armor")
    
    # Ensure mastery weapon is present (simplified check)
    has_weapon = False
    for item in character['inventory']:
        if item in weapons:
            has_weapon = True
            break
    if not has_weapon:
         character['inventory'].append(random.choice(weapons))
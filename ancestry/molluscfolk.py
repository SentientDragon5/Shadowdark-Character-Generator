import random

def apply_effects(character):
    character['languages'].append("Merran")
    if random.choice(["gear", "ac"]) == "gear":
        character['traits'].append("Adaptable: +3 gear slots, swim at normal speed, breathe underwater")
    else:
        character['traits'].append("Adaptable: +1 AC, swim at normal speed, breathe underwater")
        character['talents'].append("+1 AC")
import random

def apply_effects(character):
    """
    Applies Elf ancestry effects:
    - [cite_start]Languages: Common, Elvish, Sylvan [cite: 208]
    - [cite_start]Farsight: +1 bonus to attack rolls with ranged weapons or +1 spellcasting checks. [cite: 209]
    """
    character['languages'].extend(["Elvish", "Sylvan"])
    
    # Farsight: Randomly choose between ranged or spellcasting bonus
    bonus = random.choice(["ranged weapons", "spellcasting checks"])
    character['traits'].append(f"Farsight: +1 bonus to {bonus}")
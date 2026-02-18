import random

def apply_effects(character):
    """
    Applies Dwarf ancestry effects:
    - Languages: Common, Dwarvish
    - Stout: Start with +2 HP. Roll hit points per level with advantage.
    """
    character['languages'].append("Dwarvish")
    
    # Stout: +2 HP
    character['hp']['max'] += 2
    character['hp']['current'] += 2
    
    # Note: The advantage on HP roll is handled here by re-rolling if the generator
    # didn't already do it, or we simply add a note for future levels.
    # For Level 1, we assume the generator passed a base roll. 
    # To simulate advantage for the base level 1 die:
    # We roll again and take the higher of the current base (minus Con/bonuses) vs new roll.
    # However, to keep it simple and safe with the passed object, we will just add the trait.
    
    character['traits'].append("Stout: +2 HP, Roll HP with advantage")
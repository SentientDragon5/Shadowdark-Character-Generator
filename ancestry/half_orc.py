def apply_effects(character):
    """
    Applies Half-Orc ancestry effects:
    - [cite_start]Languages: Common, Orcish [cite: 224]
    - [cite_start]Mighty: +1 bonus to attack and damage rolls with melee weapons. [cite: 225]
    """
    character['languages'].append("Orcish")
    character['traits'].append("Mighty: +1 attack/damage with melee weapons")
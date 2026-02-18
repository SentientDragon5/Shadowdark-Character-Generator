def apply_effects(character):
    """
    Applies Goblin ancestry effects:
    - [cite_start]Languages: Common, Goblin [cite: 212]
    - [cite_start]Keen Senses: You can't be surprised. [cite: 213]
    """
    character['languages'].append("Goblin")
    character['traits'].append("Keen Senses: You can't be surprised")
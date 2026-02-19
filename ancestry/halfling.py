def apply_effects(character):
    """
    Applies Halfling ancestry effects:
    - [cite_start]Languages: Common [cite: 217]
    - [cite_start]Stealthy: Once per day, you can become invisible for 3 rounds. [cite: 218]
    """
    # Halflings only know Common by default, which is already in the base.
    character['traits'].append("Stealthy: Once per day, become invisible for 3 rounds")
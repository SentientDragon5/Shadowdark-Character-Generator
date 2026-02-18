import random

def apply_effects(character):
    """
    Applies Human ancestry effects:
    - [cite_start]Languages: Common + one additional common language [cite: 228]
    - [cite_start]Ambitious: Gain one additional talent roll at 1st level. [cite: 229]
    """
    # [cite_start]Common Languages list [cite: 340]
    common_languages = [
        "Dwarvish", "Elvish", "Giant", "Goblin", "Merran", 
        "Orcish", "Reptilian", "Sylvan", "Thanian"
    ]
    
    extra_lang = random.choice(common_languages)
    character['languages'].append(extra_lang)
    
    character['traits'].append("Ambitious: +1 talent roll at 1st level")
    
    # Note: The actual rolling of the extra talent happens in the main generator 
    # or needs to be triggered here if we pass the talent table.
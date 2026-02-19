import random
import gen_character

def main():
    target_level, user_class, user_ancestry, quantity = gen_character.parse_args()

    gear_data = gen_character.load_json('gear.json')
    names_data = gen_character.load_json('names.json')
    deities_data = gen_character.load_json('deities.json')
    backgrounds_data = gen_character.load_json('backgrounds.json')

    classes = ['fighter', 'priest', 'wizard', 'thief']
    ancestries = ['Human', 'Elf', 'Dwarf', 'Halfling', 'Half-Orc', 'Goblin']
    alignments = ['Lawful', 'Neutral', 'Chaotic']

    for _ in range(quantity):
        chosen_class = user_class if user_class else random.choice(classes)
        ancestry = user_ancestry if user_ancestry else random.choice(ancestries)
        align = random.choice(alignments)

        stats, mods = gen_character.roll_stats()

        name_key = ancestry.lower().replace('-', '_')
        names = names_data.get('names', {}).get(name_key, ["Unknown"])
        name = random.choice(names)

        valid_deities = [d['name'] for d in deities_data.get('deities', []) if d.get('alignment') == align]
        deity = random.choice(valid_deities) if valid_deities else "None"

        bg_list = backgrounds_data.get('backgrounds', [])
        bg = random.choice(bg_list) if bg_list else "Unknown"

        character = gen_character.create_base_character(
            name, ancestry, chosen_class, target_level, align, bg, deity, stats, mods
        )

        gen_character.apply_ancestry_and_class(character, gear_data)

        starting_gold = gen_character.roll(2, 6) * 5
        funds_cp = starting_gold * 100

        basic_gear = gear_data.get('basic_gear', [])
        if basic_gear:
            count = gen_character.roll(1, 6) + (target_level - 1)
            for _ in range(count):
                item = random.choice(basic_gear)
                cost_cp = gen_character.get_cost_cp(item['cost'])
                if funds_cp >= cost_cp:
                    funds_cp -= cost_cp
                    character['inventory'].append(item['item'])

        gen_character.finalize_inventory_and_ac(character, gear_data, funds_cp)
        gen_character.save_character(character)

if __name__ == "__main__":
    main()
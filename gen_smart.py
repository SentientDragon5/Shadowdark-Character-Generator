import random
import gen_character

def main():
    target_level, user_class, user_ancestry, quantity = gen_character.parse_args()

    gear_data = gen_character.load_json('gear.json')
    names_data = gen_character.load_json('names.json')
    deities_data = gen_character.load_json('deities.json')
    backgrounds_data = gen_character.load_json('backgrounds.json')

    for _ in range(quantity):
        stats, mods = gen_character.roll_stats()
        while max(stats.values()) < 15:
            stats, mods = gen_character.roll_stats()

        if user_class:
            chosen_class = user_class
        else:
            best_stat = max(stats, key=lambda k: stats[k])
            if best_stat == 'STR': chosen_class = 'fighter'
            elif best_stat == 'INT': chosen_class = 'wizard'
            elif best_stat == 'WIS': chosen_class = 'priest'
            elif best_stat == 'DEX': chosen_class = 'thief'
            else: chosen_class = 'fighter'

        if user_ancestry:
            ancestry = user_ancestry
        else:
            if chosen_class == 'fighter': ancestry = random.choice(['Dwarf', 'Half-Orc', 'Human'])
            elif chosen_class == 'wizard': ancestry = random.choice(['Elf', 'Human'])
            elif chosen_class == 'priest': ancestry = random.choice(['Dwarf', 'Human'])
            elif chosen_class == 'thief': ancestry = random.choice(['Halfling', 'Goblin', 'Human'])
            else: ancestry = 'Human'

        alignments = ['Lawful', 'Neutral', 'Chaotic']
        align = random.choice(alignments)

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

        item_costs = {}
        for cat in ['basic_gear', 'armor', 'weapons']:
            for item in gear_data.get(cat, []):
                item_costs[item['item']] = gen_character.get_cost_cp(item['cost'])

        priority_list = ["Backpack", "Rations (3)"]
        if chosen_class == 'fighter':
            if stats['STR'] >= stats['DEX']:
                priority_list += ["Chainmail", "Shield", "Longsword", "Leather armor", "Bastard sword"]
            else:
                priority_list += ["Leather armor", "Longbow", "Arrows (20)", "Shortsword"]
        elif chosen_class == 'priest':
            priority_list += ["Chainmail", "Shield", "Mace", "Leather armor", "Warhammer"]
        elif chosen_class == 'thief':
            priority_list += ["Leather armor", "Shortsword", "Shortbow", "Arrows (20)"]
        elif chosen_class == 'wizard':
            priority_list += ["Staff", "Dagger"]
        
        priority_list += ["Flint and steel", "Torch", "Torch", "Rope, 60'", "Grappling hook", "Crowbar", "Mirror"]

        for item_name in priority_list:
            if item_name in item_costs:
                cost = item_costs[item_name]
                if funds_cp >= cost:
                    if item_name in ["Chainmail", "Leather armor", "Plate mail"] and any(a in character['inventory'] for a in ["Chainmail", "Leather armor", "Plate mail"]):
                        continue
                    funds_cp -= cost
                    character['inventory'].append(item_name)

        if chosen_class == 'thief' and funds_cp >= 500:
            funds_cp -= 500
            character['inventory'].append("Thieves' tools")

        gen_character.finalize_inventory_and_ac(character, gear_data, funds_cp)
        gen_character.save_character(character)

if __name__ == "__main__":
    main()
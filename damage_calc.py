import json
import os
import re
import argparse
import glob
import matplotlib.pyplot as plt

def roll_avg(die_str):
    parts = re.findall(r'(\d+)d(\d+)', die_str)
    avg = sum(int(n) * (int(s) + 1) / 2 for n, s in parts)
    flat = re.search(r'([+-])(\d+)(?!d)', die_str)
    if flat:
        op, val = flat.groups()
        avg = avg + int(val) if op == '+' else avg - int(val)
    return avg

def get_char_data(json_path):
    with open(json_path, 'r') as f:
        data = json.load(f)
    
    char_name = data.get("name", "Unknown")
    target_acs = list(range(10, 23))
    attack_curves = []

    for atk in data.get("attacks", []):
        atk_mod = int(atk.get("atk", "+0").replace("+", ""))
        avg_dmg = roll_avg(atk.get("damage", "1d4"))
        
        dpr_series = []
        for ac in target_acs:
            chance = max(0.05, min(0.95, (21 - (ac - atk_mod)) / 20.0))
            dpr_series.append(chance * avg_dmg)
            
        label = f"{char_name}: {atk.get('name')}"
        attack_curves.append((label, dpr_series))
        
    return target_acs, attack_curves

def plot_stats(all_paths):
    plt.figure(figsize=(10, 6))
    target_acs = range(10, 23)

    for path in all_paths:
        acs, curves = get_char_data(path)
        for label, dpr_values in curves:
            plt.plot(acs, dpr_values, marker='o', label=label)

    plt.title("Damage Per Round (DPR) vs. Enemy Armor Class", fontsize=14)
    plt.xlabel("Enemy Armor Class (AC)", fontsize=12)
    plt.ylabel("Expected DPR", fontsize=12)
    plt.xticks(range(10, 23))
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.legend()
    plt.tight_layout()
    
    print("Displaying chart...")
    plt.show()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("json_path", type=str, nargs='?')
    parser.add_argument("--all", action="store_true")
    args = parser.parse_args()

    paths = glob.glob(os.path.join("output", "*.json")) if args.all else ([args.json_path] if args.json_path else [])
    
    if paths:
        plot_stats(paths)
    else:
        print("Please provide a JSON path or use --all to scan the output directory.")
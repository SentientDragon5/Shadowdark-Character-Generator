import json, os, re, argparse, glob
import matplotlib.pyplot as plt

def get_die_stats(die_str, level=1):
    if not die_str: return 0, 0, 0
    s = die_str.replace("(HL)", str(max(1, level // 2))).replace("(LV)", str(level))
    parts = re.findall(r'(\d+)d(\d+)', s)
    mi, ma, av = 0, 0, 0
    for n, d in parts:
        n, d = int(n), int(d)
        mi += n
        ma += n * d
        av += n * (d + 1) / 2
    f = re.search(r'([+-])(\d+)(?!d)', s)
    if f:
        op, v = f.groups()
        v = int(v)
        adj = v if op == '+' else -v
        mi, ma, av = mi + adj, ma + adj, av + adj
    return max(0, mi), max(0, ma), max(0, av)

def calculate_dpr_stats(atk, ac, save_mod):
    l = atk.get("level", 1)
    mi, ma, av = get_die_stats(atk.get("damage", "1d4"), l)
    if atk.get("type") == "spell_save" or "dc" in atk:
        dc = int(atk.get("dc", 12))
        fail = (max(1, min(20, dc - save_mod)) - 1) / 20.0
        m = fail + (1.0 - fail) * 0.5
        return mi*m, ma*m, av*m
    m = int(str(atk.get("atk", "+0")).replace("+", ""))
    h = (21 - max(2, min(20, ac - m))) / 20.0
    if "advantage" in atk.get("description", "").lower(): h = 1 - (1 - h)**2
    return mi*h, ma*h, av*h

def get_damage_sources(data, s_db, e_db):
    srcs, l = [], data.get("level", 1)
    for a in data.get("attacks", []):
        a["level"] = l
        srcs.append(a)
    sn = data.get("spells", []) + [t.replace("Spell: ", "") for t in data.get("talents", []) if str(t).startswith("Spell: ")]
    for n in sn:
        if n in s_db:
            s = s_db[n].copy()
            m = re.search(r'(\d+d\d+)', s.get("description", ""))
            if m:
                s.update({"damage": m.group(1), "type": "spell_save", "level": l, 
                          "dc": 10 + (data["stats"]["INT"]["modifier"] if "wizard" in [c.lower() for c in s.get("class", [])] else data["stats"]["WIS"]["modifier"])})
                srcs.append(s)
    en = [t.replace("Recipe: ", "") for t in data.get("talents", []) if str(t).startswith("Recipe: ")]
    for n in en:
        if n in e_db:
            e = e_db[n].copy()
            m = re.search(r'(\d+d\d+)', e.get("description", "").replace("(HL)", "1").replace("(LV)", "1"))
            if m:
                e.update({"damage": e.get("description", "").split("deal ")[1].split(" ")[0] if "deal " in e.get("description", "") else m.group(1),
                          "atk": data["stats"]["DEX"]["modifier"], "level": l})
                srcs.append(e)
    return srcs

def process_stats(paths):
    s_db = {s["name"]: s for s in (json.load(open("spells.json"))["spells"] if os.path.exists("spells.json") else [])}
    e_db = {e["name"]: e for e in (json.load(open("elixirs.json"))["elixirs"] if os.path.exists("elixirs.json") else [])}
    tr, ref = list(range(10, 23)), 15
    all_s = []
    plt.figure(figsize=(12, 7))
    for p in paths:
        if os.path.basename(p).startswith("_"): continue
        if "damage_stats.json" in p: continue
        with open(p, 'r') as f:
            d = json.load(f)
            srcs = get_damage_sources(d, s_db, e_db)
            if not srcs: continue
            c_e = {"name": d["name"], "class": d["class"], "weapon_stats": {}, "all_attacks": []}
            best_s, best_v = None, -1
            for s in srcs:
                mi_b, ma_b, av_b = get_die_stats(s.get("damage", "1d4"), d.get("level", 1))
                curve = [{"ac": v, "min": round(r[0], 2), "max": round(r[1], 2), "mean": round(r[2], 2)} 
                         for v in tr for r in [calculate_dpr_stats(s, v, v-10)]]
                dist = s.get("range", "C").split('/')[0]
                ms = [pt["mean"] for pt in curve]
                avg_dpr, min_dpr, max_dpr = sum(ms)/len(ms), min(ms), max(ms)
                a_stats = {"base_damage": {"min": mi_b, "max": ma_b, "mean": av_b}, 
                           "expected_dpr": {"min": round(min_dpr, 2), "max": round(max_dpr, 2), "mean": round(avg_dpr, 2)}}
                c_e["weapon_stats"][s["name"]] = a_stats
                a_e = {"name": s["name"], "range": dist, "stats": a_stats, "curve": curve}
                c_e["all_attacks"].append(a_e)
                m15 = calculate_dpr_stats(s, ref, ref-10)[2]
                if m15 > best_v: best_s, best_v = a_e, m15
            if best_s:
                plt.plot(tr, [pt["mean"] for pt in best_s["curve"]], marker='o', label=f"{d['name']} ({best_s['range']}): {best_s['name']}")
            all_s.append(c_e)
    with open("output/_damage_stats.json", "w") as f: json.dump(all_s, f, indent=2)
    plt.title("Best Attack Mean DPR per Character")
    plt.xlabel("Target AC")
    plt.ylabel("Mean Damage")
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.grid(True, ls='--', alpha=0.6)
    plt.tight_layout()
    plt.savefig("output/_damage_chart.png")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--all", action="store_true")
    files = glob.glob("output/*.json")
    if files: process_stats(files)
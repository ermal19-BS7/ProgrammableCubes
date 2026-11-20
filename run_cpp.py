"""Ekzekuton algoritmin e kundert (C++) per JWST ose Enterprise, kthen komandat dhe i verifikon.

Perdorimi:
    python run_cpp.py --case JWST          (rreth 1 minute)
    python run_cpp.py --case Enterprise    (rreth 1.5 - 2 ore)
    python run_cpp.py --case Enterprise --fresh   (fshin rezultatet e ndermjetme dhe fillon nga e para)

Enterprise ekzekutohet ne faza. Pas cdo faze ruhet rezultati ne reverse_cpp/work,
keshtu qe nese nderpritet, ekzekutimi i radhes vazhdon nga faza e fundit e perfunduar.
"""
import argparse
import json
import os
import shutil
import subprocess
import sys
import time

import numpy as np

from src.load_problem import load_problem, PROJECT_ROOT
from src.scoring import evaluate

CPP_DIR = os.path.join(PROJECT_ROOT, "reverse_cpp")
WORK = os.path.join(CPP_DIR, "work")
SRC = os.path.join(CPP_DIR, "reverse_solver.cpp")
EXE = os.path.join(CPP_DIR, "reverse_solver.exe" if os.name == "nt" else "reverse_solver")

BASE = {"DIG": "4", "DIGRAD": "3", "DIGRAD2": "2", "DIGM": "40", "PARK": "5"}

# Parametrat me te cilat u gjeten zgjidhjet.
CONFIG = {
    "JWST": {
        "stages": [
            {"name": "zgjidhja e kundert", "seed": 1, "evict": [213], "env": BASE},
        ],
    },
    "Enterprise": {
        "stages": [
            # 1. zgjidhja e kundert; kubet qe ngecin zakonisht levizen te paret (PRIO)
            {"name": "1 prioritet", "seed": 1, "prio": [2, 14, 33, 120, 300, 830, 1269, 1393, 1399],
             "env": {**BASE, "STOPAT": "1456"}},
            # 2-3. evikimi i kubeve te sakta rreth vendeve te lira, pastaj rindertimi
            {"name": "2 evikim", "seed": 5, "env": {**BASE, "EVICTF": "3"}},
            {"name": "3 evikim", "seed": 35, "env": {**BASE, "EVICTF": "4"}},
            # 4-5. operatori i ures per kubet qe jane pika prerjeje
            {"name": "4 ure", "seed": 33, "env": {**BASE, "EVICTF": "3", "BRLEG": "1", "BRDIG": "3"}},
            {"name": "5 ure", "seed": 39, "env": {**BASE, "EVICTF": "3", "EVICTR": "3", "BRLEG": "1", "BRDIG": "3"}},
            # 6. kubi i bllokuar 1042 zhvendoset ne nje qelize te lire afer
            {"name": "6 zhvendosje", "seed": 1, "ur": 0,
             "env": {"PSEUDO": "1042 3", "DIG": "4", "DIGRAD": "3", "DIGRAD2": "3", "DIGM": "30",
                     "PARK": "5", "REACHMS": "1000000"}},
        ],
        # 7. fix-up nga konfigurimi fillestar per kubet qe mbeten
        "fix": {"name": "7 fix-up", "seed": 2, "maxd": 100, "maxst": 200000,
                "env": {"EVICTF": "3", "EVICTC": "3", "BRIDGE": "1", "BRDIG": "3", "BRK": "6", "BRS": "80",
                        "BRMD": "150", "BRMS": "200000", "BRMAX": "4", "BRDROP": "0", "DIGMD": "200",
                        "DIGMS": "400000", "REACHMS": "1000000", "DIG": "4", "DIGRAD": "3", "DIGRAD2": "2",
                        "DIGM": "30", "PARK": "5"}},
    },
}


def compile_if_needed():
    if os.path.exists(EXE) and os.path.getmtime(EXE) >= os.path.getmtime(SRC):
        return
    cxx = shutil.which("g++")
    if cxx is None:
        sys.exit("Nuk u gjet g++. Instalo MSYS2/MinGW dhe provo perseri.")
    print("Po kompilohet...", flush=True)
    subprocess.run([cxx, "-O2", "-o", EXE, SRC], check=True)


def write_problem(path, header, start_pos, start_types, goal_pos, goal_types):
    with open(path, "w") as f:
        f.write(header + "\n")
        for p, t in zip(start_pos, start_types):
            f.write(f"{p[0]} {p[1]} {p[2]} {t}\n")
        for p, t in zip(goal_pos, goal_types):
            f.write(f"{p[0]} {p[1]} {p[2]} {t}\n")


def read_cmds(path):
    return [tuple(map(int, l.split())) for l in open(path) if l.strip()]


def run_stage(st, prob_file, out, resume=None, evict_file=None):
    if os.path.exists(out) and os.path.exists(out + ".end"):
        print(f"[{st['name']}] u gjet rezultati i ruajtur, po vazhdoj.", flush=True)
        return
    env = dict(os.environ)
    env.update(st["env"])
    env["CKPT"] = out + ".ckpt"
    if resume:
        env["RESUME"] = resume
    if "prio" in st:
        pf = out + ".prio"
        open(pf, "w").write(" ".join(map(str, st["prio"])) + "\n")
        env["PRIO"] = pf
    if "STOPAT" in st["env"]:
        env["STOPOUT"] = out
    args = [EXE, prob_file, str(st.get("maxd", 60)), str(st.get("maxst", 20000)), out + ".tmp", "conn", "0.1",
            str(st["seed"]), "2", str(st.get("ur", 3)), "0", "3"]
    if evict_file:
        args.append(evict_file)
    t0 = time.time()
    print(f"[{st['name']}] po ekzekutohet...", flush=True)
    res = subprocess.run(args, env=env, capture_output=True, text=True)
    if "STOPAT" in st["env"] and os.path.exists(out):
        # faza ndalet sapo arrin numrin e caktuar te kubeve te sakta
        open(out + ".end", "w").write("")
    else:
        os.replace(out + ".tmp", out)
        end_tmp = out + ".tmp.end"
        if os.path.exists(end_tmp):
            os.replace(end_tmp, out + ".end")
        else:
            open(out + ".end", "w").write("")
    line = [l for l in res.stdout.split("\n") if l.startswith("RESULT")]
    last = [l for l in res.stderr.split("\n") if l.strip()][-1:] if res.stderr else []
    print(f"[{st['name']}] perfundoi per {time.time() - t0:.0f} s. {line[0] if line else (last[0] if last else '')}",
          flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--case", default="JWST", choices=list(CONFIG))
    ap.add_argument("--fresh", action="store_true")
    a = ap.parse_args()
    cfg = CONFIG[a.case]

    problem = load_problem(a.case)
    init_pos = np.array(problem["initial_config"]).astype(int).tolist()
    tgt_pos = np.array(problem["target_config"]).astype(int).tolist()
    init_types = [int(t) for t in problem["initial_types"]]
    tgt_types = [int(t) for t in problem["target_types"]]
    n = len(init_pos)
    header = f"{n} {int(problem['num_cube_types'])} {int(problem['max_cmds'])} 0.3"

    work = os.path.join(WORK, a.case)
    if a.fresh and os.path.exists(work):
        shutil.rmtree(work)
    os.makedirs(work, exist_ok=True)
    compile_if_needed()

    # problemi i kundert: fillimi = konfigurimi i synuar, synimi = konfigurimi fillestar
    rev_file = os.path.join(work, "rev.txt")
    write_problem(rev_file, header, tgt_pos, tgt_types, init_pos, init_types)

    prev = None
    for i, st in enumerate(cfg["stages"]):
        out = os.path.join(work, f"stage{i + 1}.cmd")
        ev = None
        if st.get("evict"):
            ev = os.path.join(work, "evict.txt")
            open(ev, "w").write("\n".join(map(str, st["evict"])) + "\n")
        run_stage(st, rev_file, out, resume=prev, evict_file=ev)
        prev = out

    rev_cmds = read_cmds(prev)
    end_pos = [tuple(map(int, l.split())) for l in open(prev + ".end") if l.strip()]

    fix_cmds = []
    start_pos = [tuple(p) for p in init_pos]
    if "fix" in cfg:
        # fix-up: nga konfigurimi fillestar te gjendja ku perfundon zgjidhja e kundert
        fix_file = os.path.join(work, "fix.txt")
        write_problem(fix_file, header, init_pos, init_types, end_pos, tgt_types)
        fout = os.path.join(work, "fix.cmd")
        run_stage(cfg["fix"], fix_file, fout)
        fix_cmds = read_cmds(fout)
        start_pos = [tuple(map(int, l.split())) for l in open(fout + ".end") if l.strip()]

    index = {p: i for i, p in enumerate(start_pos)}
    mapping = {}
    for k, pos in enumerate(end_pos):
        i = index.get(tuple(pos))
        if i is None or init_types[i] != tgt_types[k]:
            sys.exit(f"Zgjidhja nuk eshte e plote (kubi {k} nuk eshte ne vendin e duhur).")
        mapping[k] = i
    fw = list(fix_cmds) + [(mapping[k], m ^ 1) for k, m in reversed(rev_cmds)]
    print("VERIFIKIM:", evaluate(problem, fw))
    out = os.path.join(PROJECT_ROOT, "solutions", f"{a.case}_cpp.json")
    json.dump([list(map(int, x)) for x in fw], open(out, "w"))
    print("ruajtur", out)


if __name__ == "__main__":
    main()

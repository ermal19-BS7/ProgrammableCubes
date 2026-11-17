"""Ekzekuton algoritmin e kundert (C++) per nje rast, kthen komandat dhe i verifikon me vleresuesin zyrtar."""
import argparse
import json
import os
import shutil
import subprocess
import sys

import numpy as np

from src.load_problem import load_problem, PROJECT_ROOT
from src.scoring import evaluate

CPP_DIR = os.path.join(PROJECT_ROOT, "reverse_cpp")
WORK = os.path.join(CPP_DIR, "work")
EXE = os.path.join(CPP_DIR, "reverse_solver.exe" if os.name == "nt" else "reverse_solver")

# parametrat me te cilat u gjeten zgjidhjet (pa evict = lista bosh)
CONFIG = {
    "JWST": dict(
        win=0.1, seed=1, noise=2.0, evict=[213],
        env={"DIG": "4", "DIGRAD": "3", "DIGRAD2": "2", "DIGM": "40", "PARK": "5"},
    ),
}

p = argparse.ArgumentParser()
p.add_argument("--case", default="JWST")
a = p.parse_args()
cfg = CONFIG[a.case]

problem = load_problem(a.case)
init_pos = np.array(problem["initial_config"]).astype(int).tolist()
tgt_pos = np.array(problem["target_config"]).astype(int).tolist()
init_types = [int(t) for t in problem["initial_types"]]
tgt_types = [int(t) for t in problem["target_types"]]
n = len(init_pos)

os.makedirs(WORK, exist_ok=True)

# problemi i kundert: fillimi = konfigurimi i synuar, synimi = konfigurimi fillestar
rev_file = os.path.join(WORK, f"{a.case}_rev.txt")
with open(rev_file, "w") as f:
    f.write(f"{n} {int(problem['num_cube_types'])} {int(problem['max_cmds'])} 0.3\n")
    for pos, t in zip(tgt_pos, tgt_types):
        f.write(f"{pos[0]} {pos[1]} {pos[2]} {t}\n")
    for pos, t in zip(init_pos, init_types):
        f.write(f"{pos[0]} {pos[1]} {pos[2]} {t}\n")
evict_file = os.path.join(WORK, f"{a.case}.evict")
with open(evict_file, "w") as f:
    f.write("\n".join(map(str, cfg["evict"])) + "\n")

# kompilimi
if not os.path.exists(EXE):
    cxx = shutil.which("g++")
    if cxx is None:
        sys.exit("Nuk u gjet g++. Instalo MSYS2/MinGW (shih udhezimet) dhe provo perseri.")
    print("Po kompilohet...", flush=True)
    subprocess.run([cxx, "-O2", "-o", EXE, os.path.join(CPP_DIR, "reverse_solver.cpp")], check=True)

# ekzekutimi
cmd_file = os.path.join(WORK, f"{a.case}_rev.cmd")
env = dict(os.environ)
env.update(cfg["env"])
print("Po ekzekutohet algoritmi (mund te zgjase disa minuta)...", flush=True)
args = [EXE, rev_file, "60", "20000", cmd_file, "conn", str(cfg["win"]), str(cfg["seed"]), str(cfg["noise"]), "3", "0", "3"]
if cfg["evict"]:
    args.append(evict_file)
res = subprocess.run(args, env=env, capture_output=True, text=True)
line = [l for l in res.stdout.split("\n") if l.startswith("RESULT")]
print(line[0] if line else res.stdout[-300:])

# kthimi i komandave
rev_cmds = [tuple(map(int, l.split())) for l in open(cmd_file) if l.strip()]
end_pos = [tuple(map(int, l.split())) for l in open(cmd_file + ".end") if l.strip()]
index = {tuple(pos): i for i, pos in enumerate(init_pos)}
mapping = {}
for k, pos in enumerate(end_pos):
    i = index.get(pos)
    if i is None or init_types[i] != tgt_types[k]:
        sys.exit(f"Zgjidhja e kundert nuk eshte e plote (kubi {k} nuk eshte ne vendin e duhur).")
    mapping[k] = i
fw = [(mapping[k], m ^ 1) for k, m in reversed(rev_cmds)]
print("VERIFIKIM:", evaluate(problem, fw))
out = os.path.join(PROJECT_ROOT, "solutions", f"{a.case}_cpp.json")
json.dump([list(map(int, x)) for x in fw], open(out, "w"))
print("ruajtur", out)

import argparse
import json
import os
import time

import numpy as np

from src.load_problem import load_problem, PROJECT_ROOT
from src.scoring import evaluate

p = argparse.ArgumentParser()
p.add_argument("--case", default="ISS")
p.add_argument("--win", type=float, default=0.4)
p.add_argument("--noise", type=float, default=1.0)
p.add_argument("--seeds", type=int, default=40)
p.add_argument("--start", type=int, default=1)
a = p.parse_args()

problem = load_problem(a.case)
from reverse_solver import solve_reverse, to_forward

init_pos = np.array(problem["initial_config"]).tolist()
tgt_pos = np.array(problem["target_config"]).tolist()
init_types = list(problem["initial_types"])
tgt_types = list(problem["target_types"])
n = len(init_pos)

for seed in range(a.start, a.start + a.seeds):
    t0 = time.time()
    cmds, sim, correct = solve_reverse(init_pos, init_types, tgt_pos, tgt_types, a.win, a.noise, seed)
    k = sum(correct)
    print(f"seed {seed}: {k}/{n} kuba, {len(cmds)} komanda, {time.time()-t0:.0f}s", flush=True)
    if k == n:
        fw = to_forward(init_pos, init_types, tgt_types, cmds, sim)
        print("VERIFIKIM:", evaluate(problem, fw), flush=True)
        out = os.path.join(PROJECT_ROOT, "solutions", f"{a.case}_reverse_py.json")
        json.dump([list(map(int, x)) for x in fw], open(out, "w"))
        print("ruajtur", out)
        break
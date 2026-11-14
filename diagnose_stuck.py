import argparse
import json
import os
from collections import Counter

import numpy as np

from src.load_problem import PROJECT_ROOT, load_problem


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--case", default="ISS")
    p.add_argument("--show", type=int, default=8)
    args = p.parse_args()

    problem = load_problem(args.case)
    from programmable_cubes_UDP import ProgrammableCubes

    path = os.path.join(PROJECT_ROOT, "solutions", f"{args.case}_best_commands.json")
    with open(path) as f:
        commands = json.load(f)

    cubes = ProgrammableCubes(problem["initial_config"])
    for c, m in commands:
        cubes.apply_single_update_step(c, m)

    types = problem["initial_types"]
    n = len(types)
    targets = {}
    for t in range(problem["num_cube_types"]):
        targets[t] = {tuple(q) for q in problem["target_config"][problem["target_types"] == t].tolist()}
    pos_type = {tuple(cubes.cube_position[i].tolist()): int(types[i]) for i in range(n)}

    correct = [tuple(cubes.cube_position[i].tolist()) in targets[types[i]] for i in range(n)]
    free = {t: set(targets[t]) for t in targets}
    for i in range(n):
        if correct[i]:
            free[types[i]].discard(tuple(cubes.cube_position[i].tolist()))

    print("Kubë të saktë:", sum(correct), "nga", n, "| komanda:", len(commands))

    legal_hist = Counter()
    dist_hist = Counter()
    rows = []
    for i in range(n):
        if correct[i]:
            continue
        legal = 0
        for m in range(6):
            if cubes.apply_single_update_step(i, m) == 1:
                legal += 1
                cubes.apply_single_update_step(i, m ^ 1)
        arr = np.array(list(free[types[i]]))
        d = int(np.abs(arr - cubes.cube_position[i]).sum(axis=1).min()) if len(arr) else -1
        legal_hist[legal] += 1
        dist_hist[min(d, 10)] += 1
        rows.append((i, int(types[i]), tuple(cubes.cube_position[i].tolist()), legal, d))

    print()
    print("Lëvizje të ligjshme për kubët e gabuar (numri i lëvizjeve: numri i kubëve):")
    for k in sorted(legal_hist):
        print(f"  {k}/6: {legal_hist[k]}")
    print("Distanca te objektivi më i afërt i lirë (10 = 10 ose më shumë):")
    for k in sorted(dist_hist):
        print(f"  {k}: {dist_hist[k]}")

    occupied = Counter()
    empty = Counter()
    for t in free:
        for q in free[t]:
            occ = pos_type.get(q)
            if occ is None:
                empty[t] += 1
            else:
                occupied[(t, occ)] += 1
    print()
    print("Objektivat e lirë bosh sipas llojit:", dict(empty))
    print("Objektivat e lirë të zënë nga kub i llojit tjetër (objektiv, kub): numri:", dict(occupied))

    print()
    print(f"Shembuj të kubëve të gabuar (kub, lloj, pozicion, lëvizje, distancë):")
    for r in rows[:args.show]:
        print("  ", r)


if __name__ == "__main__":
    main()
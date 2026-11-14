import argparse
import json
import os
from collections import Counter

from src.load_problem import PROJECT_ROOT, load_problem


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--case", default="JWST")
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

    occupied = {tuple(cubes.cube_position[i].tolist()) for i in range(n)}
    free = {t: set(targets[t]) for t in targets}
    for i in range(n):
        q = tuple(cubes.cube_position[i].tolist())
        if q in targets[types[i]]:
            free[types[i]].discard(q)

    steps = ((1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1))
    print("Objektivat bosh sipas numrit të fqinjëve të zënë (0-6), për çdo lloj:")
    for t in sorted(free):
        hist = Counter()
        for q in free[t]:
            if q in occupied:
                continue
            k = sum((q[0] + a, q[1] + b, q[2] + c) in occupied for a, b, c in steps)
            hist[k] += 1
        total = sum(hist.values())
        print(f"  lloji {t}: {total} bosh -> {dict(sorted(hist.items()))}")


if __name__ == "__main__":
    main()
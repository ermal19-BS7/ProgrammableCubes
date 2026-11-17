import argparse
import json
import os
import time

import numpy as np

from src.export_solution import export_solution
from src.load_problem import CASES, PROJECT_ROOT, load_problem
from src.scoring import evaluate
from src.solver_planned import solve_planned


def shake(problem, commands, rng, radius):
    from programmable_cubes_UDP import ProgrammableCubes

    cubes = ProgrammableCubes(problem["initial_config"])
    for c, m in commands:
        cubes.apply_single_update_step(c, m)

    types = problem["initial_types"]
    n = len(types)
    targets = {}
    for t in range(problem["num_cube_types"]):
        targets[t] = {tuple(q) for q in problem["target_config"][problem["target_types"] == t].tolist()}

    pos = [tuple(cubes.cube_position[i].tolist()) for i in range(n)]
    free = {t: set(targets[t]) for t in targets}
    for i in range(n):
        if pos[i] in targets[types[i]]:
            free[types[i]].discard(pos[i])
    holes = [q for t in free for q in free[t]]
    if not holes:
        return None

    q = holes[int(rng.integers(len(holes)))]
    near = [i for i in range(n) if sum(abs(a - b) for a, b in zip(pos[i], q)) <= radius]
    if not near:
        return None
    c = near[int(rng.integers(len(near)))]

    moves = []
    for _ in range(int(rng.integers(1, 4))):
        for m in rng.permutation(6):
            if cubes.apply_single_update_step(c, int(m)) == 1:
                moves.append((int(c), int(m)))
                break
    if not moves:
        return None
    return list(commands) + moves


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--case", default="ISS", choices=CASES)
    p.add_argument("--minutes", type=float, default=15.0)
    p.add_argument("--radius", type=int, default=3)
    p.add_argument("--seed", type=int, default=0)
    args = p.parse_args()

    problem = load_problem(args.case)
    path = os.path.join(PROJECT_ROOT, "solutions", f"{args.case}_best_commands.json")
    with open(path) as f:
        best = [tuple(c) for c in json.load(f)]
    r = evaluate(problem, best)
    best_f = float(r["fitness"])
    print(f"fillimi: {r['correct']} kuba, {r['commands']} komanda, fitness {best_f:.4f}")

    rng = np.random.default_rng(args.seed)
    t_end = time.time() + args.minutes * 60
    it = 0
    t0 = time.time()
    while time.time() < t_end:
        it += 1
        shaken = shake(problem, best, rng, args.radius)
        if shaken is None:
            continue
        cand = solve_planned(problem, 4, 3000, 120, shaken, 3, "near", 0)
        rc = evaluate(problem, cand)
        fc = float(rc["fitness"])
        mark = ""
        if fc < best_f:
            best, best_f = cand, fc
            with open(path, "w") as f:
                json.dump([list(c) for c in best], f)
            export_solution(problem, best, "lns")
            mark = "  <-- ruajtur"
        print(f"  hapi {it}: {rc['correct']} kuba, {rc['commands']} komanda, fitness {fc:.4f}, më i miri {best_f:.4f}, {time.time() - t0:.0f}s{mark}")

    print(f"përfundim: fitness {best_f:.4f} pas {it} hapash")


if __name__ == "__main__":
    main()
import argparse
import json
import os

from src.load_problem import PROJECT_ROOT, load_problem


def stays_connected(pos, occupied):
    steps = ((1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1))
    x, y, z = pos
    neigh = [(x + a, y + b, z + c) for a, b, c in steps if (x + a, y + b, z + c) in occupied]
    if len(neigh) <= 1:
        return True
    goal = set(neigh[1:])
    seen = {neigh[0], pos}
    stack = [neigh[0]]
    while stack:
        cx, cy, cz = stack.pop()
        for a, b, c in steps:
            q = (cx + a, cy + b, cz + c)
            if q in occupied and q not in seen:
                seen.add(q)
                goal.discard(q)
                if not goal:
                    return True
                stack.append(q)
    return not goal


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--case", default="ISS")
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
    pos = {i: tuple(cubes.cube_position[i].tolist()) for i in range(n)}
    occupied = set(pos.values())

    wrong = [i for i in range(n) if pos[i] not in targets[types[i]]]
    stuck = cut = other = 0
    for i in wrong:
        legal = 0
        for m in range(6):
            if cubes.apply_single_update_step(i, m) == 1:
                legal += 1
                cubes.apply_single_update_step(i, m ^ 1)
        if legal == 0:
            stuck += 1
            if stays_connected(pos[i], occupied):
                other += 1
            else:
                cut += 1

    all_cut = sum(1 for i in range(n) if not stays_connected(pos[i], occupied))
    print(f"Kubë të gabuar: {len(wrong)} nga {n}")
    print(f"Me 0/6 lëvizje: {stuck}")
    print(f"  prej tyre pika lidhëse (heqja e ndan strukturën): {cut}")
    print(f"  prej tyre të rrethuar fizikisht (nuk janë pika lidhëse): {other}")
    print(f"Pika lidhëse në gjithë strukturën: {all_cut} nga {n}")


if __name__ == "__main__":
    main()
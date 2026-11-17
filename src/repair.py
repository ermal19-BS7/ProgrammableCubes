import time

import numpy as np

from src.solver_planned import plan_path


def repair(problem, commands, slack=3, budget=1500, topk=2, depth=2, fanout=6, max_len=60, minutes=10.0):
    from programmable_cubes_UDP import ProgrammableCubes

    t_end = time.time() + minutes * 60
    cubes = ProgrammableCubes(problem["initial_config"])
    types = problem["initial_types"]
    n = len(types)
    for c, m in commands:
        cubes.apply_single_update_step(c, m)
    commands = [(int(c), int(m)) for c, m in commands]

    def pos(c):
        return tuple(cubes.cube_position[c].tolist())

    targets = {}
    for t in range(problem["num_cube_types"]):
        targets[t] = {tuple(q) for q in problem["target_config"][problem["target_types"] == t].tolist()}

    at = {pos(c): c for c in range(n)}
    correct = np.array([pos(c) in targets[types[c]] for c in range(n)])
    free = {t: set(targets[t]) for t in targets}
    for c in range(n):
        if correct[c]:
            free[types[c]].discard(pos(c))

    offsets = [
        (a, b, d)
        for a in range(-2, 3)
        for b in range(-2, 3)
        for d in range(-2, 3)
        if 0 < abs(a) + abs(b) + abs(d) <= 2
    ]
    offsets.sort(key=lambda o: abs(o[0]) + abs(o[1]) + abs(o[2]))

    def l1(a, b):
        return sum(abs(x - y) for x, y in zip(a, b))

    def move_cube(c, m):
        old = pos(c)
        if cubes.apply_single_update_step(c, m) == 0:
            return None
        new = pos(c)
        del at[old]
        at[new] = c
        return old, new

    def undo(c, m, expected):
        cur = pos(c)
        cubes.apply_single_update_step(c, m ^ 1)
        new = pos(c)
        if new != expected:
            raise RuntimeError("Zhbërja nuk e ktheu kubin në vendin e vjetër")
        del at[cur]
        at[new] = c

    def place(c, q):
        h0 = (l1(pos(c), q) + 1) // 2
        path = None
        for bound in range(h0, h0 + slack + 1):
            if bound > max_len:
                break
            path = plan_path(cubes, c, q, bound, budget)
            if path is not None:
                break
        if path is None:
            return False
        for m in path:
            move_cube(c, m)
            commands.append((int(c), int(m)))
        correct[c] = True
        free[types[c]].discard(pos(c))
        return True

    def fill(t, q, d):
        if time.time() > t_end:
            return False
        wrong = sorted(
            (c for c in range(n) if not correct[c] and types[c] == t),
            key=lambda c: l1(pos(c), q),
        )[:topk]
        for c in wrong:
            if place(c, q):
                return True
        if d == 0:
            return False
        tried = 0
        for off in offsets:
            cand = (q[0] + off[0], q[1] + off[1], q[2] + off[2])
            c = at.get(cand)
            if c is None or not correct[c] or types[c] != t:
                continue
            for m in range(6):
                r = move_cube(c, m)
                if r is None:
                    continue
                old, new = r
                if new != q:
                    undo(c, m, old)
                    continue
                commands.append((int(c), int(m)))
                free[t].discard(q)
                free[t].add(old)
                tried += 1
                if fill(t, old, d - 1):
                    return True
                commands.pop()
                free[t].discard(old)
                free[t].add(q)
                undo(c, m, old)
            if tried >= fanout:
                break
        return False

    progress = True
    while progress and len(commands) < problem["max_cmds"] and time.time() < t_end:
        progress = False
        holes = [(t, q) for t in free for q in sorted(free[t]) if q not in at]
        for t, q in holes:
            if time.time() > t_end:
                break
            if q in at or q not in free[t]:
                continue
            if fill(t, q, depth):
                progress = True
                print(f"  +1 kub: {int(correct.sum())} të saktë, {len(commands)} komanda")
    return commands
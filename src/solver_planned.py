from collections import deque

import numpy as np


def plan_path(cubes, c, goal, bound, budget):
    goal = np.asarray(goal)
    nodes = [0]

    def h(p):
        return (int(np.abs(p - goal).sum()) + 1) // 2

    def dfs(g, last, path):
        if np.array_equal(cubes.cube_position[c], goal):
            return True
        for m in range(6):
            if last is not None and m == (last ^ 1):
                continue
            old = cubes.cube_position[c].copy()
            if cubes.apply_single_update_step(c, m) == 0:
                continue
            nodes[0] += 1
            found = False
            if g + 1 + h(cubes.cube_position[c]) <= bound and nodes[0] < budget:
                path.append(m)
                found = dfs(g + 1, m, path)
                if not found:
                    path.pop()
            cubes.apply_single_update_step(c, m ^ 1)
            if not np.array_equal(cubes.cube_position[c], old):
                raise RuntimeError("Zhbërja nuk e ktheu kubin në vendin e vjetër")
            if found:
                return True
        return False

    path = []
    return path if dfs(0, None, path) else None


STEPS = ((1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1))


def compute_depth(all_targets):
    xs, ys, zs = zip(*all_targets)
    lo = (min(xs) - 1, min(ys) - 1, min(zs) - 1)
    hi = (max(xs) + 1, max(ys) + 1, max(zs) + 1)

    def inside(p):
        return all(lo[i] <= p[i] <= hi[i] for i in range(3))

    ext = {lo}
    dq = deque([lo])
    while dq:
        p = dq.popleft()
        for a, b, c in STEPS:
            q = (p[0] + a, p[1] + b, p[2] + c)
            if inside(q) and q not in all_targets and q not in ext:
                ext.add(q)
                dq.append(q)

    depth = {}
    dq = deque()
    for q in all_targets:
        if any((q[0] + a, q[1] + b, q[2] + c) in ext for a, b, c in STEPS):
            depth[q] = 1
            dq.append(q)
    while dq:
        p = dq.popleft()
        for a, b, c in STEPS:
            q = (p[0] + a, p[1] + b, p[2] + c)
            if q in all_targets and q not in depth:
                depth[q] = depth[p] + 1
                dq.append(q)
    return depth


def solve_planned(problem, slack=4, budget=3000, max_len=120, prefix=None, topk=3, order="near", seed=0, window=0.15):
    from programmable_cubes_UDP import ProgrammableCubes

    rng = np.random.default_rng(seed)
    cubes = ProgrammableCubes(problem["initial_config"])
    types = problem["initial_types"]
    n = len(types)

    prefix = list(prefix) if prefix else []
    for c, m in prefix:
        cubes.apply_single_update_step(c, m)

    def pos(c):
        return tuple(cubes.cube_position[c].tolist())

    targets = {}
    for t in range(problem["num_cube_types"]):
        targets[t] = {tuple(q) for q in problem["target_config"][problem["target_types"] == t].tolist()}
    all_targets = set().union(*targets.values())
    depth = compute_depth(all_targets) if order in ("deep", "deepwin", "deeppeel") else {}

    sweep_mode = order.startswith("sweep") or order in ("deepwin", "deeppeel")
    peel_mode = order == "deeppeel"
    rank = {}
    frac = window
    if sweep_mode:
        if order in ("deepwin", "deeppeel"):
            ranked = sorted(all_targets, key=lambda q: (-depth.get(q, 0), q))
        else:
            sign = 1 if order[5] == "+" else -1
            axis = "xyz".index(order[6])
            ranked = sorted(all_targets, key=lambda q: (sign * q[axis], q))
        rank = {q: i for i, q in enumerate(ranked)}

    pts = list(all_targets) + [tuple(p) for p in np.array(problem["initial_config"]).tolist()]
    bx, by, bz = zip(*pts)
    box_lo = (min(bx) - 3, min(by) - 3, min(bz) - 3)
    box_hi = (max(bx) + 3, max(by) + 3, max(bz) + 3)

    def reach(occupied, extra=None):
        seen = {box_lo}
        stack = [box_lo]
        while stack:
            p = stack.pop()
            for a, b, c in STEPS:
                q = (p[0] + a, p[1] + b, p[2] + c)
                if q in seen:
                    continue
                if not (
                    box_lo[0] <= q[0] <= box_hi[0]
                    and box_lo[1] <= q[1] <= box_hi[1]
                    and box_lo[2] <= q[2] <= box_hi[2]
                ):
                    continue
                if q in occupied or q == extra:
                    continue
                seen.add(q)
                stack.append(q)
        return seen

    def exposure(occupied):
        ext = reach(occupied)
        out = {}
        dq = deque()
        for p in occupied:
            if any((p[0] + a, p[1] + b, p[2] + c) in ext for a, b, c in STEPS):
                out[p] = 1
                dq.append(p)
        while dq:
            p = dq.popleft()
            for a, b, c in STEPS:
                q = (p[0] + a, p[1] + b, p[2] + c)
                if q in occupied and q not in out:
                    out[q] = out[p] + 1
                    dq.append(q)
        return out

    def enclosure(q):
        return sum((q[0] + a, q[1] + b, q[2] + d) in all_targets for a, b, d in STEPS)

    correct = np.array([pos(c) in targets[types[c]] for c in range(n)])
    free = {t: set(targets[t]) for t in targets}
    for c in range(n):
        if correct[c]:
            free[types[c]].discard(pos(c))

    commands = list(prefix)
    history = [(len(commands), int(correct.sum()))]

    def l1(a, b):
        return sum(abs(x - y) for x, y in zip(a, b))

    def nearest(c):
        return min(free[types[c]], key=lambda q: l1(pos(c), q))

    def sort_key(c):
        q = nearest(c)
        if order == "inner":
            return (-enclosure(q), l1(pos(c), q))
        if order == "random":
            return rng.random()
        return l1(pos(c), q)

    def try_place(c, q, occupied):
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
        old = pos(c)
        for m in path:
            cubes.apply_single_update_step(c, m)
            commands.append((int(c), int(m)))
        occupied.discard(old)
        occupied.add(pos(c))
        free[types[c]].discard(pos(c))
        correct[c] = True
        history.append((len(commands), int(correct.sum())))
        return True

    def open_targets(occupied):
        r0 = reach(occupied)
        return {q for t in free for q in free[t] if q not in occupied and q in r0}

    def is_safe(q, occupied, before):
        r1 = reach(occupied, q)
        return all(x in r1 for x in before if x != q)

    safe_mode = order == "safe"
    allow_unsafe = False

    progress = True
    while progress and len(commands) < problem["max_cmds"]:
        progress = False
        occupied = {pos(c) for c in range(n)}

        if order == "deep":
            pending = [(t, q) for t in free for q in free[t] if q not in occupied]
            pending.sort(key=lambda tq: -depth.get(tq[1], 0))
            for t, q in pending:
                if q not in free[t] or q in occupied:
                    continue
                cands = sorted(
                    (c for c in range(n) if not correct[c] and types[c] == t),
                    key=lambda c: l1(pos(c), q),
                )[:topk]
                for c in cands:
                    if try_place(c, q, occupied):
                        progress = True
                        break
            continue

        allowed = None
        if sweep_mode:
            frees = sorted((q for t in free for q in free[t]), key=lambda q: rank[q])
            k = max(1, int(len(frees) * frac))
            allowed = set(frees[:k])

        before = open_targets(occupied) if safe_mode and not allow_unsafe else None
        wrong = [c for c in range(n) if not correct[c] and free[types[c]]]
        if peel_mode:
            expo = exposure(occupied)
            wrong.sort(key=lambda c: (expo.get(pos(c), 99), sort_key(c)))
        else:
            wrong.sort(key=sort_key)
        for c in wrong:
            t = types[c]
            cand = sorted(
                (q for q in free[t] if q not in occupied and (allowed is None or q in allowed)),
                key=lambda q: l1(pos(c), q),
            )[:topk]
            for q in cand:
                if before is not None and not is_safe(q, occupied, before):
                    continue
                if try_place(c, q, occupied):
                    progress = True
                    if before is not None:
                        before = open_targets(occupied)
                    break

        if safe_mode:
            if progress:
                allow_unsafe = False
            elif not allow_unsafe:
                allow_unsafe = True
                progress = True

        if sweep_mode and not progress and frac < 1.0:
            frac = min(1.0, frac * 2)
            progress = True

    best_len, best_score = len(prefix), -1e9
    for length, k in history:
        s = 0.9 * k / n - 0.1 * length / problem["max_cmds"]
        if s > best_score:
            best_score, best_len = s, length
    return commands[:best_len]
import numpy as np


def assign_targets(problem):
    ini = np.array(problem["initial_config"])
    tgt = np.array(problem["target_config"])
    ity = np.array(problem["initial_types"])
    tty = np.array(problem["target_types"])
    n = len(ini)
    goal = np.zeros((n, 3), dtype=int)
    for t in np.unique(ity):
        cubes = list(np.where(ity == t)[0])
        slots = list(np.where(tty == t)[0])
        slot_of = {tuple(tgt[s]): s for s in slots}
        # Kubët që janë tashmë në një synim të llojit të vet mbeten aty
        for c in list(cubes):
            s = slot_of.get(tuple(ini[c]))
            if s is not None and s in slots:
                goal[c] = tgt[s]
                cubes.remove(c)
                slots.remove(s)
        if not cubes:
            continue
        d = np.abs(ini[cubes][:, None, :] - tgt[slots][None, :, :]).sum(axis=2)
        try:
            from scipy.optimize import linear_sum_assignment
            r, k = linear_sum_assignment(d)
            for i, j in zip(r, k):
                goal[cubes[i]] = tgt[slots[j]]
        except ImportError:
            pairs = sorted((d[i, j], i, j) for i in range(len(cubes)) for j in range(len(slots)))
            used_i, used_j = set(), set()
            for _, i, j in pairs:
                if i in used_i or j in used_j:
                    continue
                used_i.add(i)
                used_j.add(j)
                goal[cubes[i]] = tgt[slots[j]]
    return goal


def solve_assigned(problem, max_attempts=60000, seed=0, keep_prob=0.2):
    from programmable_cubes_UDP import ProgrammableCubes

    rng = np.random.default_rng(seed)
    cubes = ProgrammableCubes(problem["initial_config"])
    n = len(problem["initial_types"])
    goal = assign_targets(problem)

    def dist(c):
        return int(np.abs(cubes.cube_position[c] - goal[c]).sum())

    correct = np.array([dist(c) == 0 for c in range(n)])
    commands = []

    def score_now():
        return 0.9 * correct.sum() / n - 0.1 * len(commands) / problem["max_cmds"]

    best_score = score_now()
    best_len = 0

    for attempt in range(max_attempts):
        if attempt % 2000 == 0:
            print(f"  prova {attempt}: {len(commands)} komanda, {int(correct.sum())} kuba te sakte")
        if score_now() > best_score:
            best_score = score_now()
            best_len = len(commands)
        if len(commands) >= problem["max_cmds"]:
            break
        wrong = np.where(~correct)[0]
        if len(wrong) == 0:
            break

        c = int(rng.choice(wrong))
        m = int(rng.integers(6))
        old = cubes.cube_position[c].copy()
        d_before = dist(c)

        if cubes.apply_single_update_step(c, m) == 0:
            continue
        commands.append((c, m))

        d_after = dist(c)
        if d_after == 0:
            correct[c] = True
            continue
        if d_after < d_before or rng.random() < keep_prob:
            continue

        if cubes.apply_single_update_step(c, m ^ 1) == 1:
            if np.array_equal(cubes.cube_position[c], old):
                commands.pop()
            else:
                commands.append((c, m ^ 1))

    if score_now() > best_score:
        best_score = score_now()
        best_len = len(commands)

    return commands[:best_len]
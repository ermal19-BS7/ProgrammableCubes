import numpy as np


def solve_greedy(problem, max_attempts=2000, seed=0, keep_prob=0.0):
    # Importohet këtu sepse load_problem() duhet ta ketë rregulluar sys.path më parë
    from programmable_cubes_UDP import ProgrammableCubes

    rng = np.random.default_rng(seed)
    cubes = ProgrammableCubes(problem["initial_config"])
    types = problem["initial_types"]

    targets = []
    free = []
    for t in range(problem["num_cube_types"]):
        tset = {tuple(p) for p in problem["target_config"][problem["target_types"] == t].tolist()}
        targets.append(tset)
        free.append(set(tset))

    # Shënoj kubët që janë tashmë në vendin e duhur dhe e heq pozicionin e tyre nga të lirët
    correct = np.zeros(len(types), dtype=bool)
    for i, p in enumerate(cubes.cube_position):
        pos = tuple(p.tolist())
        if pos in targets[types[i]]:
            correct[i] = True
            free[types[i]].discard(pos)

    def distance(pos, t):
        if not free[t]:
            return 0
        arr = np.array(list(free[t]))
        return np.abs(arr - pos).sum(axis=1).min()

    commands = []

    def score_now():
        # Pjesa e formulës zyrtare që ndryshon: kubët e saktë dhe numri i komandave
        return 0.9 * correct.sum() / len(types) - 0.1 * len(commands) / problem["max_cmds"]

    # Kujtoj gjendjen më të mirë, sepse komandat e fundit mund ta ulin rezultatin
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
        t = types[c]
        old = cubes.cube_position[c].copy()
        d_before = distance(old, t)

        # Lëvizja e paligjshme kthen 0 dhe nuk ndryshon asgjë
        if cubes.apply_single_update_step(c, m) == 0:
            continue
        commands.append((c, m))

        new = tuple(cubes.cube_position[c].tolist())
        if new in free[t]:
            free[t].discard(new)
            correct[c] = True
            continue
        if distance(cubes.cube_position[c], t) < d_before:
            continue

        # Ndonjëherë e mbaj lëvizjen edhe pse nuk e afroi, që kubët të mos ngecin
        if rng.random() < keep_prob:
            continue

        # Përndryshe e zhbëj lëvizjen me atë të kundërtën
        if cubes.apply_single_update_step(c, m ^ 1) == 1:
            if np.array_equal(cubes.cube_position[c], old):
                commands.pop()
            else:
                commands.append((c, m ^ 1))

    # Kontroll i fundit, sepse cikli i kontrollon rezultatin vetëm në fillim të çdo prove
    if score_now() > best_score:
        best_score = score_now()
        best_len = len(commands)

    return commands[:best_len]
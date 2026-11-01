import numpy as np


def solve_directed(problem, max_attempts=2000, seed=0, keep_prob=0.0):
    # Importohet këtu sepse load_problem() duhet ta ketë rregulluar sys.path më parë
    from programmable_cubes_UDP import ProgrammableCubes

    rng = np.random.default_rng(seed)
    cubes = ProgrammableCubes(problem["initial_config"])
    types = problem["initial_types"]
    n = len(types)

    targets = []
    free = []
    for t in range(problem["num_cube_types"]):
        tset = {tuple(p) for p in problem["target_config"][problem["target_types"] == t].tolist()}
        targets.append(tset)
        free.append(set(tset))

    correct = np.zeros(n, dtype=bool)
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

    def step(c, m):
        # Zbaton lëvizjen dhe e shton në listë vetëm nëse ishte e ligjshme
        if cubes.apply_single_update_step(c, m) == 1:
            commands.append((c, m))
            return True
        return False

    def score_now():
        return 0.9 * correct.sum() / n - 0.1 * len(commands) / problem["max_cmds"]

    best_score = score_now()
    best_len = 0

    for attempt in range(max_attempts):
        if attempt % 2000 == 0:
            print(f"  prova {attempt}: {len(commands)} komanda, {int(correct.sum())} kuba te sakte")

        if len(commands) <= problem["max_cmds"] and score_now() > best_score:
            best_score = score_now()
            best_len = len(commands)

        # Lë pak hapësirë, sepse një provë mund të shtojë disa komanda
        if len(commands) >= problem["max_cmds"] - 5:
            break
        wrong = np.where(~correct)[0]
        if len(wrong) == 0:
            break

        c = int(rng.choice(wrong))
        t = types[c]
        old = cubes.cube_position[c].copy()
        d_before = distance(old, t)

        # Provoj të gjashtë lëvizjet dhe ia zhbëj secilës, përveç nëse kubi zë një synim
        options = []
        landed = False
        for m in rng.permutation(6):
            m = int(m)
            if not step(c, m):
                continue
            new = tuple(cubes.cube_position[c].tolist())
            if new in free[t]:
                free[t].discard(new)
                correct[c] = True
                landed = True
                break
            options.append((distance(cubes.cube_position[c], t), m))
            if step(c, m ^ 1) and np.array_equal(cubes.cube_position[c], old):
                commands.pop()
                commands.pop()
            else:
                # Zhbërja nuk e ktheu kubin, kështu që gjendja ka ndryshuar; ndaloj këtë provë
                options = []
                break
        if landed or not options:
            continue

        best_d, best_m = min(options)
        if best_d < d_before:
            step(c, best_m)
        elif rng.random() < keep_prob:
            step(c, options[int(rng.integers(len(options)))][1])

    if len(commands) <= problem["max_cmds"] and score_now() > best_score:
        best_len = len(commands)

    return commands[:best_len]
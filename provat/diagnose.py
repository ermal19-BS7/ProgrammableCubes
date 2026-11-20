import argparse
import contextlib
import io

import numpy as np

from src.load_problem import CASES, load_problem
from src.scoring import evaluate
from src.solver_greedy import solve_greedy


def main():
    parser = argparse.ArgumentParser(description="Tregon a jane te bllokuar kubet e gabuar")
    parser.add_argument("--case", default="JWST", choices=CASES)
    parser.add_argument("--attempts", type=int, default=150000)
    parser.add_argument("--keep", type=float, default=0.2)
    parser.add_argument("--seed", type=int, default=3)
    args = parser.parse_args()

    problem = load_problem(args.case)

    # Importohet pas load_problem(), kur sys.path eshte rregulluar
    from programmable_cubes_UDP import ProgrammableCubes

    with contextlib.redirect_stdout(io.StringIO()):
        commands = solve_greedy(problem, max_attempts=args.attempts, seed=args.seed, keep_prob=args.keep)

    print("Rezultati:", evaluate(problem, commands))

    positions = problem["udp"].final_cube_positions.copy()
    types = problem["initial_types"]

    # Kubet e gabuar jane ata qe nuk ndodhen ne nje pozicion te synuar te llojit te tyre
    wrong = []
    for t in range(problem["num_cube_types"]):
        target = {tuple(p) for p in problem["target_config"][problem["target_types"] == t].tolist()}
        for i in np.where(types == t)[0]:
            if tuple(positions[i].tolist()) not in target:
                wrong.append(int(i))
    print("Kuba te gabuar:", len(wrong))

    # Per cdo kub te gabuar numeroj sa nga 6 levizjet jane te ligjshme.
    # Pas cdo prove e rindertoj ansamblin nga pozicionet fillestare te kesaj gjendjeje.
    cubes = ProgrammableCubes(positions)
    legal_counts = []
    for c in wrong:
        legal = 0
        for m in range(6):
            if cubes.apply_single_update_step(c, m) == 1:
                legal += 1
            cubes.reset(positions)
        legal_counts.append(legal)

    counts = np.bincount(legal_counts, minlength=7)
    for k in range(7):
        print(f"{counts[k]} kuba te gabuar kane {k} levizje te ligjshme")


if __name__ == "__main__":
    main()
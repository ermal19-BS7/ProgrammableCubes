import argparse
import contextlib
import io
import time

from src.export_solution import export_solution
from src.load_problem import CASES, load_problem
from src.scoring import evaluate
from src.solver_assigned import solve_assigned


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--case", default="ISS", choices=CASES)
    p.add_argument("--attempts", type=int, default=60000)
    p.add_argument("--keep", type=float, default=0.2)
    p.add_argument("--seeds", type=int, default=5)
    p.add_argument("--start", type=int, default=0)
    args = p.parse_args()

    problem = load_problem(args.case)
    best = None
    fits = []
    for seed in range(args.start, args.start + args.seeds):
        t0 = time.time()
        with contextlib.redirect_stdout(io.StringIO()):
            commands = solve_assigned(problem, args.attempts, seed, args.keep)
        r = evaluate(problem, commands)
        fits.append(float(r["fitness"]))
        print(f"seed {seed}: {r['correct']} kuba, {r['commands']} komanda, fitness {r['fitness']:.4f}, {time.time() - t0:.1f}s")
        if best is None or r["fitness"] < best[0]:
            best = (r["fitness"], seed, commands)
    print(f"mesatarja {sum(fits) / len(fits):.4f}, me e mira {best[0]:.4f} (seed {best[1]})")
    export_solution(problem, best[2], f"assigned_k{args.keep}_a{args.attempts}_s{best[1]}")


if __name__ == "__main__":
    main()

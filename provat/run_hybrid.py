import argparse
import contextlib
import io
import time

from src.export_solution import export_solution
from src.load_problem import CASES, load_problem
from src.scoring import evaluate
from src.solver_greedy import solve_greedy
from src.solver_planned import solve_planned


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--case", default="ISS", choices=CASES)
    p.add_argument("--attempts", type=int, default=60000)
    p.add_argument("--keep", type=float, default=0.2)
    p.add_argument("--seeds", type=int, default=5)
    p.add_argument("--slack", type=int, default=4)
    p.add_argument("--budget", type=int, default=3000)
    args = p.parse_args()

    problem = load_problem(args.case)
    t0 = time.time()
    prefix = solve_planned(problem, args.slack, args.budget)
    r0 = evaluate(problem, prefix)
    print(f"planifikuesi: {r0['correct']} kuba, {r0['commands']} komanda, fitness {r0['fitness']:.4f}, {time.time() - t0:.1f}s")

    best = None
    fits = []
    for seed in range(args.seeds):
        t1 = time.time()
        with contextlib.redirect_stdout(io.StringIO()):
            commands = solve_greedy(problem, args.attempts, seed, args.keep, 0.0, prefix)
        r = evaluate(problem, commands)
        fits.append(float(r["fitness"]))
        print(f"seed {seed}: {r['correct']} kuba, {r['commands']} komanda, fitness {r['fitness']:.4f}, {time.time() - t1:.1f}s")
        if best is None or r["fitness"] < best[0]:
            best = (r["fitness"], seed, commands)
    print(f"mesatarja {sum(fits) / len(fits):.4f}, me e mira {best[0]:.4f} (seed {best[1]})")
    export_solution(problem, best[2], f"hybrid_k{args.keep}_a{args.attempts}_s{best[1]}")


if __name__ == "__main__":
    main()
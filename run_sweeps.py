import argparse
import time

from src.load_problem import CASES, load_problem
from src.scoring import evaluate
from src.solver_planned import solve_planned


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--case", default="ISS", choices=CASES)
    p.add_argument("--window", type=float, default=0.15)
    p.add_argument("--slack", type=int, default=4)
    p.add_argument("--budget", type=int, default=3000)
    p.add_argument("--orders", nargs="+", default=["near", "deepwin", "deeppeel"])
    args = p.parse_args()

    problem = load_problem(args.case)
    for order in args.orders:
        t0 = time.time()
        commands = solve_planned(problem, args.slack, args.budget, 120, None, 3, order, 0, args.window)
        r = evaluate(problem, commands)
        print(f"{args.case} {order} (dritare {args.window}): {r['correct']} kuba, {r['commands']} komanda, fitness {float(r['fitness']):.4f}, {time.time() - t0:.0f}s")


if __name__ == "__main__":
    main()
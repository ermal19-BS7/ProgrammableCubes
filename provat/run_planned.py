import argparse
import time

from src.export_solution import export_solution
from src.load_problem import CASES, load_problem
from src.scoring import evaluate
from src.solver_planned import solve_planned


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--case", default="ISS", choices=CASES)
    p.add_argument("--slack", type=int, default=4)
    p.add_argument("--budget", type=int, default=3000)
    p.add_argument("--maxlen", type=int, default=120)
    args = p.parse_args()

    problem = load_problem(args.case)
    t0 = time.time()
    commands = solve_planned(problem, args.slack, args.budget, args.maxlen)
    r = evaluate(problem, commands)
    print(f"{r['correct']} kuba, {r['commands']} komanda, fitness {r['fitness']:.4f}, {time.time() - t0:.1f}s")
    export_solution(problem, commands, f"planned_sl{args.slack}_b{args.budget}")


if __name__ == "__main__":
    main()
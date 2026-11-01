import argparse
import contextlib
import io
import time

from src.load_problem import CASES, load_problem
from src.scoring import evaluate
from src.solver_directed import solve_directed
from src.solver_greedy import solve_greedy


def main():
    parser = argparse.ArgumentParser(description="Krahason dy zgjidhesit me te njejtat parametra")
    parser.add_argument("--case", default="ISS", choices=CASES)
    parser.add_argument("--attempts", type=int, default=20000)
    parser.add_argument("--keep", type=float, default=0.2)
    parser.add_argument("--seed", type=int, default=0)
    args = parser.parse_args()

    problem = load_problem(args.case)

    for name, solver in (("greedy", solve_greedy), ("directed", solve_directed)):
        start = time.time()
        with contextlib.redirect_stdout(io.StringIO()):
            commands = solver(problem, max_attempts=args.attempts, seed=args.seed, keep_prob=args.keep)
        print(name, evaluate(problem, commands), f"{time.time() - start:.1f}s")


if __name__ == "__main__":
    main()
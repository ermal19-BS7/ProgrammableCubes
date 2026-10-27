import argparse
import time

from src.export_solution import export_solution
from src.load_problem import CASES, load_problem, summarize
from src.scoring import evaluate
from src.solver_greedy import solve_greedy


def main():
    parser = argparse.ArgumentParser(description="Programmable Cubes (SpOC 3)")
    parser.add_argument("--case", default="ISS", choices=CASES, help="Rasti qe do te ekzekutohet")
    parser.add_argument("--attempts", type=int, default=2000, help="Numri i provave te zgjidhesit")
    parser.add_argument("--keep", type=float, default=0.0, help="Probabiliteti per ta mbajtur nje levizje qe nuk afron")
    parser.add_argument("--seed", type=int, default=0, help="Fara e rastesise")
    args = parser.parse_args()

    problem = load_problem(args.case)
    summarize(problem)

    print("Pa komanda:", evaluate(problem, []))

    start = time.time()
    commands = solve_greedy(problem, max_attempts=args.attempts, seed=args.seed, keep_prob=args.keep)
    print(f"Koha e zgjidhesit: {time.time() - start:.1f} sekonda")
    print("Zgjidhesi greedy:", evaluate(problem, commands))

    label = f"greedy_k{args.keep}_a{args.attempts}_s{args.seed}"
    out_path, fitness = export_solution(problem, commands, label=label)
    print("Skedari i dorezimit:", out_path)
    print("Fitness i kromozomit te plote:", fitness)


if __name__ == "__main__":
    main()
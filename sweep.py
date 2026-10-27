import argparse
import contextlib
import io
import time

from src.export_solution import export_solution
from src.load_problem import CASES, load_problem
from src.scoring import evaluate
from src.solver_greedy import solve_greedy


def main():
    parser = argparse.ArgumentParser(description="Provon shume seed-e dhe ruan me te miren")
    parser.add_argument("--case", default="ISS", choices=CASES)
    parser.add_argument("--attempts", type=int, default=60000)
    parser.add_argument("--keep", type=float, default=0.2)
    parser.add_argument("--seeds", type=int, default=10, help="Sa seed-e te provohen")
    parser.add_argument("--start", type=int, default=0, help="Seed-i i pare")
    args = parser.parse_args()

    problem = load_problem(args.case)

    best_seed = None
    best_commands = None
    best_fitness = None

    for seed in range(args.start, args.start + args.seeds):
        t0 = time.time()
        # Heshtoj printimet e progresit te zgjidhesit, qe tabela te mbetet e lexueshme
        with contextlib.redirect_stdout(io.StringIO()):
            commands = solve_greedy(problem, max_attempts=args.attempts, seed=seed, keep_prob=args.keep)
        result = evaluate(problem, commands)
        fitness = float(result["fitness"])
        print(f"seed {seed}: {result['correct']} kuba, {result['commands']} komanda, "
              f"fitness {fitness:.4f}, {time.time() - t0:.1f}s")

        if best_fitness is None or fitness < best_fitness:
            best_fitness, best_seed, best_commands = fitness, seed, commands

    print(f"\nMe i miri: seed {best_seed}, fitness {best_fitness:.4f}")
    label = f"sweep_k{args.keep}_a{args.attempts}_s{best_seed}"
    out_path, fitness = export_solution(problem, best_commands, label=label)
    print("Skedari i dorezimit:", out_path)
    print("Fitness i kromozomit te plote:", fitness)


if __name__ == "__main__":
    main()
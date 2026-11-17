import argparse
import json
import os
import time

from src.export_solution import export_solution
from src.load_problem import CASES, PROJECT_ROOT, load_problem
from src.repair import repair
from src.scoring import evaluate


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--case", default="ISS", choices=CASES)
    p.add_argument("--slack", type=int, default=3)
    p.add_argument("--budget", type=int, default=1500)
    p.add_argument("--topk", type=int, default=2)
    p.add_argument("--depth", type=int, default=2)
    p.add_argument("--minutes", type=float, default=10.0)
    args = p.parse_args()

    problem = load_problem(args.case)
    path = os.path.join(PROJECT_ROOT, "solutions", f"{args.case}_best_commands.json")
    with open(path) as f:
        commands = [tuple(c) for c in json.load(f)]

    base = evaluate(problem, commands)
    print(f"fillimi: {base['correct']} kuba, {base['commands']} komanda, fitness {float(base['fitness']):.4f}")

    t0 = time.time()
    new = repair(problem, commands, args.slack, args.budget, args.topk, args.depth, 6, 60, args.minutes)
    r = evaluate(problem, new)
    print(f"pas riparimit: {r['correct']} kuba, {r['commands']} komanda, fitness {float(r['fitness']):.4f}, {time.time() - t0:.0f}s")

    if float(r["fitness"]) < float(base["fitness"]):
        with open(path, "w") as f:
            json.dump([list(c) for c in new], f)
        export_solution(problem, new, f"repair_d{args.depth}_t{args.topk}")
        print("Përmirësim: u ruajt.")
    else:
        print("Pa përmirësim: skedari nuk u ndryshua.")


if __name__ == "__main__":
    main()
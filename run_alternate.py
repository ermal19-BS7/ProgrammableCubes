import argparse
import contextlib
import io
import json
import os
import time

from src.export_solution import export_solution
from src.load_problem import CASES, PROJECT_ROOT, load_problem
from src.scoring import evaluate
from src.solver_greedy import solve_greedy
from src.solver_planned import solve_planned


def quiet(fn, *a, **k):
    with contextlib.redirect_stdout(io.StringIO()):
        return fn(*a, **k)


def run_one(problem, args, seed, t0):
    best = {"fitness": None, "commands": None, "label": None}

    def consider(label, commands):
        r = evaluate(problem, commands)
        f = float(r["fitness"])
        print(f"  {label}: {r['correct']} kuba, {r['commands']} komanda, fitness {f:.4f}, {time.time() - t0:.0f}s")
        if best["fitness"] is None or f < best["fitness"]:
            best["fitness"] = f
            best["commands"] = list(commands)
            best["label"] = label
        return r

    commands = quiet(solve_planned, problem, args.slack, args.budget, 120, None, 3, args.order, seed)
    r = consider("planifikues 0", commands)
    last_correct = r["correct"]
    stalls = 0

    for k in range(args.rounds):
        commands = quiet(solve_greedy, problem, args.burst, seed + k, args.keep, 0.0, commands, False)
        consider(f"rafal greedy {k + 1}", commands)
        commands = quiet(solve_planned, problem, args.slack, args.budget, 120, commands, 3, args.order, seed + k)
        r = consider(f"planifikues {k + 1}", commands)
        if r["correct"] <= last_correct:
            stalls += 1
        else:
            stalls = 0
        last_correct = r["correct"]
        if stalls >= args.patience:
            break

    commands = quiet(solve_greedy, problem, args.final, seed + 100, args.keep, 0.0, best["commands"], True)
    consider("greedy final", commands)
    return best


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--case", default="ISS", choices=CASES)
    p.add_argument("--rounds", type=int, default=10)
    p.add_argument("--burst", type=int, default=3000)
    p.add_argument("--final", type=int, default=5000)
    p.add_argument("--keep", type=float, default=0.2)
    p.add_argument("--seed", type=int, default=0)
    p.add_argument("--seeds", type=int, default=1)
    p.add_argument("--patience", type=int, default=2)
    p.add_argument("--slack", type=int, default=4)
    p.add_argument("--budget", type=int, default=3000)
    p.add_argument("--order", default="near", choices=["near", "inner", "random"])
    args = p.parse_args()

    problem = load_problem(args.case)
    t0 = time.time()
    overall = None
    for s in range(args.seed, args.seed + args.seeds):
        print(f"seed {s} (rend: {args.order})")
        best = run_one(problem, args, s * 1000, t0)
        print(f"  -> me e mira: {best['label']}, fitness {best['fitness']:.4f}")
        if overall is None or best["fitness"] < overall[0]:
            overall = (best["fitness"], s, best["commands"])

    print(f"REZULTATI: fitness {overall[0]:.4f} (seed {overall[1]})")

    path = os.path.join(PROJECT_ROOT, "solutions", f"{args.case}_best_commands.json")
    if os.path.exists(path):
        with open(path) as f:
            old = [tuple(c) for c in json.load(f)]
        old_fit = float(evaluate(problem, old)["fitness"])
        if old_fit <= overall[0]:
            print(f"Rezultati i ruajtur më parë ({old_fit:.4f}) është më i mirë ose i barabartë: nuk e prek.")
            return

    export_solution(problem, overall[2], f"alternate_{args.order}_b{args.burst}_s{overall[1]}")
    with open(path, "w") as f:
        json.dump(overall[2], f)
    print("Komandat u ruajtën te", path)


if __name__ == "__main__":
    main()
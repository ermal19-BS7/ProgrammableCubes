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


def run_one(problem, args, seed, t0, state):
    best = {"fitness": None, "commands": None, "label": None}

    def consider(label, commands):
        r = evaluate(problem, commands)
        f = float(r["fitness"])
        mark = ""
        if f < state["fit"]:
            state["fit"] = f
            with open(state["path"], "w") as fh:
                json.dump([list(c) for c in commands], fh)
            export_solution(problem, commands, "progress")
            mark = "  (ruajtur)"
        print(f"  {label}: {r['correct']} kuba, {r['commands']} komanda, fitness {f:.4f}, {time.time() - t0:.0f}s{mark}")
        if best["fitness"] is None or f < best["fitness"]:
            best["fitness"] = f
            best["commands"] = list(commands)
            best["label"] = label
        return r

    if args.resume and os.path.exists(state["path"]):
        with open(state["path"]) as fh:
            commands = [tuple(c) for c in json.load(fh)]
        r = consider("fillimi (nga skedari i ruajtur)", commands)
    else:
        commands = quiet(solve_planned, problem, args.slack, args.budget, 120, None, 3, args.order, seed)
        r = consider("planifikues 0", commands)
    last_correct = r["correct"]
    stalls = 0

    for k in range(args.rounds):
        commands = quiet(solve_greedy, problem, args.burst, seed + k, args.keep, args.shake, commands, False)
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
    p.add_argument("--shake", type=float, default=0.0)
    p.add_argument("--seed", type=int, default=0)
    p.add_argument("--seeds", type=int, default=1)
    p.add_argument("--patience", type=int, default=2)
    p.add_argument("--slack", type=int, default=4)
    p.add_argument("--budget", type=int, default=3000)
    p.add_argument("--order", default="near")
    p.add_argument("--resume", action="store_true")
    args = p.parse_args()

    problem = load_problem(args.case)
    t0 = time.time()

    path = os.path.join(PROJECT_ROOT, "solutions", f"{args.case}_best_commands.json")
    state = {"path": path, "fit": 0.0}
    if os.path.exists(path):
        with open(path) as fh:
            saved = [tuple(c) for c in json.load(fh)]
        state["fit"] = float(evaluate(problem, saved)["fitness"])
        print(f"Rezultati i ruajtur: {state['fit']:.4f}")

    overall = None
    for s in range(args.seed, args.seed + args.seeds):
        print(f"seed {s} (rend: {args.order}, shake: {args.shake}, resume: {args.resume})")
        best = run_one(problem, args, s * 1000, t0, state)
        print(f"  -> me e mira: {best['label']}, fitness {best['fitness']:.4f}")
        if overall is None or best["fitness"] < overall[0]:
            overall = (best["fitness"], s)

    print(f"REZULTATI: fitness {overall[0]:.4f}; më i miri i ruajtur: {state['fit']:.4f}")


if __name__ == "__main__":
    main()
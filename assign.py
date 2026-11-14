import argparse
import numpy as np
from src.load_problem import setup_environment, load_problem

try:
    from scipy.optimize import linear_sum_assignment
except ImportError:
    linear_sum_assignment = None


def assign(problem):
    ini = np.array(problem["initial_config"])
    tgt = np.array(problem["target_config"])
    ity = np.array(problem["initial_types"])
    tty = np.array(problem["target_types"])
    pairs = {}
    total = 0
    for t in np.unique(ity):
        a = np.where(ity == t)[0]
        b = np.where(tty == t)[0]
        d = np.abs(ini[a][:, None, :] - tgt[b][None, :, :]).sum(axis=2)
        if linear_sum_assignment is not None:
            r, c = linear_sum_assignment(d)
        else:
            r, c = np.arange(len(a)), np.argsort(d.argmin(axis=1))
        for i, j in zip(r, c):
            pairs[int(a[i])] = int(b[j])
            total += int(d[i, j])
    return pairs, total


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--case", default="ISS")
    args = p.parse_args()
    setup_environment()
    problem = load_problem(args.case)
    pairs, total = assign(problem)
    print("Rasti:", args.case)
    print("Kubë:", problem["num_cubes"])
    print("Distanca totale Manhattan:", total)
    print("Kufi i poshtëm i komandave (distanca / 2):", total // 2)
    print("Maksimumi i lejuar:", problem["max_cmds"])
    print("Scipy:", "po" if linear_sum_assignment else "jo (përdoret zgjidhje e përafërt)")


if __name__ == "__main__":
    main()
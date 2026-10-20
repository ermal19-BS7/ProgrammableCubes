import argparse
import numpy as np

from src.load_problem import CASES , load_problem , summarize
from src.scoring import evaluate

def main():
    parser = argparse.ArgumentParser(description="Programmable Cubes (SpOC 3)")
    parser.add_argument("--case", default="ISS" , choices=CASES , help="Rasti qe do te ekzekutohet")
    args = parser.parse_args()

    problem = load_problem(args.case)
    summarize(problem)

    baseline = problem["udp"].fitness(np.array([-1]))
    print("Fitness pa asnje komand (pritet 0):", baseline)

    print("Pa komanda:", evaluate(problem, []))

    rng = np.random.default_rng(0)
    random_commands = [(int(rng.integers(148)), int(rng.integers(6))) for _ in range(200)]
    print("200 komanda të rastësishme:", evaluate(problem, random_commands))


if __name__=="__main__":
    main()
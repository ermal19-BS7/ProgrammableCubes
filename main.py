import argparse
import numpy as np

from src.load_problem import CASES , load_problem , summarize

def main():
    parser = argparse.ArgumentParser(description="Programmable Cubes (SpOC 3)")
    parser.add_argument("--case", default="ISS" , choices=CASES , help="Rasti qe do te ekzekutohet")
    args = parser.parse_args()

    problem = load_problem(args.case)
    summarize(problem)

    baseline = problem["udp"].fitness(np.array([-1]))
    print("Fitness pa asnje komand (pritet 0):", baseline)


if __name__=="__main__":
    main()
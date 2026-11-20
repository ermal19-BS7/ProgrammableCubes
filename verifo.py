"""Verifikon zgjidhjet e ruajtura te solutions/ me vleresuesin zyrtar.

Perdorimi:
    python verifo.py                 (te tre rastet)
    python verifo.py --case JWST     (vetem nje rast)
"""
import argparse
import json
import os

ROOT = os.path.dirname(os.path.abspath(__file__))
FILES = {
    "ISS": "ISS_reverse_py.json",
    "JWST": "JWST_cpp.json",
    "Enterprise": "Enterprise_cpp.json",
}

ap = argparse.ArgumentParser()
ap.add_argument("--case", choices=list(FILES))
a = ap.parse_args()
cases = [a.case] if a.case else list(FILES)

# skedaret lexohen para load_problem, sepse ai e ndryshon folderin e punes
solutions = {}
for case in cases:
    data = json.load(open(os.path.join(ROOT, "solutions", FILES[case])))
    solutions[case] = [tuple(x) for x in (data["commands"] if isinstance(data, dict) else data)]

from src.load_problem import load_problem
from src.scoring import evaluate

for case in cases:
    print(case, evaluate(load_problem(case), solutions[case]), flush=True)

import json

import numpy as np

from src.load_problem import PROJECT_ROOT


def build_chromosome(commands, chromosome_length):
    chromosome = []
    for cube, move in commands:
        chromosome += [int(cube), int(move)]
    chromosome.append(-1)

    # Nëse ka vend të mbetur, e plotësoj me zero dhe një -1 të fundit.
    # Kur komandat janë në kufi, -1 e parë është tashmë e fundit.
    if len(chromosome) < chromosome_length:
        chromosome += [0] * (chromosome_length - len(chromosome) - 1)
        chromosome.append(-1)

    assert len(chromosome) == chromosome_length, "Shumë komanda për këtë rast"
    return np.array(chromosome)


def export_solution(problem, commands, label="greedy"):
    chromosome = build_chromosome(commands, problem["chromosome_length"])

    # Folderi i punës është ndryshuar te Challenge/, prandaj përdor rrugë absolute
    out_dir = PROJECT_ROOT / "solutions"
    out_dir.mkdir(exist_ok=True)
    out_path = out_dir / f"{problem['name']}_{label}.json"

    entry = {
        "decisionVector": chromosome.tolist(),
        "problem": problem["name"].lower(),
        "challenge": "spoc-3-programmable-cubes",
        "name": f"{problem['name']} {label}",
        "description": "Greedy solver with random moves",
    }
    with open(out_path, "wt") as f:
        json.dump([entry], f, indent=6)

    # Vlerësoj kromozomin e plotë, që të krahasohet me atë që del nga ESA
    fitness = problem["udp"].fitness(chromosome)[0]
    return out_path, fitness
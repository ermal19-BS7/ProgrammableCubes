import os
import sys
from pathlib import Path

import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parent.parent
CHALLENGE_DIR = PROJECT_ROOT / "Challenge"

CASES = ("ISS", "JWST", "Enterprise")


def setup_environment():
    # Kodi i ESA-s i hap 'problems/...' dhe 'data/...' relativisht me folderin e punës,
    # prandaj e ndryshoj folderin e punës te Challenge/ në vend që t'i ndryshoj skedarët e tyre
    if str(CHALLENGE_DIR) not in sys.path:
        sys.path.insert(0, str(CHALLENGE_DIR))
    os.chdir(CHALLENGE_DIR)


def load_problem(case):
    if case not in CASES:
        raise ValueError(f"Rasti duhet të jetë një nga {CASES}, jo '{case}'")

    setup_environment()

    # Importohet pasi folderi i punës është rregulluar, përndryshe nuk gjen skedarët
    from programmable_cubes_UDP import programmable_cubes_UDP

    udp = programmable_cubes_UDP(case)
    setup = udp.setup

    return {
        "name": case,
        "udp": udp,
        "setup": setup,
        "num_cubes": setup["num_cubes"],
        "num_cube_types": setup["num_cube_types"],
        "max_cmds": setup["max_cmds"],
        # Dy numra për çdo komandë (kubi dhe lëvizja) plus një -1 në fund
        "chromosome_length": 2 * setup["max_cmds"] + 1,
        # UDP-ja i ngarkon pozicionet fillestare vetëm brenda fitness, prandaj i ngarkoj vetë
        "initial_config": np.load(f"{setup['path']}/Initial_Config.npy"),
        "initial_types": udp.initial_cube_types,
        "target_config": udp.target_cube_positions,
        "target_types": udp.target_cube_types,
    }


def count_correct(problem, positions):
    # Njëlloj si fitness_function e ESA-s: për çdo lloj, numëroj pozicionet e synuara
    # që janë të zëna nga një kub i atij lloji
    correct = 0
    for t in range(problem["num_cube_types"]):
        target = {tuple(p) for p in problem["target_config"][problem["target_types"] == t].tolist()}
        current = {tuple(p) for p in positions[problem["initial_types"] == t].tolist()}
        correct += len(target & current)
    return correct


def summarize(problem):
    print("Rasti:", problem["name"])
    print("Numri i kubëve:", problem["num_cubes"])
    print("Numri i llojeve:", problem["num_cube_types"])
    print("Maksimumi i komandave:", problem["max_cmds"])
    print("Gjatësia e kromozomit:", problem["chromosome_length"])

    for label in ("initial", "target"):
        types, counts = np.unique(problem[label + "_types"], return_counts=True)
        print(f"Kubë për lloj ({label}):", dict(zip(types.tolist(), counts.tolist())))

    correct = count_correct(problem, problem["initial_config"])
    print(f"Kubë të saktë në fillim: {correct} nga {problem['num_cubes']}")
    print()


if __name__ == "__main__":
    for case in CASES:
        summarize(load_problem(case))
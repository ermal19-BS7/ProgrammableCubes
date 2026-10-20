import numpy as np

from src.load_problem import count_correct


def evaluate(problem, commands):
    # commands është një listë çiftesh (kubi, lëvizja), p.sh. [(3, 1), (7, 4)]
    chromosome = []
    for cube, move in commands:
        chromosome += [cube, move]
    chromosome.append(-1)

    udp = problem["udp"]
    fitness = udp.fitness(np.array(chromosome))[0]

    # fitness() i ruan pozicionet përfundimtare te final_cube_positions
    correct = count_correct(problem, udp.final_cube_positions)

    return {
        "fitness": fitness,
        "correct": correct,
        "commands": len(commands),
    }
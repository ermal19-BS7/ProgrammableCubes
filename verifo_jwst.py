import json
from src.load_problem import load_problem
from src.scoring import evaluate

commands = [tuple(x) for x in json.load(open("solutions/JWST_commands_reverse_method.json"))]
problem = load_problem("JWST")
print(evaluate(problem, commands))
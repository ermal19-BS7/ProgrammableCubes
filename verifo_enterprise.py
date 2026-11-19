import json, os
ROOT = os.path.dirname(os.path.abspath(__file__))
data = json.load(open(os.path.join(ROOT, "solutions", "Enterprise_commands_reverse_method.json")))
commands = data["commands"] if isinstance(data, dict) else data

from src.load_problem import load_problem
from src.scoring import evaluate

problem = load_problem("Enterprise")
print(evaluate(problem, commands))

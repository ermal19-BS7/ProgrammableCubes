import numpy as np
from pathlib import Path

#ketu e zgjedhum rastin qe dojm me shqyrtu

CASE="ISS"

base = Path(__file__).resolve().parent.parent / "Challenge" / "data" / CASE


files = [
    "Initial_Config.npy",
    "Initial_Cube_Types.npy",
    "Target_Config.npy",
    "Target_Cube_Types.npy",
]


for name in files :
    arr = np.load(base / name)
    print("=====", name)
    print("forma (shape):", arr.shape)
    print("lloji (dtype):", arr.dtype)
    print("5 rreshtat e parë:")
    print(arr[:5])
    print()
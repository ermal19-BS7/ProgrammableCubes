"""Pika hyrese e projektit: ekzekuton algoritmin perfundimtar per rastin e zgjedhur.

    python main.py --case ISS          (Python, rreth 20 sekonda)
    python main.py --case JWST         (C++, rreth 1-2 minuta)
    python main.py --case Enterprise   (C++, rreth 2 ore)
"""
import argparse
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))

ap = argparse.ArgumentParser(description="Programmable Cubes (ESA SpOC 3)")
ap.add_argument("--case", default="ISS", choices=["ISS", "JWST", "Enterprise"])
a = ap.parse_args()

if a.case == "ISS":
    cmd = [sys.executable, os.path.join(ROOT, "run_reverse.py"), "--case", "ISS"]
else:
    cmd = [sys.executable, os.path.join(ROOT, "run_cpp.py"), "--case", a.case]
sys.exit(subprocess.call(cmd, cwd=ROOT))

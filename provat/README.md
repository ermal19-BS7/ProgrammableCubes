# Provat e hershme

Ketu jane algoritmet dhe skriptet e provuara para metodes perfundimtare (zgjidhja e kundert).
Mbahen per te treguar evolucionin e projektit; nuk perdoren nga zgjidhjet perfundimtare.

- `main_greedy.py`, `sweep.py`, `run_sweeps.py`: zgjidhesi greedy me levizje te rastesishme
- `run_alternate.py`, `run_hybrid.py`, `run_assigned.py`, `run_planned.py`: variante te greedy-t
- `run_lns.py`, `run_repair.py`, `run_finish.py`: perpjekje per riparim te zgjidhjeve te pjesshme
- `diagnose*.py`, `compare.py`, `assign.py`: analiza e kubeve qe ngecin

Algoritmet perkatese jane te `src/` (`solver_*.py`, `repair.py`).
Rezultatet e tyre jane te `solutions/` (p.sh. `ISS_greedy_*.json`, `JWST_sweep_*.json`).

Ekzekutohen nga rrenja e projektit, p.sh.: `python -m provat.run_hybrid`

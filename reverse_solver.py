"""Zgjidhja e kundert: ndertojme formen fillestare nga ajo e synuar, pastaj e kthejme sekuencen mbrapsht."""
import random
from collections import deque

from CubeMoveset import (
    diffs_to_surrounding,
    displacements,
    move_pattern_mapping,
    move_patterns_empty,
    move_patterns_occupied,
)

D6 = ((1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1))
SURR = [[tuple(v) for v in diffs_to_surrounding[a].tolist()] for a in range(3)]
PAT_DIR = [list(map(int, move_pattern_mapping[0])), list(map(int, move_pattern_mapping[1]))]
PAT_OCC = [list(map(int, p)) for p in move_patterns_occupied]
PAT_EMP = [list(map(int, p)) for p in move_patterns_empty]
DISP = [tuple(int(x) for x in d) for d in displacements]


class Sim:
    def __init__(self, positions):
        self.pos = [tuple(int(x) for x in p) for p in positions]
        self.occ = {p: i for i, p in enumerate(self.pos)}

    def connected_without(self, c):
        p = self.pos[c]
        nbs = [q for q in ((p[0] + a, p[1] + b, p[2] + d) for a, b, d in D6) if q in self.occ]
        if len(nbs) <= 1:
            return True
        nbset = set(nbs)
        seen = {p, nbs[0]}
        stack = [nbs[0]]
        found = 1
        while stack:
            x = stack.pop()
            for a, b, d in D6:
                q = (x[0] + a, x[1] + b, x[2] + d)
                if q in seen or q not in self.occ:
                    continue
                seen.add(q)
                stack.append(q)
                if q in nbset:
                    found += 1
                    if found == len(nbs):
                        return True
        return False

    def pattern(self, c, m):
        p = self.pos[c]
        ax, direction = m >> 1, m & 1
        S = SURR[ax]
        for pi in PAT_DIR[direction]:
            if all((p[0] + S[s][0], p[1] + S[s][1], p[2] + S[s][2]) in self.occ for s in PAT_OCC[pi]) and not any(
                (p[0] + S[s][0], p[1] + S[s][1], p[2] + S[s][2]) in self.occ for s in PAT_EMP[pi]
            ):
                return pi
        return -1

    def move(self, c, m):
        if not self.connected_without(c):
            return False
        pi = self.pattern(c, m)
        if pi < 0:
            return False
        d = DISP[(m >> 1) * 16 + pi]
        p = self.pos[c]
        q = (p[0] + d[0], p[1] + d[1], p[2] + d[2])
        del self.occ[p]
        self.pos[c] = q
        self.occ[q] = c
        return True

    def place(self, c, q):
        del self.occ[self.pos[c]]
        self.pos[c] = q
        self.occ[q] = c


def bfs_path(sim, c, free_targets, allowed, max_depth=60, max_states=20000):
    start = sim.pos[c]
    parent = {start: None}
    dq = deque([(start, 0)])
    seen = 0
    goal = None
    while dq:
        p, d = dq.popleft()
        if p != start and p in free_targets and p in allowed:
            goal = p
            break
        seen += 1
        if d >= max_depth or seen > max_states:
            continue
        sim.place(c, p)
        for m in range(6):
            if not sim.move(c, m):
                continue
            q = sim.pos[c]
            sim.place(c, p)
            if q not in parent:
                parent[q] = (p, m)
                dq.append((q, d + 1))
    sim.place(c, start)
    if goal is None:
        return None
    path = []
    cur = goal
    while parent[cur] is not None:
        prev, m = parent[cur]
        path.append(m)
        cur = prev
    path.reverse()
    return path


def solve_reverse(init_pos, init_types, tgt_pos, tgt_types, win=0.4, noise=1.0, seed=0, log=None):
    """Zgjidh problemin e kundert: nga konfigurimi i synuar drejt atij fillestar."""
    rng = random.Random(seed)
    n = len(init_pos)
    sim = Sim(tgt_pos)
    types = [int(t) for t in tgt_types]
    goal_at = {tuple(int(x) for x in p): int(t) for p, t in zip(init_pos, init_types)}
    free = {}
    for p, t in goal_at.items():
        free.setdefault(t, set()).add(p)
    correct = [False] * n
    for c in range(n):
        if goal_at.get(sim.pos[c]) == types[c]:
            correct[c] = True
            free[types[c]].discard(sim.pos[c])

    goal_set = set(goal_at)
    rank_key = {}
    for q in goal_set:
        nb = sum((q[0] + a, q[1] + b, q[2] + d) in goal_set for a, b, d in D6)
        rank_key[q] = -nb + noise * rng.random()
    ranked = sorted(goal_set, key=lambda q: rank_key[q])
    rank = {q: i for i, q in enumerate(ranked)}

    cmds = []
    frac = win
    progress = True
    while progress:
        progress = False
        all_free = [q for t in free for q in free[t]]
        all_free.sort(key=lambda q: rank[q])
        k = max(1, int(len(all_free) * frac))
        allowed = set(all_free[:k])
        keys = []
        for c in range(n):
            if correct[c] or not free[types[c]]:
                continue
            best = min(
                abs(sim.pos[c][0] - q[0]) + abs(sim.pos[c][1] - q[1]) + abs(sim.pos[c][2] - q[2])
                for q in free[types[c]]
            )
            foreign = 0 if sim.pos[c] in goal_at else 100000
            keys.append((foreign + best + int(noise * 3 * rng.random()), c))
        keys.sort()
        for _, c in keys:
            if correct[c]:
                continue
            path = bfs_path(sim, c, free[types[c]], allowed)
            if path is None:
                continue
            for m in path:
                sim.move(c, m)
                cmds.append((c, m))
            free[types[c]].discard(sim.pos[c])
            correct[c] = True
            progress = True
        if not progress and frac < 1.0:
            frac = min(1.0, frac * 2)
            progress = True
        if log:
            log(f"  korrekte {sum(correct)}/{n}, komanda {len(cmds)}")
    return cmds, sim, correct


def to_forward(init_pos, init_types, tgt_types, cmds, sim):
    """Kthen komandat e zgjidhjes se kundert ne komanda per drejtimin normal."""
    index = {tuple(int(x) for x in p): i for i, p in enumerate(init_pos)}
    mapping = {}
    for k in range(len(sim.pos)):
        i = index.get(sim.pos[k])
        if i is None or int(init_types[i]) != int(tgt_types[k]):
            return None
        mapping[k] = i
    return [(mapping[k], m ^ 1) for k, m in reversed(cmds)]
import numpy as np
from collections import defaultdict

# ── t maps to ops_remaining: ops_remaining = 5 - t ───────────────────────────
# t=0 → 5 ops left (start),  t=5 → 0 ops left (terminal, V=0)

def base_increments(action, a_prev):
    if action == 'safe':
        return [(1, 0.8), (2, 0.2)]
    if action == 'fast':
        if a_prev != 'fast':
            return [(3, 0.7), (4, 0.3)]
        else:
            return [(5, 0.6), (7, 0.4)]

def fatigue_distribution(f, action, a_prev):
    dist = defaultdict(float)
    for delta, p in base_increments(action, a_prev):
        f_new = f + delta
        if action == 'fast' and f >= 8:
            dist[f_new]     += p * 0.8
            dist[f_new + 4] += p * 0.2
        else:
            dist[f_new] += p
    return dict(dist)

def time_cost(action):
    return 5 if action == 'safe' else 2

def outcome_reward(f_new, r, action):
    """Deterministic reward given a specific fatigue outcome f_new."""
    if f_new >= 10:       # p_f = 1
        return -10 * r
    else:                 # p_f = 0
        return 10 - time_cost(action)

# ── DP Tables: V[t][f][a_prev] ────────────────────────────────────────────────

ACTIONS  = ['safe', 'fast']
FATIGUES = list(range(10))
A_PREVS  = ['none', 'safe', 'fast']

# V[t] and policy[t] indexed by (f, a_prev)
V      = {t: defaultdict(lambda: defaultdict(float)) for t in range(6)}
policy = {t: defaultdict(lambda: defaultdict(str))   for t in range(6)}

# ── Base Case: t=5 → ops_remaining=0 → V=0 ───────────────────────────────────
for f in FATIGUES:
    for ap in A_PREVS:
        V[5][f][ap] = 0.0

# ── Backward Induction: t = 4 down to 0 ──────────────────────────────────────
for t in range(4, -1, -1):
    r = 5 - t                      # ops remaining at this time step

    for f in FATIGUES:
        for ap in A_PREVS:
            # a_prev='none' only valid at t=0 (very first action, no history)
            if ap == 'none' and t != 0: continue
            if ap != 'none' and t == 0: continue

            best_val, best_action = -np.inf, None

            for action in ACTIONS:
                q_val = 0.0
                dist  = fatigue_distribution(f, action, ap)

                for f_new, p in dist.items():
                    # Step 1: fatigue outcome determined
                    # Step 2: deterministic reward given f_new
                    reward = outcome_reward(f_new, r, action)

                    # Step 3: future value at t+1
                    future = 0.0
                    if f_new < 10:             # survived → look up V[t+1]
                        future = V[t + 1][f_new][action]

                    q_val += p * (reward + future)

                if q_val > best_val:
                    best_val, best_action = q_val, action

            V[t][f][ap]      = best_val
            policy[t][f][ap] = best_action

# ── Print Results ─────────────────────────────────────────────────────────────

for t in range(5):
    r = 5 - t
    print(f"\n{'='*60}")
    print(f"  t = {t}  |  ops_remaining = {r}")
    print(f"{'='*60}")
    print(f"  {'State (f, a_prev)':<22} {'V*(s)':>10}  {'pi*(s)':>6}")
    print(f"  {'-'*42}")
    for f in FATIGUES:
        for ap in A_PREVS:
            if ap == 'none' and t != 0: continue
            if ap != 'none' and t == 0: continue
            print(f"  ({f}, {ap:<5})  "
                  f"{V[t][f][ap]:>16.4f}  {policy[t][f][ap]:>6}")

print(f"\n{'='*60}")
print(f"  t = 5  |  ops_remaining = 0  (TERMINAL: V = 0 for all states)")
print(f"{'='*60}")

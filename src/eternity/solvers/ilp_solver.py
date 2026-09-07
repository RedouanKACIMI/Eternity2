"""PuLP + CBC ILP model for Eternity-II-style edge-matching puzzles.
"""
import time
import warnings
from dataclasses import dataclass
from typing import Dict, Optional, Tuple

import pulp

from ..model import GRAY, PuzzleInstance, Solution


@dataclass
class SolveResult:
    status: str  # "Optimal", "Infeasible", "Not Solved" (hit the time limit), "Undefined"
    solve_time_s: float
    solution: Optional[Solution]


def solve_ilp(instance: PuzzleInstance, time_limit_s: float = 60.0) -> SolveResult:
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", DeprecationWarning)
        return _solve_ilp_impl(instance, time_limit_s)


def _solve_ilp_impl(instance: PuzzleInstance, time_limit_s: float) -> SolveResult:
    n_rows, n_cols = instance.n_rows, instance.n_cols
    pieces = instance.pieces
    max_color = max(c for p in pieces for c in p.edges)

    prob = pulp.LpProblem("eternity", pulp.LpMinimize)
    prob += 0  # feasibility

    x: Dict[Tuple[int, int, int, int], pulp.LpVariable] = {
        (r, c, p.id, k): pulp.LpVariable(f"x_r{r}_c{c}_p{p.id}_k{k}", cat="Binary")
        for r in range(n_rows)
        for c in range(n_cols)
        for p in pieces
        for k in range(4)
    }

    # Exactly one (piece, rotation) per cell.
    for r in range(n_rows):
        for c in range(n_cols):
            prob += pulp.lpSum(x[r, c, p.id, k] for p in pieces for k in range(4)) == 1

    # Exactly one (cell, rotation) per piece.
    for p in pieces:
        prob += (
            pulp.lpSum(x[r, c, p.id, k] for r in range(n_rows) for c in range(n_cols) for k in range(4))
            == 1
        )

    # Per-cell displayed-color variables
    top: Dict[Tuple[int, int], pulp.LpVariable] = {}
    right: Dict[Tuple[int, int], pulp.LpVariable] = {}
    bottom: Dict[Tuple[int, int], pulp.LpVariable] = {}
    left: Dict[Tuple[int, int], pulp.LpVariable] = {}
    for r in range(n_rows):
        for c in range(n_cols):
            top[r, c] = pulp.LpVariable(f"top_r{r}_c{c}", 0, max_color, cat="Integer")
            right[r, c] = pulp.LpVariable(f"right_r{r}_c{c}", 0, max_color, cat="Integer")
            bottom[r, c] = pulp.LpVariable(f"bottom_r{r}_c{c}", 0, max_color, cat="Integer")
            left[r, c] = pulp.LpVariable(f"left_r{r}_c{c}", 0, max_color, cat="Integer")

            prob += top[r, c] == pulp.lpSum(
                p.rotate(k)[0] * x[r, c, p.id, k] for p in pieces for k in range(4)
            )
            prob += right[r, c] == pulp.lpSum(
                p.rotate(k)[1] * x[r, c, p.id, k] for p in pieces for k in range(4)
            )
            prob += bottom[r, c] == pulp.lpSum(
                p.rotate(k)[2] * x[r, c, p.id, k] for p in pieces for k in range(4)
            )
            prob += left[r, c] == pulp.lpSum(
                p.rotate(k)[3] * x[r, c, p.id, k] for p in pieces for k in range(4)
            )

    # Border edges must face GRAY.
    for c in range(n_cols):
        prob += top[0, c] == GRAY
        prob += bottom[n_rows - 1, c] == GRAY
    for r in range(n_rows):
        prob += left[r, 0] == GRAY
        prob += right[r, n_cols - 1] == GRAY

    # Adjacent cells must show the same color on their shared edge.
    for r in range(n_rows):
        for c in range(n_cols - 1):
            prob += right[r, c] == left[r, c + 1]
    for r in range(n_rows - 1):
        for c in range(n_cols):
            prob += bottom[r, c] == top[r + 1, c]

    solver = pulp.PULP_CBC_CMD(msg=False, timeLimit=time_limit_s)
    start = time.perf_counter()
    prob.solve(solver)
    elapsed = time.perf_counter() - start

    status_name = pulp.LpStatus[prob.status]
    solution: Optional[Solution] = None
    if status_name == "Optimal":
        solution = {}
        for r in range(n_rows):
            for c in range(n_cols):
                for p in pieces:
                    for k in range(4):
                        val = x[r, c, p.id, k].value()
                        if val is not None and val > 0.5:
                            solution[r, c] = (p.id, k)

    return SolveResult(status=status_name, solve_time_s=elapsed, solution=solution)

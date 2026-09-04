"""CP-SAT model for Eternity-II-style edge-matching puzzles.

  1. every cell holds exactly one (piece, rotation) pair
  2. every piece is used at exactly one (cell, rotation) pair

"""
import time
from dataclasses import dataclass
from typing import Dict, Optional, Tuple

from ortools.sat.python import cp_model

from ..model import GRAY, PuzzleInstance, Solution


@dataclass
class SolveResult:
    status: str  # "OPTIMAL", "FEASIBLE", "INFEASIBLE", "UNKNOWN", "MODEL_INVALID"
    solve_time_s: float
    solution: Optional[Solution]


def solve_cpsat(instance: PuzzleInstance, time_limit_s: float = 60.0, num_workers: int = 8) -> SolveResult:
    n_rows, n_cols = instance.n_rows, instance.n_cols
    pieces = instance.pieces
    max_color = max(c for p in pieces for c in p.edges)

    model = cp_model.CpModel()

    x: Dict[Tuple[int, int, int, int], cp_model.IntVar] = {}
    for r in range(n_rows):
        for c in range(n_cols):
            for p in pieces:
                for rot in range(4):
                    x[r, c, p.id, rot] = model.NewBoolVar(f"x_r{r}_c{c}_p{p.id}_rot{rot}")

    # Exactly one (piece, rotation) per cell.
    for r in range(n_rows):
        for c in range(n_cols):
            model.AddExactlyOne(x[r, c, p.id, rot] for p in pieces for rot in range(4))

    # Exactly one (cell, rotation) per piece.
    for p in pieces:
        model.AddExactlyOne(
            x[r, c, p.id, rot] for r in range(n_rows) for c in range(n_cols) for rot in range(4)
        )

    # Per-cell displayed-color variables, channeled to the placement variables.
    top: Dict[Tuple[int, int], cp_model.IntVar] = {}
    right: Dict[Tuple[int, int], cp_model.IntVar] = {}
    bottom: Dict[Tuple[int, int], cp_model.IntVar] = {}
    left: Dict[Tuple[int, int], cp_model.IntVar] = {}
    for r in range(n_rows):
        for c in range(n_cols):
            top[r, c] = model.NewIntVar(0, max_color, f"top_r{r}_c{c}")
            right[r, c] = model.NewIntVar(0, max_color, f"right_r{r}_c{c}")
            bottom[r, c] = model.NewIntVar(0, max_color, f"bottom_r{r}_c{c}")
            left[r, c] = model.NewIntVar(0, max_color, f"left_r{r}_c{c}")
            for p in pieces:
                for rot in range(4):
                    t, rr, b, l = p.rotate(rot)
                    var = x[r, c, p.id, rot]
                    model.Add(top[r, c] == t).OnlyEnforceIf(var)
                    model.Add(right[r, c] == rr).OnlyEnforceIf(var)
                    model.Add(bottom[r, c] == b).OnlyEnforceIf(var)
                    model.Add(left[r, c] == l).OnlyEnforceIf(var)

    # Border edges must face GRAY.
    for c in range(n_cols):
        model.Add(top[0, c] == GRAY)
        model.Add(bottom[n_rows - 1, c] == GRAY)
    for r in range(n_rows):
        model.Add(left[r, 0] == GRAY)
        model.Add(right[r, n_cols - 1] == GRAY)

    # Adjacent cells must show the same color on their shared edge.
    for r in range(n_rows):
        for c in range(n_cols - 1):
            model.Add(right[r, c] == left[r, c + 1])
    for r in range(n_rows - 1):
        for c in range(n_cols):
            model.Add(bottom[r, c] == top[r + 1, c])

    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = time_limit_s
    solver.parameters.num_workers = num_workers

    start = time.perf_counter()
    status = solver.Solve(model)
    elapsed = time.perf_counter() - start

    status_name = solver.StatusName(status)
    solution: Optional[Solution] = None
    if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        solution = {}
        for r in range(n_rows):
            for c in range(n_cols):
                for p in pieces:
                    for rot in range(4):
                        if solver.Value(x[r, c, p.id, rot]):
                            solution[r, c] = (p.id, rot)

    return SolveResult(status=status_name, solve_time_s=elapsed, solution=solution)

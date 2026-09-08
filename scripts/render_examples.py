"""Render a couple of example solved boards into assets/ for the README."""
import os

from eternity.generator import generate_instance
from eternity.solvers.cpsat_solver import solve_cpsat
from eternity.verify import verify_solution
from eternity.visualize import render_solution

os.makedirs("assets", exist_ok=True)

EXAMPLES = [
    dict(n=8, colors=8, seed=1, time_limit=60, show_piece_ids=False, filename="assets/solution_8x8.png"),
    dict(n=4, colors=4, seed=2, time_limit=30, show_piece_ids=True, filename="assets/solution_4x4_labeled.png"),
    dict(n=5, colors=5, seed=2, time_limit=60, show_piece_ids=True, filename="assets/solution_5x5_labeled.png"),
]

for ex in EXAMPLES:
    instance = generate_instance(ex["n"], ex["n"], ex["colors"], seed=ex["seed"])
    result = solve_cpsat(instance, time_limit_s=ex["time_limit"])
    assert result.status == "OPTIMAL", f"expected OPTIMAL, got {result.status}"
    ok, reason = verify_solution(instance, result.solution)
    assert ok, reason

    title = f"{ex['n']}x{ex['n']}, colors={ex['colors']}, seed={ex['seed']}"
    render_solution(instance, result.solution, ex["filename"], title=title, show_piece_ids=ex["show_piece_ids"])
    print(f"wrote {ex['filename']}  ({result.solve_time_s:.2f}s to solve)")

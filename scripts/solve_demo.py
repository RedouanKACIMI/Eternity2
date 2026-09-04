"""Quick end-to-end smoke test: generate -> solve -> verify -> print.
Run with: python scripts/solve_demo.py
"""
from eternity.generator import generate_instance
from eternity.solvers.cpsat_solver import solve_cpsat
from eternity.verify import verify_solution


def print_grid(instance, solution) -> None:
    pieces_by_id = {p.id: p for p in instance.pieces}
    for r in range(instance.n_rows):
        cells = []
        for c in range(instance.n_cols):
            piece_id, rot = solution[r, c]
            edges = pieces_by_id[piece_id].rotate(rot)
            cells.append(f"p{piece_id:>2}{edges}")
        print("  ".join(cells))


def run(n_rows: int, n_cols: int, n_colors: int, seed: int, time_limit: float) -> None:
    print(f"--- {n_rows}x{n_cols} board, {n_colors} colors, seed={seed} ---")
    instance = generate_instance(n_rows, n_cols, n_colors, seed=seed)
    result = solve_cpsat(instance, time_limit_s=time_limit)
    print(f"status={result.status}  time={result.solve_time_s:.2f}s")
    if result.solution is not None:
        ok, reason = verify_solution(instance, result.solution)
        print(f"verified={ok}" + (f"  ({reason})" if reason else ""))
        print_grid(instance, result.solution)
    print()


if __name__ == "__main__":
    run(n_rows=3, n_cols=3, n_colors=2, seed=1, time_limit=30)
    run(n_rows=4, n_cols=4, n_colors=3, seed=2, time_limit=30)
    run(n_rows=5, n_cols=5, n_colors=4, seed=3, time_limit=60)

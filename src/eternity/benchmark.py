"""Benchmark harness for the CP-SAT solver.
"""
import csv
from dataclasses import dataclass
from typing import List, Optional

from .generator import generate_instance
from .solvers.cpsat_solver import solve_cpsat
from .verify import verify_solution


@dataclass
class BenchmarkConfig:
    n_rows: int
    n_cols: int
    n_colors: int
    seed: int
    time_limit_s: float


@dataclass
class BenchmarkRecord:
    n_rows: int
    n_cols: int
    n_colors: int
    seed: int
    time_limit_s: float
    status: str
    solve_time_s: float
    verified: Optional[bool]






def run_benchmark(configs: List[BenchmarkConfig], verbose: bool = True) -> List[BenchmarkRecord]:
    records = []
    for cfg in configs:
        instance = generate_instance(cfg.n_rows, cfg.n_cols, cfg.n_colors, seed=cfg.seed)
        result = solve_cpsat(instance, time_limit_s=cfg.time_limit_s)

        verified: Optional[bool] = None
        if result.solution is not None:
            ok, _ = verify_solution(instance, result.solution)
            verified = ok

        records.append(
            BenchmarkRecord(
                n_rows=cfg.n_rows,
                n_cols=cfg.n_cols,
                n_colors=cfg.n_colors,
                seed=cfg.seed,
                time_limit_s=cfg.time_limit_s,
                status=result.status,
                solve_time_s=result.solve_time_s,
                verified=verified,
            )
        )
        if verbose:
            print(
                f"{cfg.n_rows}x{cfg.n_cols}  colors={cfg.n_colors:<3} seed={cfg.seed}  "
                f"-> {result.status:<10} in {result.solve_time_s:7.2f}s  verified={verified}"
            )
    return records


def write_csv(records: List[BenchmarkRecord], path: str) -> None:
    fieldnames = [
        "n_rows",
        "n_cols",
        "n_colors",
        "seed",
        "time_limit_s",
        "status",
        "solve_time_s",
        "verified",
    ]
    with open(path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in records:
            writer.writerow(
                {
                    "n_rows": r.n_rows,
                    "n_cols": r.n_cols,
                    "n_colors": r.n_colors,
                    "seed": r.seed,
                    "time_limit_s": r.time_limit_s,
                    "status": r.status,
                    "solve_time_s": f"{r.solve_time_s:.4f}",
                    "verified": r.verified,
                }
            )

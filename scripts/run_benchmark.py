"""Run the CP-SAT benchmark sweep and write results to CSV.
"""
from eternity.benchmark import BenchmarkConfig, run_benchmark, write_csv
from eternity.solvers.cpsat_solver import solve_cpsat

SIZE_TIME_LIMITS = [
    (3, 30),
    (4, 30),
    (5, 30),
    (6, 30),
    (7, 60),
    (8, 60),
    (9, 90),
    (10, 60),  # TODO: check why it didn't finish tight in 60s
]

SWEEP = [
    BenchmarkConfig(n_rows=n, n_cols=n, n_colors=colors, seed=1, time_limit_s=time_limit)
    for n, time_limit in SIZE_TIME_LIMITS
    for colors in (n, 2 * n)
]

if __name__ == "__main__":
    records = run_benchmark(SWEEP, solve_fn=solve_cpsat, solver_name="cpsat")
    write_csv(records, "../benchmark_results_cpsat.csv")
    print("\nWrote benchmark_results_cpsat.csv")

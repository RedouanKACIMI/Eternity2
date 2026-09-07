"""Run the PuLP/CBC ILP benchmark sweep and write results to CSV.
"""
from eternity.benchmark import BenchmarkConfig, run_benchmark, write_csv
from eternity.solvers.ilp_solver import solve_ilp

SIZE_TIME_LIMITS = [
    (3, 30),
    (4, 60),
    (5, 90),
    (6, 120),  # CBC's practical frontier
]

SWEEP = [
    BenchmarkConfig(n_rows=n, n_cols=n, n_colors=colors, seed=1, time_limit_s=time_limit)
    for n, time_limit in SIZE_TIME_LIMITS
    for colors in (n, 2 * n)
]

if __name__ == "__main__":
    records = run_benchmark(SWEEP, solve_fn=solve_ilp, solver_name="ilp")
    write_csv(records, "../benchmark_results_ilp.csv")
    print("\nWrote benchmark_results_ilp.csv")

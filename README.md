# Eternity II-Style Edge-Matching Puzzle Solver

A constraint-satisfaction / ILP solver for reduced-scale instances of
Eternity II-style edge-matching puzzles: square tiles with a color on
each of the four edges, where adjacent tiles must match colors along
their shared edge.

This project follows up on a university Proseminar (TU Dortmund, WiSe
2023/24) covering Burkardt & Garvie's ILP formulation for the original
1999 Eternity Puzzle. **Full-size Eternity II (16x16, 256 pieces) is
NP-hard and not the target here**, this project targets reduced
instances (roughly 3x3 up to 8-10x10, depending on what each approach
can actually solve in reasonable time) and reports honestly on where
the approach breaks down.

## Setup

```bash
pip install -e ".[dev]"
```

## Try it

```bash
python scripts/solve_demo.py   # generate -> solve -> verify -> print, on a few small boards
pytest                          # generator + solver + verifier test suite
```

## Modeling approach (CP-SAT)

This is a **pure feasibility problem** --> find any valid placement, or
prove none exists. There's no objective function, which is also why a
successful solve reports `OPTIMAL`: with nothing to optimize, any
feasible point is trivially optimal.

### Sets and parameters

$$R = \{0,\dots,n_r-1\}, \quad C = \{0,\dots,n_c-1\}, \quad P = \{0,\dots,M-1\}, \quad K = \{0,1,2,3\}$$

where $M = n_r \cdot n_c$ is both the number of cells and the number
of pieces, and $K$ indexes clockwise quarter-turns. Piece $p$ has a
base edge tuple $(t_p, r_p, b_p, l_p)$ (top/right/bottom/left);
rotating $k$ steps clockwise cyclically shifts it to
$(t_p^k, r_p^k, b_p^k, l_p^k)$:

| $k$ | edges shown |
|---|---|
| 0 | $(t_p,\ r_p,\ b_p,\ l_p)$ |
| 1 | $(l_p,\ t_p,\ r_p,\ b_p)$ |
| 2 | $(b_p,\ l_p,\ t_p,\ r_p)$ |
| 3 | $(r_p,\ b_p,\ l_p,\ t_p)$ |

$\text{GRAY} = 0$; $\Gamma$ is the largest color value appearing in
the instance.

### Decision variables

$$x_{r,c,p,k} \in \{0,1\} \quad \forall (r,c)\in R\times C,\ p\in P,\ k\in K$$

$x_{r,c,p,k}=1$ iff piece $p$, rotated $k$ times, occupies cell
$(r,c)$.

Four auxiliary integer variables per cell, channeled to $x$ below,
hold the color actually displayed on each side once a piece is
placed:

$$T_{r,c},\ \mathrm{Rt}_{r,c},\ B_{r,c},\ L_{r,c} \in \{0,\dots,\Gamma\}$$

### Constraints

**1. Every cell holds exactly one (piece, rotation):**

$$\sum_{p\in P}\sum_{k\in K} x_{r,c,p,k} = 1 \qquad \forall (r,c)\in R\times C$$

**2. Every piece is used exactly once:**

$$\sum_{(r,c)\in R\times C}\sum_{k\in K} x_{r,c,p,k} = 1 \qquad \forall p\in P$$

Together, (1) and (2) force $x$ to encode a bijection between pieces
and cells (no separate all-different constraint is needed).

**3. Channeling: tie displayed colors to the chosen assignment.**
The code enforces this as an implication per assignment, via
`OnlyEnforceIf`:

$$x_{r,c,p,k}=1 \ \Rightarrow\ T_{r,c}=t_p^k,\ \ \mathrm{Rt}_{r,c}=r_p^k,\ \ B_{r,c}=b_p^k,\ \ L_{r,c}=l_p^k \qquad \forall (r,c,p,k)$$

Given constraint (1), this is mathematically equivalent to a single
weighted-sum equation per cell:

$$T_{r,c} = \sum_{p,k} t_p^k\, x_{r,c,p,k}, \quad \mathrm{Rt}_{r,c} = \sum_{p,k} r_p^k\, x_{r,c,p,k}, \quad B_{r,c} = \sum_{p,k} b_p^k\, x_{r,c,p,k}, \quad L_{r,c} = \sum_{p,k} l_p^k\, x_{r,c,p,k}$$

CP-SAT's reification is a natural fit since it's SAT-based under the
hood. CBC (the planned PuLP alternative) has no native reification
primitive, so that model will use the weighted-sum form instead (same constraint, different syntax).

**4. Border edges must show GRAY:**

$$T_{0,c}=0\ \ \forall c\in C, \qquad B_{n_r-1,c}=0\ \ \forall c\in C, \qquad L_{r,0}=0\ \ \forall r\in R, \qquad \mathrm{Rt}_{r,n_c-1}=0\ \ \forall r\in R$$

**5. Adjacent cells agree on their shared edge:**

$$\mathrm{Rt}_{r,c} = L_{r,c+1} \quad \forall r\in R,\ c\in\{0,\dots,n_c-2\}$$

$$B_{r,c} = T_{r+1,c} \quad \forall r\in\{0,\dots,n_r-2\},\ c\in C$$

### Size

$|x| = M^2 \cdot 4 = 4M^2$ binary variables, plus 4 channeling
equations per $x$ variable. For a square board of side $n$ ($M=n^2$):
$4n^4$ variables and $16n^4$ constraints (the concrete source of the
CP-SAT blowup the benchmark phase will need to characterize).

See `src/eternity/solvers/cpsat_solver.py` for the implementation with
inline commentary.

## Benchmark results (CP-SAT, single seed)

Ran on 3x3 through 10x10 boards, two color-count settings per size
("tight": colors = n, "loose": colors = 2n), one seed each. Harness in
`src/eternity/benchmark.py`; reproduce with
`python scripts/run_benchmark.py` (writes `benchmark_results.csv`).

| size | colors | status | solve time | verified |
|---|---|---|---|---|
| 3x3 | 3 (tight) | OPTIMAL | 0.04s | yes |
| 3x3 | 6 (loose) | OPTIMAL | 0.02s | yes |
| 4x4 | 4 (tight) | OPTIMAL | 0.05s | yes |
| 4x4 | 8 (loose) | OPTIMAL | 0.04s | yes |
| 5x5 | 5 (tight) | OPTIMAL | 0.48s | yes |
| 5x5 | 10 (loose) | OPTIMAL | 0.09s | yes |
| 6x6 | 6 (tight) | OPTIMAL | 1.71s | yes |
| 6x6 | 12 (loose) | OPTIMAL | 0.15s | yes |
| 7x7 | 7 (tight) | OPTIMAL | 23.56s | yes |
| 7x7 | 14 (loose) | OPTIMAL | 0.46s | yes |
| 8x8 | 8 (tight) | OPTIMAL | 10.72s | yes |
| 8x8 | 16 (loose) | OPTIMAL | 1.43s | yes |
| 9x9 | 9 (tight) | UNKNOWN (timed out) | 90.16s (cap) | -- |
| 9x9 | 18 (loose) | OPTIMAL | 12.11s | yes |
| 10x10 | 10 (tight) | UNKNOWN (timed out) | 60.41s (cap) | -- |
| 10x10 | 20 (loose) | OPTIMAL | 15.42s | yes |

**Takeaways:**

- **Color count matters more than board size.** Tight instances
  (colors = n) are consistently 5 to 50x slower than loose instances
  (colors = 2n) at the same board size. Fewer colors means more pieces
  look interchangeable to the solver, which blows up the search space
  even though the board itself hasn't grown.
- **The practical frontier for hard (tight) instances is around 8x8**
  with this formulation, `num_workers=8`, and no symmetry breaking.
  9x9 and 10x10 tight instances did not finish within their time caps.
- **UNKNOWN here means "ran out of time," never "possibly
  unsolvable."** Every instance is generated via reverse construction
  (see `generator.py`), so a solution is guaranteed to exist: a
  CP-SAT status of UNKNOWN on these instances is unambiguous: the
  solver hasn't found it yet, full stop.
- **7x7 tight (23.56s) took longer than 8x8 tight (10.72s).** single-seed timings are noisy, especially with CP-SAT's
  parallel portfolio search. in a later benchmark pass I should run
  multiple seeds per configuration and report medians, not single
  points.

## Layout

```
src/eternity/
  model.py              # Piece, PuzzleInstance, rotation logic
  generator.py           # reverse-construction instance generator
  verify.py              # independent solution checker
  benchmark.py           # sweep harness -> CSV
  solvers/
    cpsat_solver.py       # OR-Tools CP-SAT model
scripts/
  solve_demo.py           # end-to-end smoke test
  run_benchmark.py        # runs the full benchmark sweep
tests/                    # pytest suite
benchmark_results.csv    # latest recorded sweep (3x3 - 10x10)
```

## Reference

Burkardt, J., Garvie, M. - ILP formulation for the 1999 Eternity
Puzzle. (Full citation and discussion to be added in the final
writeup.)

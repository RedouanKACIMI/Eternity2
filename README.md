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

Decision variables `x[r, c, p, rot]` are boolean: true iff piece `p`
sits at cell `(r, c)` rotated by `rot` (0..3, 90-degree clockwise
steps). Two "exactly one" constraint families force every cell to hold
exactly one (piece, rotation) and every piece to be used exactly once,
which together make the assignment a bijection between pieces and
cells, no separate all-different constraint needed.

Edge matching is done via **channeling**: each cell gets four small
integer variables for its displayed top/right/bottom/left color.
Placing a piece pins those variables through reification
(`OnlyEnforceIf`). Edge matching between neighbors then becomes a
single equality between two integer variables, and border cells are
constrained to show GRAY (Eternity II's "faces outward" color)
directly. See `src/eternity/solvers/cpsat_solver.py` for the full
model with inline commentary.

## Layout

```
src/eternity/
  model.py              # Piece, PuzzleInstance, rotation logic
  generator.py           # reverse-construction instance generator
  verify.py              # independent solution checker
  solvers/
    cpsat_solver.py       # OR-Tools CP-SAT model
scripts/solve_demo.py    # end-to-end smoke test
tests/                    # pytest suite
```

## Reference

Burkardt, J., Garvie, M. ILP formulation for the 1999 Eternity
Puzzle. (Full citation and discussion to be added in the final
writeup.)

"""Generate solvable Eternity-II-style puzzle instances.
"""
import random
from typing import List, Optional

from .model import GRAY, Edges, Piece, PuzzleInstance


def generate_instance(
    n_rows: int,
    n_cols: int,
    n_colors: int,
    seed: Optional[int] = None,
) -> PuzzleInstance:
    """Build a random solvable instance via reverse construction."""
    if n_colors < 1:
        raise ValueError("n_colors must be >= 1")
    rng = random.Random(seed)

    # v_edge[r][c] = color of the boundary between cell (r, c) and (r, c+1)
    v_edge = [[rng.randint(1, n_colors) for _ in range(n_cols - 1)] for _ in range(n_rows)]
    # h_edge[r][c] = color of the boundary between cell (r, c) and (r+1, c)
    h_edge = [[rng.randint(1, n_colors) for _ in range(n_cols)] for _ in range(n_rows - 1)]

    def top(r: int, c: int) -> int:
        return h_edge[r - 1][c] if r > 0 else GRAY

    def bottom(r: int, c: int) -> int:
        return h_edge[r][c] if r < n_rows - 1 else GRAY

    def left(r: int, c: int) -> int:
        return v_edge[r][c - 1] if c > 0 else GRAY

    def right(r: int, c: int) -> int:
        return v_edge[r][c] if c < n_cols - 1 else GRAY

    solved_edges: List[Edges] = [
        (top(r, c), right(r, c), bottom(r, c), left(r, c))
        for r in range(n_rows)
        for c in range(n_cols)
    ]

    scrambled: List[Edges] = []
    for edges in solved_edges:
        k = rng.randint(0, 3)
        t, r_, b, l = edges
        for _ in range(k):
            t, r_, b, l = l, t, r_, b
        scrambled.append((t, r_, b, l))
    rng.shuffle(scrambled)

    pieces = tuple(Piece(id=i, edges=e) for i, e in enumerate(scrambled))
    return PuzzleInstance(n_rows=n_rows, n_cols=n_cols, pieces=pieces)

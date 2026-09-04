"""Core data structures for Eternity-II-style edge-matching puzzles.
"""
from dataclasses import dataclass
from typing import Dict, Tuple

GRAY = 0  # border/no-pattern edge, by Eternity II convention

Edges = Tuple[int, int, int, int]  # (top, right, bottom, left)

# A solution maps each (row, col) cell to the (piece_id, rotation) placed there.
# rotation is a count of 90-degree clockwise turns, 0..3.
Solution = Dict[Tuple[int, int], Tuple[int, int]]


@dataclass(frozen=True)
class Piece:
    """A single puzzle piece in a fixed reference orientation.
    """

    id: int
    edges: Edges

    def rotate(self, k: int) -> Edges:
        """Return this piece's edge tuple after k clockwise 90-degree turns.
        """
        k %= 4
        t, r, b, l = self.edges
        for _ in range(k):
            t, r, b, l = l, t, r, b
        return (t, r, b, l)


@dataclass
class PuzzleInstance:
    """A puzzle instance: board size + the pieces to place on it.
    """

    n_rows: int
    n_cols: int
    pieces: Tuple[Piece, ...]

    def __post_init__(self) -> None:
        expected = self.n_rows * self.n_cols
        if len(self.pieces) != expected:
            raise ValueError(
                f"Expected {expected} pieces for a {self.n_rows}x{self.n_cols} "
                f"board, got {len(self.pieces)}"
            )

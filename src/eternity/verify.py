"""Independent solution checker.
"""
from typing import Tuple

from .model import GRAY, PuzzleInstance, Solution


def verify_solution(instance: PuzzleInstance, solution: Solution) -> Tuple[bool, str]:

    n_rows, n_cols = instance.n_rows, instance.n_cols
    pieces_by_id = {p.id: p for p in instance.pieces}

    if len(solution) != n_rows * n_cols:
        return False, f"expected {n_rows * n_cols} placed cells, got {len(solution)}"

    used_pieces = set()
    edges_at = {}

    for r in range(n_rows):
        for c in range(n_cols):
            if (r, c) not in solution:
                return False, f"cell ({r},{c}) has no piece"
            piece_id, rot = solution[r, c]
            if piece_id not in pieces_by_id:
                return False, f"cell ({r},{c}) references unknown piece {piece_id}"
            if piece_id in used_pieces:
                return False, f"piece {piece_id} used more than once"
            if rot not in (0, 1, 2, 3):
                return False, f"cell ({r},{c}) has invalid rotation {rot}"
            used_pieces.add(piece_id)
            edges_at[r, c] = pieces_by_id[piece_id].rotate(rot)

    if len(used_pieces) != len(instance.pieces):
        return False, "not every piece was used exactly once"

    for r in range(n_rows):
        for c in range(n_cols):
            t, right_e, b, l = edges_at[r, c]

            if r == 0 and t != GRAY:
                return False, f"cell ({r},{c}) top edge touches the border but isn't GRAY"
            if r == n_rows - 1 and b != GRAY:
                return False, f"cell ({r},{c}) bottom edge touches the border but isn't GRAY"
            if c == 0 and l != GRAY:
                return False, f"cell ({r},{c}) left edge touches the border but isn't GRAY"
            if c == n_cols - 1 and right_e != GRAY:
                return False, f"cell ({r},{c}) right edge touches the border but isn't GRAY"

            if c < n_cols - 1:
                _, _, _, left_of_next = edges_at[r, c + 1]
                if right_e != left_of_next:
                    return False, f"color mismatch between ({r},{c}) right and ({r},{c+1}) left"
            if r < n_rows - 1:
                top_of_below, _, _, _ = edges_at[r + 1, c]
                if b != top_of_below:
                    return False, f"color mismatch between ({r},{c}) bottom and ({r+1},{c}) top"

    return True, ""

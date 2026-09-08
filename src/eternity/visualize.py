"""Render solved boards as images.

Requires the optional `viz` extra (`pip install -e ".[viz]"`).
"""
from typing import Dict, Optional

import matplotlib

matplotlib.use("Agg")  # headless
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon

from .model import GRAY, PuzzleInstance, Solution

_BORDER_COLOR = "#999999"
_PALETTE = plt.get_cmap("tab20")


def _color_for(value: int) -> object:
    if value == GRAY:
        return _BORDER_COLOR
    return _PALETTE((value - 1) % 20 / 20)


def render_solution(
    instance: PuzzleInstance,
    solution: Solution,
    path: str,
    title: Optional[str] = None,
    show_piece_ids: bool = False,
) -> None:
    n_rows, n_cols = instance.n_rows, instance.n_cols
    pieces_by_id = {p.id: p for p in instance.pieces}

    fig, ax = plt.subplots(figsize=(max(n_cols, 3), max(n_rows, 3)))

    for (r, c), (piece_id, rot) in solution.items():
        t, right, b, left = pieces_by_id[piece_id].rotate(rot)
        x0, x1 = c, c + 1
        y0, y1 = -(r + 1), -r  # row 0 at the top; matplotlib y grows upward
        cx, cy = (x0 + x1) / 2, (y0 + y1) / 2

        # (corner, corner, center, edge color) for each of the 4 triangles
        triangles = [
            ((x0, y1), (x1, y1), t),  # top
            ((x1, y1), (x1, y0), right),  # right
            ((x1, y0), (x0, y0), b),  # bottom
            ((x0, y0), (x0, y1), left),  # left
        ]
        for corner_a, corner_b, color_val in triangles:
            tri = Polygon(
                [corner_a, corner_b, (cx, cy)],
                closed=True,
                facecolor=_color_for(color_val),
                edgecolor="black",
                linewidth=0.4,
            )
            ax.add_patch(tri)

        if show_piece_ids:
            ax.text(
                cx,
                cy,
                str(piece_id),
                ha="center",
                va="center",
                fontsize=7,
                color="white",
                bbox=dict(boxstyle="circle", facecolor="black", alpha=0.65, pad=0.15),
            )

    ax.set_xlim(0, n_cols)
    ax.set_ylim(-n_rows, 0)
    ax.set_aspect("equal")
    ax.axis("off")
    if title:
        ax.set_title(title)

    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)

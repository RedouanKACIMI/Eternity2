import pytest

from eternity.generator import generate_instance
from eternity.model import GRAY, Piece
from eternity.solvers.cpsat_solver import solve_cpsat
from eternity.solvers.ilp_solver import solve_ilp
from eternity.verify import verify_solution
from eternity.visualize import render_solution


def test_rotate_full_circle_returns_original():
    p = Piece(id=0, edges=(1, 2, 3, 4))
    assert p.rotate(0) == p.edges
    assert p.rotate(4) == p.edges


def test_rotate_one_step_matches_convention():
    # (top, right, bottom, left) = (1, 2, 3, 4)
    # one clockwise turn: new_top=old_left, new_right=old_top,
    # new_bottom=old_right, new_left=old_bottom
    p = Piece(id=0, edges=(1, 2, 3, 4))
    assert p.rotate(1) == (4, 1, 2, 3)


@pytest.mark.parametrize(
    "n_rows,n_cols,n_colors,seed",
    [
        (3, 3, 2, 1),
        (3, 3, 3, 7),
        (4, 4, 3, 2),
        (4, 5, 3, 5),
    ],
)
def test_generated_instance_is_solvable_and_verifies(n_rows, n_cols, n_colors, seed):
    instance = generate_instance(n_rows, n_cols, n_colors, seed=seed)
    assert len(instance.pieces) == n_rows * n_cols

    result = solve_cpsat(instance, time_limit_s=30.0)
    assert result.status in ("OPTIMAL", "FEASIBLE"), (
        f"expected a solution for a by-construction-solvable {n_rows}x{n_cols} instance, "
        f"got {result.status}"
    )
    ok, reason = verify_solution(instance, result.solution)
    assert ok, reason


@pytest.mark.parametrize(
    "n_rows,n_cols,n_colors,seed",
    [
        (2, 2, 2, 1),
        (3, 3, 2, 1),
        (3, 3, 3, 7),
        (4, 4, 4, 2),
    ],
)
def test_ilp_solves_and_verifies(n_rows, n_cols, n_colors, seed):
    # CBC is dramatically slower than CP-SAT on this formulation (see
    # README benchmark section), kept small so the suite stays fast.
    instance = generate_instance(n_rows, n_cols, n_colors, seed=seed)
    result = solve_ilp(instance, time_limit_s=60.0)
    assert result.status == "Optimal", (
        f"expected a solution for a by-construction-solvable {n_rows}x{n_cols} instance, "
        f"got {result.status}"
    )
    ok, reason = verify_solution(instance, result.solution)
    assert ok, reason


def test_verifier_rejects_reused_piece():
    instance = generate_instance(2, 2, 2, seed=1)
    p0 = instance.pieces[0]
    bad_solution = {(0, 0): (p0.id, 0), (0, 1): (p0.id, 0), (1, 0): (p0.id, 0), (1, 1): (p0.id, 0)}
    ok, reason = verify_solution(instance, bad_solution)
    assert not ok
    assert "more than once" in reason


def test_verifier_rejects_border_color_mismatch():
    # A 1x1 board must be a single piece with all four edges GRAY.
    bad_piece = Piece(id=0, edges=(1, GRAY, GRAY, GRAY))
    from eternity.model import PuzzleInstance

    instance = PuzzleInstance(n_rows=1, n_cols=1, pieces=(bad_piece,))
    ok, reason = verify_solution(instance, {(0, 0): (0, 0)})
    assert not ok
    assert "GRAY" in reason


def test_render_solution_writes_a_nonempty_png(tmp_path):
    instance = generate_instance(3, 3, 3, seed=1)
    result = solve_cpsat(instance, time_limit_s=30.0)
    assert result.solution is not None

    out = tmp_path / "render.png"
    render_solution(instance, result.solution, str(out), title="test", show_piece_ids=True)
    assert out.exists()
    assert out.stat().st_size > 0

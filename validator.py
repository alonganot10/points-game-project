from typing import Sequence, Tuple

from chain import max_weighted_chain, compute_LRT

Point = Tuple[float, float]


def solution_score(weights: Sequence[int]) -> int:
    """
    Objective function:
    maximize total sum of weights.
    """

    return sum(weights)


def upgraded_count(weights: Sequence[int]) -> int:
    """
    Number of points upgraded from 1 to 3.
    """

    return sum(1 for w in weights if w == 3)


def is_feasible(points: Sequence[Point], weights: Sequence[int], W: int) -> bool:
    """
    A solution is feasible if:
        1. every weight is either 1 or 3
        2. max weighted chain <= W
    """

    if any(w not in (1, 3) for w in weights):
        return False

    return max_weighted_chain(points, weights) <= W


def is_terminal(points: Sequence[Point], weights: Sequence[int], W: int) -> bool:
    """
    A state is terminal if no point with weight 1 can be upgraded to 3
    without violating max weighted chain <= W.

    Important:
    Given current L/R/through values, upgrading point i from 1 to 3
    adds exactly 2 to every chain passing through i.

    So upgrade is legal iff:
        through[i] + 2 <= W
    """

    if not is_feasible(points, weights, W):
        return False

    _, _, through = compute_LRT(points, weights)

    for i, w in enumerate(weights):
        if w == 1 and through[i] + 2 <= W:
            return False

    return True


def validate_or_raise(points: Sequence[Point], weights: Sequence[int], W: int) -> None:
    """
    Raises an error if solution is invalid.
    """

    if len(points) != len(weights):
        raise ValueError("points and weights must have the same length")

    if any(w not in (1, 3) for w in weights):
        raise ValueError("all weights must be either 1 or 3")

    max_chain = max_weighted_chain(points, weights)

    if max_chain > W:
        raise ValueError(
            f"solution is not feasible: max weighted chain = {max_chain}, but W = {W}"
        )

    if not is_terminal(points, weights, W):
        raise ValueError("solution is feasible but not terminal")
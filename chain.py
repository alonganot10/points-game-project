from typing import List, Optional, Sequence, Tuple

import chain_cpp

Point = Tuple[float, float]


def _normalize_points(points: Sequence[Point]) -> List[Point]:
    return [(float(x), float(y)) for x, y in points]


def _normalize_weights(weights: Optional[Sequence[int]], n: int) -> List[int]:
    if weights is None:
        return [1] * n

    if len(weights) != n:
        raise ValueError("points and weights must have the same length")

    return [int(w) for w in weights]


def chain_dp_forward(points: Sequence[Point], weights: Optional[Sequence[int]] = None) -> List[int]:
    points = _normalize_points(points)
    weights = _normalize_weights(weights, len(points))

    return chain_cpp.chain_dp_forward(points, weights)


def max_weighted_chain(points: Sequence[Point], weights: Sequence[int]) -> int:
    points = _normalize_points(points)
    weights = _normalize_weights(weights, len(points))

    return chain_cpp.max_weighted_chain(points, weights)


def compute_W(points: Sequence[Point]) -> int:
    points = _normalize_points(points)

    return chain_cpp.compute_W(points)


def compute_LRT(points: Sequence[Point], weights: Optional[Sequence[int]] = None):
    points = _normalize_points(points)
    weights = _normalize_weights(weights, len(points))

    return chain_cpp.compute_LRT(points, weights)
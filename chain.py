from typing import List, Sequence, Tuple, Optional

Point = Tuple[float, float]


class FenwickMax:
    """
    Fenwick tree for prefix maximum queries.
    Supports:
        update(index, value)
        query(index) -> max value in [1..index]
    """

    def __init__(self, size: int):
        self.size = size
        self.tree = [0] * (size + 1)

    def update(self, index: int, value: int) -> None:
        while index <= self.size:
            if value > self.tree[index]:
                self.tree[index] = value
            index += index & -index

    def query(self, index: int) -> int:
        result = 0
        while index > 0:
            if self.tree[index] > result:
                result = self.tree[index]
            index -= index & -index
        return result


def chain_dp_forward(points: Sequence[Point], weights: Optional[Sequence[int]] = None) -> List[int]:
    """
    dp[i] = maximum weighted chain ending at point i.

    Chain condition:
        x_j < x_i and y_j < y_i

    Runtime:
        O(n log n)
    """

    n = len(points)

    if weights is None:
        weights = [1] * n

    if len(weights) != n:
        raise ValueError("points and weights must have the same length")

    if n == 0:
        return []

    y_values = sorted({y for _, y in points})
    y_to_index = {y: idx + 1 for idx, y in enumerate(y_values)}

    order = sorted(range(n), key=lambda i: (points[i][0], points[i][1]))

    fenwick = FenwickMax(len(y_values))
    dp = [0] * n

    pos = 0

    while pos < n:
        current_x = points[order[pos]][0]
        batch = []

        while pos < n and points[order[pos]][0] == current_x:
            batch.append(order[pos])
            pos += 1

        updates = []

        for i in batch:
            _, y = points[i]
            y_idx = y_to_index[y]

            # strict y condition, so query only values with y < current y
            best_previous = fenwick.query(y_idx - 1)

            dp[i] = best_previous + int(weights[i])
            updates.append((y_idx, dp[i]))

        # Update only after the whole x-batch.
        # This prevents chaining points with the same x.
        for y_idx, value in updates:
            fenwick.update(y_idx, value)

    return dp


def max_weighted_chain(points: Sequence[Point], weights: Sequence[int]) -> int:
    """
    Returns the maximum total weight of a valid chain.
    """

    dp = chain_dp_forward(points, weights)

    if not dp:
        return 0

    return max(dp)


def compute_W(points: Sequence[Point]) -> int:
    """
    W = longest chain length when all weights are 1.
    """

    weights = [1] * len(points)
    return max_weighted_chain(points, weights)


def compute_LRT(points: Sequence[Point], weights: Optional[Sequence[int]] = None):
    """
    Returns:
        L[i] = max weighted chain ending at point i
        R[i] = max weighted chain starting at point i
        through[i] = max weighted chain passing through point i

    For weighted chains:
        through[i] = L[i] + R[i] - weights[i]

    because point i is counted twice.
    """

    n = len(points)

    if weights is None:
        weights = [1] * n

    if len(weights) != n:
        raise ValueError("points and weights must have the same length")

    L = chain_dp_forward(points, weights)

    # To compute chains starting at point i,
    # transform (x, y) -> (-x, -y), then compute ending chains.
    reversed_points = [(-x, -y) for x, y in points]
    R = chain_dp_forward(reversed_points, weights)

    through = [
        L[i] + R[i] - int(weights[i])
        for i in range(n)
    ]

    return L, R, through
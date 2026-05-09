from dataclasses import dataclass
from typing import Dict, List, Optional, Sequence, Set, Tuple
import random
import time

from chain import compute_W, compute_LRT, max_weighted_chain
from validator import solution_score, upgraded_count, is_terminal

Point = Tuple[float, float]


@dataclass
class GRASPConfig:
    iterations: int = 5
    rcl_size: int = 30
    seed: int = 42
    time_limit_seconds: Optional[float] = None
    verbose: bool = True


def _initial_candidates(points: Sequence[Point], W: int) -> Tuple[List[int], List[int]]:
    """
    Finds points that are even possible to upgrade at the beginning.

    If the best unweighted chain through point i has length T[i],
    then upgrading i adds 2.

    So initially, i can only be considered if:
        T[i] + 2 <= W
    """

    n = len(points)
    weights = [1] * n

    _, _, through = compute_LRT(points, weights)

    candidates = [
        i for i in range(n)
        if through[i] + 2 <= W
    ]

    return candidates, through


def _construct_one_solution(
    points: Sequence[Point],
    W: int,
    initial_candidates: Sequence[int],
    base_through: Sequence[int],
    rng: random.Random,
    config: GRASPConfig,
) -> List[int]:
    """
    One GRASP construction phase.

    Builds one terminal feasible solution using randomized greedy choices.
    """

    n = len(points)

    weights = [1] * n
    remaining: Set[int] = set(initial_candidates)

    while remaining:
        _, _, current_through = compute_LRT(points, weights)

        legal_candidates = []

        # Remove candidates that are no longer legal.
        # Since weights only increase, an illegal candidate will never become legal later.
        for i in list(remaining):
            if current_through[i] + 2 <= W:
                current_slack = W - current_through[i]
                initial_slack = W - base_through[i]

                # Higher score is better.
                legal_candidates.append(
                    (current_slack, initial_slack, rng.random(), i)
                )
            else:
                remaining.remove(i)

        if not legal_candidates:
            break

        legal_candidates.sort(reverse=True)

        rcl_length = min(config.rcl_size, len(legal_candidates))
        rcl = legal_candidates[:rcl_length]

        _, _, _, chosen = rng.choice(rcl)

        weights[chosen] = 3
        remaining.remove(chosen)

    return weights


def solve_grasp(points: Sequence[Point], config: Optional[GRASPConfig] = None) -> Dict:
    """
    Main GRASP solver.

    Returns a dictionary with:
        weights
        W
        score
        upgraded_count
        max_weighted_chain
        iterations_done
        terminal
        runtime_seconds
    """

    if config is None:
        config = GRASPConfig()

    start_time = time.perf_counter()
    rng = random.Random(config.seed)

    n = len(points)

    W = compute_W(points)

    initial_candidates, base_through = _initial_candidates(points, W)

    best_weights = [1] * n
    best_score = solution_score(best_weights)
    best_max_chain = W

    iterations_done = 0

    if config.verbose:
        print(f"W = {W}")
        print(f"Initial possible candidates = {len(initial_candidates)}")

    for iteration in range(config.iterations):
        if config.time_limit_seconds is not None:
            elapsed = time.perf_counter() - start_time
            if elapsed >= config.time_limit_seconds:
                break

        weights = _construct_one_solution(
            points=points,
            W=W,
            initial_candidates=initial_candidates,
            base_through=base_through,
            rng=rng,
            config=config,
        )

        current_score = solution_score(weights)
        current_max_chain = max_weighted_chain(points, weights)

        if current_max_chain <= W and current_score > best_score:
            best_weights = weights
            best_score = current_score
            best_max_chain = current_max_chain

        iterations_done += 1

        if config.verbose:
            print(
                f"Iteration {iteration + 1}: "
                f"score={current_score}, "
                f"upgraded={upgraded_count(weights)}, "
                f"max_chain={current_max_chain}"
            )

    runtime_seconds = time.perf_counter() - start_time

    terminal = is_terminal(points, best_weights, W)

    return {
        "weights": best_weights,
        "W": W,
        "score": best_score,
        "upgraded_count": upgraded_count(best_weights),
        "max_weighted_chain": best_max_chain,
        "iterations_done": iterations_done,
        "terminal": terminal,
        "runtime_seconds": runtime_seconds,
    }
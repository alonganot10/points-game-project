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

    # New:
    # Instead of scanning all remaining candidates every step,
    # scan only a random sample.
    candidate_sample_size: int = 500


def _initial_candidates(points: Sequence[Point], W: int) -> Tuple[List[int], List[int]]:
    """
    Finds points that are possible to upgrade at the beginning.

    If the best unweighted chain through point i has length T[i],
    then upgrading i adds 2.

    Initially, i can only be considered if:
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


def _build_legal_candidates_from_list(
    candidate_indices: Sequence[int],
    remaining: Set[int],
    current_through: Sequence[int],
    base_through: Sequence[int],
    W: int,
    rng: random.Random,
) -> List[Tuple[int, int, float, int]]:
    """
    Builds scored legal candidates from a given list of candidate indices.

    Returns tuples:
        (current_slack, initial_slack, random_tiebreaker, point_index)

    Higher tuple is better because we sort reverse=True.
    """

    legal_candidates = []

    for i in candidate_indices:
        if i not in remaining:
            continue

        if current_through[i] + 2 <= W:
            current_slack = W - current_through[i]
            initial_slack = W - base_through[i]

            legal_candidates.append(
                (current_slack, initial_slack, rng.random(), i)
            )
        else:
            # Since weights only increase, a point that is illegal now
            # will not become legal later.
            remaining.remove(i)

    return legal_candidates


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

    Builds one feasible terminal-like solution using randomized greedy choices.

    This version samples candidates instead of scanning all remaining candidates
    every step.
    """

    n = len(points)

    weights = [1] * n
    remaining: Set[int] = set(initial_candidates)

    while remaining:
        # This is still the expensive part.
        # It recomputes the current best weighted chain through every point.
        _, _, current_through = compute_LRT(points, weights)

        # Sample candidates instead of checking all of them every round.
        sample_size = min(config.candidate_sample_size, len(remaining))
        sampled_candidates = rng.sample(list(remaining), sample_size)

        legal_candidates = _build_legal_candidates_from_list(
            candidate_indices=sampled_candidates,
            remaining=remaining,
            current_through=current_through,
            base_through=base_through,
            W=W,
            rng=rng,
        )

        # If the random sample found no legal candidate,
        # do one full scan before stopping.
        # This prevents stopping too early just because the sample was unlucky.
        if not legal_candidates:
            legal_candidates = _build_legal_candidates_from_list(
                candidate_indices=list(remaining),
                remaining=remaining,
                current_through=current_through,
                base_through=base_through,
                W=W,
                rng=rng,
            )

            if not legal_candidates:
                break

        # Greedy-randomized selection:
        # sort candidates by score, take top rcl_size, choose randomly from them.
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
        print(f"RCL size = {config.rcl_size}")
        print(f"Candidate sample size = {config.candidate_sample_size}")

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
import argparse
from pathlib import Path
from typing import List, Tuple

import pandas as pd

from solver import GRASPConfig, solve_grasp
from validator import validate_or_raise

Point = Tuple[float, float]


def read_points_from_excel(path: str) -> Tuple[pd.DataFrame, List[Point]]:
    df = pd.read_excel(path)

    if df.shape[1] < 2:
        raise ValueError("Excel file must contain at least two columns: X and Y")

    points = [
        (df.iloc[i, 0], df.iloc[i, 1])
        for i in range(len(df))
    ]

    return df, points


def write_solution_to_excel(df: pd.DataFrame, weights: List[int], output_path: str) -> None:
    if len(df) != len(weights):
        raise ValueError("DataFrame and weights must have the same length")

    df = df.copy()
    df["Weight"] = weights

    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)

    df.to_excel(output_file, index=False)


def main() -> None:
    parser = argparse.ArgumentParser()

    parser.add_argument("input_excel", help="Path to input Excel file")
    parser.add_argument("output_excel", help="Path to output Excel file")

    parser.add_argument("--iterations", type=int, default=5)
    parser.add_argument("--rcl-size", type=int, default=30)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--time-limit", type=float, default=None)
    parser.add_argument("--quiet", action="store_true")

    args = parser.parse_args()

    df, points = read_points_from_excel(args.input_excel)

    config = GRASPConfig(
        iterations=args.iterations,
        rcl_size=args.rcl_size,
        seed=args.seed,
        time_limit_seconds=args.time_limit,
        verbose=not args.quiet,
    )

    result = solve_grasp(points, config)

    weights = result["weights"]
    W = result["W"]

    validate_or_raise(points, weights, W)

    write_solution_to_excel(df, weights, args.output_excel)

    print()
    print("Finished.")
    print(f"W = {result['W']}")
    print(f"Score = {result['score']}")
    print(f"Upgraded points = {result['upgraded_count']}")
    print(f"Max weighted chain = {result['max_weighted_chain']}")
    print(f"Terminal = {result['terminal']}")
    print(f"Iterations done = {result['iterations_done']}")
    print(f"Runtime seconds = {result['runtime_seconds']:.3f}")
    print(f"Output written to: {args.output_excel}")


if __name__ == "__main__":
    main()
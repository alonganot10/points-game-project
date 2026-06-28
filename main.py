import argparse
import re
from pathlib import Path
from typing import Dict, List, Tuple

import pandas as pd
import matplotlib.pyplot as plt

from solver import GRASPConfig, solve_grasp
from validator import validate_or_raise

Point = Tuple[float, float]


def sanitize_sheet_name(name: str, used_names: set[str]) -> str:
    """
    Excel sheet names:
    - max 31 characters
    - cannot contain: : \ / ? * [ ]
    - must be unique
    """

    cleaned = re.sub(r"[:\\/?*\[\]]", "_", str(name)).strip()

    if not cleaned:
        cleaned = "Sheet"

    cleaned = cleaned[:31]

    base = cleaned
    counter = 1

    while cleaned in used_names:
        suffix = f"_{counter}"
        cleaned = base[:31 - len(suffix)] + suffix
        counter += 1

    used_names.add(cleaned)
    return cleaned


def sanitize_filename(name: str) -> str:
    """
    Make a safe filename for plot output.
    """

    cleaned = re.sub(r'[<>:"/\\|?*\[\]]', "_", str(name)).strip()
    cleaned = re.sub(r"\s+", "_", cleaned)

    if not cleaned:
        cleaned = "sheet"

    return cleaned


def dataframe_to_points(df: pd.DataFrame, sheet_name: str) -> List[Point]:
    """
    Uses the first two columns as X and Y.
    """

    if df.shape[1] < 2:
        raise ValueError(
            f"Sheet '{sheet_name}' must contain at least two columns: X and Y"
        )

    points = [
        (float(df.iloc[i, 0]), float(df.iloc[i, 1]))
        for i in range(len(df))
    ]

    return points


def plot_solution(
    df: pd.DataFrame,
    sheet_name: str,
    output_path: Path,
) -> None:
    """
    Creates a scatter plot:
    - gray = Weight 1
    - red = Weight 3
    """

    if "Weight" not in df.columns:
        raise ValueError("DataFrame must contain a Weight column before plotting")

    x_col = df.columns[0]
    y_col = df.columns[1]

    weight_1 = df[df["Weight"] == 1]
    weight_3 = df[df["Weight"] == 3]

    plt.figure(figsize=(10, 8))

    plt.scatter(
        weight_1[x_col],
        weight_1[y_col],
        s=8,
        alpha=0.35,
        color="gray",
        label="Weight 1",
    )

    plt.scatter(
        weight_3[x_col],
        weight_3[y_col],
        s=18,
        alpha=0.9,
        color="red",
        label="Weight 3",
    )

    plt.xlabel(str(x_col))
    plt.ylabel(str(y_col))
    plt.title(f"Points Colored by Final Weight - {sheet_name}")
    plt.grid(True)
    plt.legend()

    output_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close()


def solve_one_sheet(
    sheet_name: str,
    df: pd.DataFrame,
    config: GRASPConfig,
) -> Tuple[pd.DataFrame, Dict]:
    """
    Runs the solver on one Excel sheet.
    """

    points = dataframe_to_points(df, sheet_name)

    result = solve_grasp(points, config)

    weights = result["weights"]
    W = result["W"]

    validate_or_raise(points, weights, W)

    output_df = df.copy()
    output_df["Weight"] = weights

    return output_df, result


def main() -> None:
    parser = argparse.ArgumentParser()

    parser.add_argument("input_excel", help="Path to input Excel workbook")
    parser.add_argument("output_excel", help="Path to output Excel workbook")

    parser.add_argument("--iterations", type=int, default=5)
    parser.add_argument("--rcl-size", type=int, default=30)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--time-limit", type=float, default=None)
    parser.add_argument("--quiet", action="store_true")

    parser.add_argument(
        "--plot-dir",
        default="output/plots",
        help="Directory where per-sheet plots will be saved",
    )

    args = parser.parse_args()

    input_path = Path(args.input_excel)
    output_path = Path(args.output_excel)
    plot_dir = Path(args.plot_dir)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    plot_dir.mkdir(parents=True, exist_ok=True)

    excel_file = pd.ExcelFile(input_path)
    sheet_names = excel_file.sheet_names

    if not sheet_names:
        raise ValueError("Input Excel file contains no sheets")

    summary_rows = []
    used_output_sheet_names = set()

    base_config = GRASPConfig(
        iterations=args.iterations,
        rcl_size=args.rcl_size,
        seed=args.seed,
        time_limit_seconds=args.time_limit,
        verbose=not args.quiet,
    )

    with pd.ExcelWriter(output_path, engine="openpyxl") as writer:
        for sheet_index, sheet_name in enumerate(sheet_names):
            print()
            print("=" * 80)
            print(f"Running sheet {sheet_index + 1}/{len(sheet_names)}: {sheet_name}")
            print("=" * 80)

            df = pd.read_excel(input_path, sheet_name=sheet_name)

            # Different seed per sheet, while still reproducible.
            sheet_config = GRASPConfig(
                iterations=base_config.iterations,
                rcl_size=base_config.rcl_size,
                seed=base_config.seed + sheet_index,
                time_limit_seconds=base_config.time_limit_seconds,
                verbose=base_config.verbose,
            )

            output_df, result = solve_one_sheet(
                sheet_name=sheet_name,
                df=df,
                config=sheet_config,
            )

            safe_sheet_name = sanitize_sheet_name(sheet_name, used_output_sheet_names)

            output_df.to_excel(
                writer,
                sheet_name=safe_sheet_name,
                index=False,
            )

            plot_filename = sanitize_filename(sheet_name) + ".png"
            plot_path = plot_dir / plot_filename

            plot_solution(
                df=output_df,
                sheet_name=sheet_name,
                output_path=plot_path,
            )

            summary_rows.append(
                {
                    "Input Sheet": sheet_name,
                    "Output Sheet": safe_sheet_name,
                    "Rows": len(output_df),
                    "W": result["W"],
                    "Score": result["score"],
                    "Upgraded Points": result["upgraded_count"],
                    "Max Weighted Chain": result["max_weighted_chain"],
                    "Terminal": result["terminal"],
                    "Iterations Done": result["iterations_done"],
                    "Runtime Seconds": round(result["runtime_seconds"], 3),
                    "Plot": str(plot_path),
                }
            )

        summary_df = pd.DataFrame(summary_rows)

        # Optional summary tab inside the result workbook.
        summary_sheet_name = sanitize_sheet_name("Summary", used_output_sheet_names)
        summary_df.to_excel(
            writer,
            sheet_name=summary_sheet_name,
            index=False,
        )

    print()
    print("=" * 80)
    print("Finished all sheets.")
    print("=" * 80)

    summary_df = pd.DataFrame(summary_rows)
    print(summary_df.to_string(index=False))

    print()
    print(f"Output workbook written to: {output_path}")
    print(f"Plots written to: {plot_dir}")


if __name__ == "__main__":
    main()
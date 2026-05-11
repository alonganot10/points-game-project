import argparse
import pandas as pd
import matplotlib.pyplot as plt


def plot_points(input_excel: str, output_image: str | None = None) -> None:
    df = pd.read_excel(input_excel)

    if df.shape[1] < 2:
        raise ValueError("Excel file must have at least two columns: X and Y")

    x_col = df.columns[0]
    y_col = df.columns[1]

    plt.figure(figsize=(10, 8))

    if "Weight" not in df.columns:
        plt.scatter(
            df[x_col],
            df[y_col],
            s=8,
            alpha=0.6,
            color="blue",
            label="Points",
        )
    else:
        weight_1 = df[df["Weight"] == 1]
        weight_3 = df[df["Weight"] == 3]

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

    plt.xlabel("X")
    plt.ylabel("Y")
    plt.title("Points Colored by Final Weight")
    plt.grid(True)
    plt.legend()

    if output_image:
        plt.savefig(output_image, dpi=300, bbox_inches="tight")
        print(f"Saved graph to {output_image}")
    else:
        plt.show()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("input_excel", help="Path to Excel file")
    parser.add_argument("--output", default=None, help="Optional output image path")

    args = parser.parse_args()

    plot_points(args.input_excel, args.output)


if __name__ == "__main__":
    main()
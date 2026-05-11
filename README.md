# Points Chain Weight Optimization Project

This project solves a geometric optimization game on a set of 2D points.

Given a set of points `(x, y)`, a point `p2` dominates another point `p1` if:

```text
p2.x > p1.x
p2.y > p1.y
```

A valid chain is a sequence of points where every point dominates the previous one.

Initially, every point has weight `1`.

The goal is to change as many point weights as possible from `1` to `3`, while keeping the maximum weighted chain value no larger than the original maximum chain length `W`.

The final output is an Excel file with a third column:

```text
Weight
```

where each value is either `1` or `3`.

---

## Project Goal

For each input Excel file containing points:

```text
X | Y
```

produce an output Excel file:

```text
X | Y | Weight
```

such that:

1. `Weight` is either `1` or `3`.
2. The maximum weighted chain is still at most `W`.
3. The solution is terminal: no additional point can be changed from `1` to `3` without violating the constraint.
4. The total sum of weights is as large as possible according to the implemented heuristic.

---

## Algorithm Overview

The project uses a GRASP-based heuristic:

```text
GRASP = Greedy Randomized Adaptive Search Procedure
```

Each iteration builds a feasible solution by repeatedly selecting points to upgrade from weight `1` to weight `3`.

At each step:

1. Compute the current longest weighted chain passing through each point.
2. Find points whose upgrade would still keep the solution feasible.
3. Score legal candidates according to their available slack.
4. Build a Restricted Candidate List, or RCL.
5. Randomly choose one candidate from the RCL.
6. Upgrade it to weight `3`.
7. Continue until no more legal upgrades exist.

The best solution over all iterations is returned.

---

## Important Definitions

### Dominance

Point `a = (x1, y1)` is before point `b = (x2, y2)` in a chain if:

```text
x1 < x2
y1 < y2
```

### W

`W` is the length of the longest chain when all point weights are `1`.

### Weighted Chain

If points have weights `1` or `3`, the weight of a chain is the sum of the weights of the points in that chain.

A solution is feasible only if:

```text
maximum weighted chain <= W
```

---

## Implementation Details

The expensive chain dynamic programming code is implemented in C++ using `pybind11`.

Python is used for:

- Reading Excel files
- Running the GRASP heuristic
- Validating the result
- Writing the output Excel file
- Plotting the points

C++ is used for:

- Computing `W`
- Computing longest weighted chains
- Computing chain values through each point

This gives better performance than pure Python.

---

## Project Structure

```text
project/
│
├── main.py              # Main entry point
├── solver.py            # GRASP heuristic
├── validator.py         # Feasibility and terminal-state validation
├── chain.py             # Python wrapper for the C++ extension
├── chain_cpp.cpp        # C++ implementation of chain DP
├── setup.py             # Builds the C++ extension
├── plot_points.py       # Optional visualization script
├── requirements.txt
│
├── input/
│   └── points.xlsx
│
└── output/
    └── result.xlsx
```

---

## Requirements

Python 3.10 or newer is recommended.

Python packages:

```text
pandas
openpyxl
pybind11
setuptools
wheel
matplotlib
```

On Windows, building the C++ extension requires:

```text
Microsoft C++ Build Tools
```

During installation, select:

```text
Desktop development with C++
```

Make sure the following components are installed:

```text
MSVC C++ build tools
Windows SDK
C++ CMake tools for Windows
```

---

## Setup

Create and activate a virtual environment:

```powershell
py -m venv .venv
```

```powershell
.\.venv\Scripts\Activate.ps1
```

Install dependencies:

```powershell
pip install -r requirements.txt
```

If `requirements.txt` does not exist yet:

```powershell
pip install pandas openpyxl pybind11 setuptools wheel matplotlib
```

Then save dependencies:

```powershell
pip freeze > requirements.txt
```

---

## Build the C++ Extension

Run this from the project root:

```powershell
python setup.py build_ext --inplace
```

After a successful build, a compiled file should appear, for example:

```text
chain_cpp.cp312-win_amd64.pyd
```

The exact filename may differ depending on your Python version and operating system.

---

## Quick Test

After building the C++ extension, run:

```powershell
python -c "import chain; print(chain.compute_W([(1,1),(2,2),(3,3)]))"
```

Expected output:

```text
3
```

Test weighted chain computation:

```powershell
python -c "import chain; print(chain.max_weighted_chain([(1,1),(2,2),(3,3)], [1,3,1]))"
```

Expected output:

```text
5
```

---

## Running the Solver

Place the input Excel file inside the `input/` folder.

Example:

```text
input/points.xlsx
```

Run:

```powershell
python main.py input/points.xlsx output/result.xlsx --iterations 5 --rcl-size 30 --seed 42
```

With a time limit:

```powershell
python main.py input/points.xlsx output/result.xlsx --iterations 100 --rcl-size 30 --seed 42 --time-limit 60
```

---

## Command-Line Arguments

### `input_excel`

Path to the input Excel file.

### `output_excel`

Path where the result Excel file will be saved.

### `--iterations`

Number of GRASP iterations.

Default:

```text
5
```

### `--rcl-size`

Size of the Restricted Candidate List.

Default:

```text
30
```

### `--seed`

Random seed for reproducibility.

Default:

```text
42
```

### `--time-limit`

Optional runtime limit in seconds.

### `--quiet`

Reduces printed output.

---

## Output

The solver creates an Excel file with a new column:

```text
Weight
```

Example:

```text
X | Y | Weight
```

Each point receives one of the following values:

```text
1
3
```

A weight of `3` means the point was upgraded by the algorithm.

---

## Plotting the Result

To visualize the output:

```powershell
python plot_points.py output/result.xlsx
```

To save the plot as an image:

```powershell
python plot_points.py output/result.xlsx --output output/points_colored.png
```

The plot shows:

```text
gray = Weight 1
red  = Weight 3
```

---

## Validation

The program validates the final solution before writing the result.

A solution is accepted only if:

```text
maximum weighted chain <= W
```

and the terminal-state check confirms that no additional point with weight `1` can be upgraded to `3`.

If validation fails, the program raises an error instead of silently producing an invalid output.

---

## Notes About Performance

The main bottleneck is repeatedly computing longest weighted chains during the GRASP construction phase.

To improve performance, the project uses a C++ implementation of the chain dynamic programming logic.

The solver still performs many calls to the chain calculation, so runtime depends on:

- Number of points
- Number of GRASP iterations
- RCL size
- Number of legal upgrades found
- Time limit

For large inputs, start with:

```powershell
python main.py input/points.xlsx output/result.xlsx --iterations 1 --rcl-size 20 --time-limit 60
```

Then increase the parameters gradually.

---

## Example Full Workflow

```powershell
py -m venv .venv
```

```powershell
.\.venv\Scripts\Activate.ps1
```

```powershell
pip install -r requirements.txt
```

```powershell
python setup.py build_ext --inplace
```

```powershell
python main.py input/points.xlsx output/result.xlsx --iterations 5 --rcl-size 30 --seed 42
```

```powershell
python plot_points.py output/result.xlsx --output output/points_colored.png
```

---

## Minimal `requirements.txt`

```text
pandas
openpyxl
pybind11
setuptools
wheel
matplotlib
```

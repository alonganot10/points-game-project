# Points Chain Weight Optimization Project

This project solves a stochastic optimization / heuristic game on a set of 2D points.

Given a set of points in the plane, the program assigns each point a final weight of either `1` or `3`.
The goal is to maximize the total sum of weights while keeping the maximum weighted chain no larger than the original maximum chain length `W`.

---

## Problem Description

A point `(x2, y2)` dominates another point `(x1, y1)` if:

```text
x2 > x1 and y2 > y1
```

A chain is a sequence of points where every point dominates the previous one.

At the start of the game, every point has weight `1`.

Let:

```text
W = maximum chain length when all weights are 1
```

During the game, a move changes one point's weight from `1` to `3`.

A move is legal only if after the change:

```text
maximum weighted chain <= W
```

The objective is to reach a terminal state with the largest possible total weight.

---

## Input Format

The input is an Excel file with two columns:

```text
X | Y
```

Each row represents one point.

Example:

```text
X    Y
1    5
2    3
7    9
```

---

## Output Format

The output is an Excel file with an added third column:

```text
X | Y | Weight
```

Where:

```text
Weight = 1 or 3
```

Example:

```text
X    Y    Weight
1    5    3
2    3    1
7    9    1
```

---

## Project Structure

```text
project/
│
├── main.py           # Main program entry point
├── solver.py         # GRASP heuristic solver
├── chain.py          # Chain DP calculations
├── validator.py      # Feasibility and terminal-state checks
├── plot_points.py    # Graphing utility
├── requirements.txt  # Python dependencies
│
├── input/            # Input Excel files
├── output/           # Output Excel files and plots
└── report/           # Project report files
```

---

## Algorithm Overview

The project uses a GRASP-based heuristic:

```text
GRASP = Greedy Randomized Adaptive Search Procedure
```

Each iteration:

1. Computes the original maximum chain length `W`.
2. Starts with all weights equal to `1`.
3. Finds candidate points that can potentially be upgraded to weight `3`.
4. Repeatedly chooses legal candidates using a randomized greedy rule.
5. Stops when no more legal upgrades are found.
6. Keeps the best solution across all iterations.

A solution is feasible if:

```text
maximum weighted chain <= W
```

The score of a solution is:

```text
sum of all point weights
```

Since weights are only `1` or `3`, maximizing the score is equivalent to maximizing the number of points upgraded to `3`.

---

## Installation

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
pip install pandas openpyxl numpy numba matplotlib
```

Then save dependencies:

```powershell
pip freeze > requirements.txt
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

```text
input_excel       Path to the input Excel file
output_excel      Path to the output Excel file

--iterations      Number of GRASP iterations
--rcl-size        Size of the Restricted Candidate List
--seed            Random seed for reproducibility
--time-limit      Optional runtime limit in seconds
--quiet           Disable verbose printing
```

Example:

```powershell
python main.py input/points.xlsx output/result.xlsx --iterations 10 --rcl-size 50 --seed 7 --time-limit 120
```

---

## Plotting the Result

To graph the points after solving:

```powershell
python plot_points.py output/result.xlsx
```

To save the graph as an image:

```powershell
python plot_points.py output/result.xlsx --output output/points_colored.png
```

The plot colors points by final weight:

```text
gray = Weight 1
red  = Weight 3
```

---

## Validation

After solving, the program validates that:

1. Every point has weight `1` or `3`.
2. The maximum weighted chain is at most `W`.
3. The final state is terminal.

A terminal state means there is no remaining point with weight `1` that can be changed to `3` without violating the chain constraint.

---

## Performance Notes

The expensive operation is computing the maximum weighted chain and the chain-through value for all points.

The project supports a faster `chain.py` implementation using:

```text
NumPy + Numba
```

This avoids the need for a C++ compiler while still improving performance compared to pure Python.

The first run may be slower because Numba compiles the functions. Later runs should be faster due to caching.

---

## Example Output

After running the solver, the terminal prints information such as:

```text
W = 120
Initial possible candidates = 4380
Iteration 1: score=14852, upgraded=2426, max_chain=120
Finished.
W = 120
Score = 14852
Upgraded points = 2426
Max weighted chain = 120
Terminal = True
Runtime seconds = 34.217
Output written to: output/result.xlsx
```

---

## Git Usage

Clone the repository:

```powershell
git clone https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
```

Enter the project folder:

```powershell
cd YOUR_REPO_NAME
```

Create a virtual environment:

```powershell
py -m venv .venv
```

Activate it:

```powershell
.\.venv\Scripts\Activate.ps1
```

Install dependencies:

```powershell
pip install -r requirements.txt
```

Run the project:

```powershell
python main.py input/points.xlsx output/result.xlsx --iterations 5 --rcl-size 30 --seed 42
```

---

## Current Limitations

This solver is heuristic.

It does not guarantee the mathematically optimal solution.

The main goal is to produce:

1. A valid solution.
2. A terminal solution.
3. A high total weight.
4. Reasonable runtime on inputs with around 10,000 points.

---

## Authors

Project for Topics in Stochastic Optimization.

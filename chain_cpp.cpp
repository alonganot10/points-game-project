#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

#include <algorithm>
#include <stdexcept>
#include <tuple>
#include <utility>
#include <vector>

namespace py = pybind11;

using Point = std::pair<double, double>;

class FenwickMax {
private:
    int size;
    std::vector<int> tree;

public:
    explicit FenwickMax(int n) : size(n), tree(n + 1, 0) {}

    void update(int index, int value) {
        while (index <= size) {
            if (value > tree[index]) {
                tree[index] = value;
            }
            index += index & -index;
        }
    }

    int query(int index) const {
        int result = 0;

        while (index > 0) {
            if (tree[index] > result) {
                result = tree[index];
            }
            index -= index & -index;
        }

        return result;
    }
};

std::vector<int> chain_dp_forward(
    const std::vector<Point>& points,
    const std::vector<int>& weights
) {
    int n = static_cast<int>(points.size());

    if (static_cast<int>(weights.size()) != n) {
        throw std::invalid_argument("points and weights must have the same length");
    }

    std::vector<int> dp(n, 0);

    if (n == 0) {
        return dp;
    }

    // Coordinate compression for y values.
    std::vector<double> y_values;
    y_values.reserve(n);

    for (const auto& p : points) {
        y_values.push_back(p.second);
    }

    std::sort(y_values.begin(), y_values.end());
    y_values.erase(std::unique(y_values.begin(), y_values.end()), y_values.end());

    auto get_y_index = [&](double y) {
        auto it = std::lower_bound(y_values.begin(), y_values.end(), y);
        return static_cast<int>(it - y_values.begin()) + 1;
    };

    // Sort point indices by x ascending, then y ascending.
    std::vector<int> order(n);

    for (int i = 0; i < n; ++i) {
        order[i] = i;
    }

    std::sort(order.begin(), order.end(), [&](int a, int b) {
        if (points[a].first != points[b].first) {
            return points[a].first < points[b].first;
        }
        return points[a].second < points[b].second;
    });

    FenwickMax fenwick(static_cast<int>(y_values.size()));

    int pos = 0;

    while (pos < n) {
        double current_x = points[order[pos]].first;

        std::vector<int> batch;

        while (pos < n && points[order[pos]].first == current_x) {
            batch.push_back(order[pos]);
            ++pos;
        }

        std::vector<std::pair<int, int>> updates;
        updates.reserve(batch.size());

        for (int i : batch) {
            double y = points[i].second;
            int y_idx = get_y_index(y);

            // Strict condition: previous y must be smaller.
            int best_previous = fenwick.query(y_idx - 1);

            dp[i] = best_previous + weights[i];
            updates.push_back({y_idx, dp[i]});
        }

        // Update only after finishing same-x batch.
        // This prevents chaining points with the same x.
        for (const auto& update : updates) {
            fenwick.update(update.first, update.second);
        }
    }

    return dp;
}

int max_weighted_chain(
    const std::vector<Point>& points,
    const std::vector<int>& weights
) {
    std::vector<int> dp = chain_dp_forward(points, weights);

    if (dp.empty()) {
        return 0;
    }

    return *std::max_element(dp.begin(), dp.end());
}

int compute_W(const std::vector<Point>& points) {
    std::vector<int> weights(points.size(), 1);
    return max_weighted_chain(points, weights);
}

std::tuple<std::vector<int>, std::vector<int>, std::vector<int>> compute_LRT(
    const std::vector<Point>& points,
    const std::vector<int>& weights
) {
    int n = static_cast<int>(points.size());

    if (static_cast<int>(weights.size()) != n) {
        throw std::invalid_argument("points and weights must have the same length");
    }

    std::vector<int> L = chain_dp_forward(points, weights);

    std::vector<Point> reversed_points;
    reversed_points.reserve(n);

    for (const auto& p : points) {
        reversed_points.push_back({-p.first, -p.second});
    }

    std::vector<int> R = chain_dp_forward(reversed_points, weights);

    std::vector<int> through(n, 0);

    for (int i = 0; i < n; ++i) {
        through[i] = L[i] + R[i] - weights[i];
    }

    return {L, R, through};
}

PYBIND11_MODULE(chain_cpp, m) {
    m.doc() = "C++ implementation of chain dynamic programming";

    m.def(
        "chain_dp_forward",
        &chain_dp_forward,
        "Compute maximum weighted chain ending at each point"
    );

    m.def(
        "max_weighted_chain",
        &max_weighted_chain,
        "Compute maximum weighted chain value"
    );

    m.def(
        "compute_W",
        &compute_W,
        "Compute longest unweighted chain length"
    );

    m.def(
        "compute_LRT",
        &compute_LRT,
        "Compute L, R, and through arrays"
    );
}
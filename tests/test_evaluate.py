"""Stage 4 tests: paired summary statistics."""
import numpy as np
import pandas as pd
import pytest

from glider_rl.evaluate import summarize
from glider_rl.utils import bootstrap_ci


def _rows(method, seed, maps, success, time, energy):
    return [{"condition": "c", "method": method, "train_seed": seed, "map_seed": m, "success": s,
             "time_s": t, "energy_J": e, "path_m": 1000.0} for m, s, t, e in zip(maps, success, time, energy)]


def test_summary_pairs_on_common_maps_and_ratios():
    maps = [1, 2, 3]
    rows = _rows("straight", -1, maps, [True, True, False], [3600, 7200, 0], [100, 200, 0])
    rows += _rows("rl", 0, maps, [True, True, True], [1800, 3600, 3600], [50, 300, 10])
    rows += _rows("rl", 1, maps, [True, False, True], [3600, 3600, 3600], [100, 300, 10])
    s = summarize(pd.DataFrame(rows), n_boot=200).set_index("method")
    assert s.loc["straight", "n_common_maps"] == 1          # only map 1 solved by everyone
    assert s.loc["rl", "success_mean"] == pytest.approx((1.0 + 2 / 3) / 2)
    assert s.loc["rl", "time_h_mean"] == pytest.approx(0.75)  # seeds: 0.5 h and 1.0 h on map 1
    assert s.loc["straight", "time_h_mean"] == pytest.approx(1.0)
    # energy ratio, seed 0: maps 1,2 -> (0.5 + 1.5)/2 = 1.0 ; seed 1: map 1 -> 1.0
    assert s.loc["rl", "energy_ratio_mean"] == pytest.approx(1.0)
    assert s.loc["straight", "energy_ratio_mean"] == pytest.approx(1.0)
    assert s.loc["straight", "success_std"] == 0.0


def test_bootstrap_ci_contains_mean_and_shrinks():
    rng = np.random.default_rng(0)
    small, big = rng.normal(0, 1, 20), rng.normal(0, 1, 2000)
    lo, hi = bootstrap_ci(small)
    assert lo < small.mean() < hi
    lo2, hi2 = bootstrap_ci(big)
    assert (hi2 - lo2) < (hi - lo)

"""Test case 1: Monte Carlo estimation of pi."""
import numpy as np


def compute(n_samples: int = 2_000_000, seed: int = 42) -> float:
    # NOTE: We generate the points only once—deterministically, using a fixed seed.
    # If each parallel worker generates its own random values ​​instead of sharing
    # this same array, you will be comparing two different random runs, and
    # numerical verification will fail even if the parallelization is implemented correctly.
    rng = np.random.default_rng(seed)
    points = rng.random((n_samples, 2))
    inside = 0
    for x, y in points:
        if x * x + y * y <= 1.0:
            inside += 1
    return 4.0 * inside / n_samples
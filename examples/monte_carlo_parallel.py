import numpy as np
from joblib import Parallel, delayed
import os

def _count_inside(points: np.ndarray) -> int:
    inside = 0
    for x, y in points:
        if x * x + y * y <= 1.0:
            inside += 1
    return inside

def compute_parallel(
    n_samples: int = 2_000_000,
    seed: int = 42,
    n_jobs: int = -1
) -> float:
    rng = np.random.default_rng(seed)
    points = rng.random((n_samples, 2))

    if n_jobs == -1:
        n_jobs = os.cpu_count() or 4
    n_jobs = max(1, n_jobs)

    chunks = np.array_split(points, n_jobs)

    inside_counts = Parallel(n_jobs=n_jobs)(
        delayed(_count_inside)(chunk) for chunk in chunks
    )

    return 4.0 * sum(inside_counts) / n_samples
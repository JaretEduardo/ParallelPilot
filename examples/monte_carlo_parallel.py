import numpy as np
import multiprocessing as mp
import os

try:
    mp.set_start_method('fork', force=True)
except RuntimeError:
    pass

def _count_inside(points_chunk):
    inside = 0
    for x, y in points_chunk:
        if x*x + y*y <= 1.0:
            inside += 1
    return inside

def compute_parallel(n_samples=2_000_000, seed=42, n_jobs=-1):
    rng = np.random.default_rng(seed)
    points = rng.random((n_samples, 2))
    if n_jobs == -1:
        n_jobs = os.cpu_count() or 4
    n_jobs = max(1, n_jobs)
    chunks = np.array_split(points, n_jobs)
    with mp.Pool(n_jobs) as pool:
        results = pool.map(_count_inside, chunks)
    return 4.0 * sum(results) / n_samples
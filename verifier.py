from __future__ import annotations
import math
from typing import Any

try:
    import numpy as np
except ImportError:
    np = None


def results_match(serial_result: Any, parallel_result: Any, tolerance: float = 1e-6) -> tuple[bool, str]:
    try:
        if np is not None and (isinstance(serial_result, np.ndarray) or isinstance(parallel_result, np.ndarray)):
            a, b = np.asarray(serial_result, dtype=float), np.asarray(parallel_result, dtype=float)
            if a.shape != b.shape:
                return False, f"Different shapes: serial={a.shape} vs parallel={b.shape}"
            if np.allclose(a, b, atol=tolerance, rtol=tolerance):
                return True, "Match within tolerance (numpy.allclose)."
            diff = np.abs(a - b)
            return False, f"Maximum difference {diff.max():.3e} exceeds tolerance {tolerance:.1e}."

        if isinstance(serial_result, (list, tuple)) and isinstance(parallel_result, (list, tuple)):
            if len(serial_result) != len(parallel_result):
                return False, f"Different lengths: {len(serial_result)} vs {len(parallel_result)}"
            for i, (a, b) in enumerate(zip(serial_result, parallel_result)):
                if not math.isclose(a, b, rel_tol=tolerance, abs_tol=tolerance):
                    return False, f"Differ at index {i}: {a} vs {b}"
            return True, "Match element-wise (math.isclose)."

        if not math.isclose(float(serial_result), float(parallel_result), rel_tol=tolerance, abs_tol=tolerance):
            return False, f"Different scalars: {serial_result} vs {parallel_result}"
        return True, "Match within tolerance (math.isclose)."
    except Exception as e:
        return False, f"Could not compare automatically: {e!r}"
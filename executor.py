from __future__ import annotations
import importlib.util, sys, time, traceback
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable


@dataclass
class ExecutionResult:
    ok: bool
    result: Any = None
    elapsed_seconds: float = 0.0
    error: str | None = None
    traceback: str | None = None


def load_function(file_path: str | Path, function_name: str) -> Callable:
    file_path = Path(file_path).resolve()
    module_name = f"parallel_module_{file_path.stem}"
    
    if module_name in sys.modules:
        module = sys.modules[module_name]
        if hasattr(module, function_name):
            return getattr(module, function_name)
    
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Could not load {file_path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    
    if not hasattr(module, function_name):
        raise AttributeError(f"{file_path} does not define '{function_name}'")
    return getattr(module, function_name)


def run_timed(func: Callable, args: tuple = (), kwargs: dict | None = None) -> ExecutionResult:
    kwargs = kwargs or {}
    start = time.perf_counter()
    try:
        result = func(*args, **kwargs)
        return ExecutionResult(True, result, time.perf_counter() - start)
    except Exception as e:
        return ExecutionResult(False, elapsed_seconds=time.perf_counter() - start,
                                error=str(e), traceback=traceback.format_exc())


def run_with_cores(func: Callable, cores: int, args: tuple, kwargs: dict | None = None) -> ExecutionResult:
    kwargs = dict(kwargs or {})
    kwargs["n_jobs"] = cores
    return run_timed(func, args, kwargs)
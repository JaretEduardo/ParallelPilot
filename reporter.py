from __future__ import annotations
import os
from dataclasses import dataclass

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from openai import OpenAI


@dataclass
class BenchmarkPoint:
    cores: int
    elapsed_seconds: float


def render_table(serial_time: float, points: list[BenchmarkPoint]) -> str:
    lines = [f"{'Cores':>10} | {'Time (s)':>12} | {'Speedup':>8}", "-" * 36,
              f"{'1 (serial)':>10} | {serial_time:>12.4f} | {'1.00x':>8}"]
    for p in points:
        lines.append(f"{p.cores:>10} | {p.elapsed_seconds:>12.4f} | {serial_time / p.elapsed_seconds:>7.2f}x")
    return "\n".join(lines)


def render_speedup_chart(serial_time: float, points: list[BenchmarkPoint], output_path: str) -> str:
    cores = [p.cores for p in points]
    speedups = [serial_time / p.elapsed_seconds for p in points]
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.plot(cores, speedups, marker="o", linewidth=2, label="actual speedup")
    ax.plot(cores, cores, linestyle="--", color="gray", label="ideal speedup")
    ax.set_xlabel("Cores"); ax.set_ylabel("Speedup"); ax.set_title("ParallelPilot — speedup vs. cores")
    ax.legend(); ax.grid(alpha=0.3); fig.tight_layout()
    fig.savefig(output_path, dpi=150); plt.close(fig)
    return output_path


def summarize_with_gpt56(serial_time: float, points: list[BenchmarkPoint], tolerance_ok: bool,
                          model: str = "gpt-5.6-terra") -> str:
    """Use YOUR own API key (OPENAI_API_KEY) — does not touch Codex credits."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return "(OPENAI_API_KEY not set; summary skipped.)"

    client = OpenAI(api_key=api_key)
    best = max(points, key=lambda p: serial_time / p.elapsed_seconds)
    prompt = f"""You are an HPC engineer. Data from a parallelization benchmark:

Serial time: {serial_time:.4f}s
Numerical verification: {"correct" if tolerance_ok else "FAILED"}
{render_table(serial_time, points)}
Best speedup: {serial_time / best.elapsed_seconds:.2f}x with {best.cores} cores.

Write a concise technical summary of 3-4 lines in English interpreting the result
(do not repeat the table)."""

    response = client.responses.create(
        model=model,
        reasoning={"effort": "low"},
        instructions="You are a concise technical assistant specialized in HPC.",
        input=prompt,
    )
    return response.output_text
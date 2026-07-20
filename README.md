# ParallelPilot

ParallelPilot is a command-line tool that automates the parallelization of serial Python code using OpenAI Codex and GPT-5.6, then validates correctness, benchmarks performance, and generates a speedup report with both a table and a Matplotlib chart.

## Description

ParallelPilot is designed for benchmark-driven parallelization workflows. Given a serial Python script, it can ask Codex to generate a parallel version, verify that the parallel implementation matches the serial output within a configurable tolerance, and measure runtime across multiple core counts.

The project also supports a pre-generated parallel file, which is useful when you want to skip Codex at runtime and benchmark an already-created parallel implementation.

## Features

- Parallel code generation with Codex using the built-in prompt templates.
- Optional manual workflow with `--parallel-file` to reuse a pre-generated parallel script.
- Numerical verification using `numpy` when available, with a `math` fallback for scalar and sequence comparisons.
- Timed execution of serial and parallel functions.
- Benchmarking across multiple core counts, such as `1,2,4,8`.
- Speedup table rendering and chart generation with Matplotlib.
- Optional GPT-5.6 textual summary when `OPENAI_API_KEY` is configured.

## Installation

### Requirements

- Python 3.10 or higher
- A virtual environment is strongly recommended
- Dependencies listed in `requirements.txt`

### Setup

1. Clone the repository.

   ```bash
   git clone https://github.com/JaretEduardo/ParallelPilot.git
   cd ParallelPilot
   ```

2. Create and activate a virtual environment.

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. Install the dependencies.

   ```bash
   pip install -r requirements.txt
   ```

4. Configure environment variables.

   Copy the example file and set the required keys:

   ```bash
   cp .env.example .env
   ```

   Then set the following values as needed:

   - `CODEX_API_KEY` for Codex-based generation
   - `OPENAI_API_KEY` for the optional GPT-5.6 summary

## Usage

ParallelPilot expects a serial Python file and the name of the function to benchmark. The default function name is `compute`.

### Basic example

```bash
python parallelpilot.py examples/monte_carlo.py --cores 1,2,4,8 --parallel-file examples/monte_carlo_parallel.py
```

This command:

- Executes the serial implementation.
- Loads the pre-generated parallel file.
- Verifies that the parallel result matches the serial result.
- Benchmarks the parallel function across the requested core counts.
- Writes a speedup chart to `examples/parallelpilot_speedup.png`.

### Generating parallel code with Codex

If you omit `--parallel-file`, ParallelPilot invokes Codex to generate the parallel implementation automatically.

```bash
python parallelpilot.py examples/monte_carlo.py --cores 1,2,4,8
```

### Useful options

```bash
python parallelpilot.py PATH_TO_SCRIPT \
  --function compute \
  --cores 1,2,4,8 \
  --tolerance 1e-6 \
  --model gpt-5.6-sol \
  --parallel-file PATH_TO_PARALLEL_FILE
```

- `--function` specifies the serial function name to load.
- `--cores` defines the benchmark core counts.
- `--tolerance` controls numerical comparison strictness.
- `--model` selects the Codex model used for generation.
- `--parallel-file` bypasses runtime Codex generation and reuses an existing parallel script.

## Project Structure

| File | Purpose |
| --- | --- |
| `parallelpilot.py` | Typer-based CLI entry point and workflow orchestration. |
| `codex_client.py` | Codex SDK client and CLI fallback client. |
| `executor.py` | Dynamic function loading and timed execution helpers. |
| `verifier.py` | Numerical comparison utilities using `numpy` or `math`. |
| `reporter.py` | Table rendering, chart generation, and optional GPT-5.6 summary. |
| `prompt_templates.py` | Prompt templates used to guide Codex. |
| `requirements.txt` | Python dependency list. |
| `.env.example` | Environment variable template. |
| `examples/monte_carlo.py` | Serial Monte Carlo pi estimation example. |
| `examples/monte_carlo_parallel.py` | Parallel implementation generated for the example. |

## Example Output

When the example script is run with the pre-generated parallel implementation, the report may include results similar to the following:

| Cores | Time (s) | Speedup |
| --- | ---: | ---: |
| 1 (serial) | 1.3605 | 1.00x |
| 1 | 1.3514 | 1.01x |
| 2 | 0.6823 | 1.99x |
| 4 | 0.3512 | 3.87x |
| 8 | 0.1897 | 7.17x |

The generated chart is saved as `examples/parallelpilot_speedup.png`. It compares actual speedup against ideal linear scaling and makes it easy to see where the implementation approaches or diverges from perfect parallel efficiency.

## Troubleshooting

- If the CLI cannot load your script, confirm that the file exists and that the function named by `--function` is defined at module scope.
- If verification fails, review the parallel implementation to ensure it preserves the same input, output, and random-seed behavior as the serial version.
- If `numpy` is unavailable, ParallelPilot still works for scalar and sequence comparisons, but array comparisons are more robust with `numpy` installed.
- If the summary step is skipped, set `OPENAI_API_KEY` in `.env`.
- If Codex generation fails, verify that your Codex credentials are configured and that the Codex CLI is available in your environment.
- If Matplotlib cannot write the chart, confirm that the output directory is writable.

## License

This project is licensed under the MIT License.

## Acknowledgements

- OpenAI, for the Codex and GPT-5.6 tooling that powers the generation and summary workflow.
- Devpost, for the hackathon platform and project showcase context.

## Contact

- GitHub: [JaretEduardo](https://github.com/JaretEduardo)
- Devpost: [Add your Devpost profile](https://devpost.com/)

If you are the repository owner, replace the Devpost link above with your personal profile URL.

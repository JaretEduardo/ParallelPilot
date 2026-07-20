# prompt_templates.py
PARALLELIZATION_PROMPT_TEMPLATE = """Read `{target_file}` in this repository. It contains `{function_name}`,
a function with optional parameters that returns a numeric result.

Task:
1. Create `{output_file}` in the same directory.
2. Implement `{function_name}_parallel` that accepts EXACTLY the same
   parameters as `{function_name}`, plus `n_jobs: int = -1`.
3. It must reproduce any data-generation steps (e.g. random numbers)
   IDENTICALLY to the original version — only parallelize the heavy
   computation over those already-generated data, using joblib.Parallel and
   joblib.delayed. The inner parallelized function must be pure.
4. Do not modify `{target_file}`. Only valid Python code in the new file
   (comments inside the code are fine).
5. When finished, briefly confirm what you did (do not repeat the code in your response)."""

FIX_PROMPT_TEMPLATE = """Verification of `{output_file}` failed:
{error_detail}

Fix `{output_file}` to address this specific issue. Do not change the
signature of `{function_name}_parallel`. Briefly confirm when done."""
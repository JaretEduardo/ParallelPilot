PROMPT_PARALLELIZATION = """
You are an expert in Python and parallelization with joblib.
Transform the following serial `for` loop into a parallel version
using `joblib.Parallel` and `joblib.delayed`. Follow these rules:

- The inner function must be pure: all inputs are passed as arguments.
- Do not use global variables.
- The numeric result must be identical within floating-point tolerance.
- Include basic error handling (try/except) in each iteration.
- Return **only the final Python code**, without explanations, without markdown,
  just the source ready to run.

Original code (loop to parallelize):
```python
{codigo}
Parallelized code:
"""
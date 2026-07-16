PROMPT_PARALELIZACION = """
Eres un experto en Python y paralelización con joblib.
Transforma el siguiente bucle `for` serial en una versión paralela
usando `joblib.Parallel` y `joblib.delayed`. Sigue estas reglas:

- La función interna debe ser pura: todas las entradas se pasan como argumentos.
- No uses variables globales.
- El resultado numérico debe ser idéntico (a nivel de tolerancia de punto flotante).
- Incluye un manejo básico de errores (try/except) en cada iteración.
- Devuelve **solo el código Python final**, sin explicaciones, sin markdown,
  directamente la fuente lista para ejecutarse.

Código original (bucle a paralelizar):
```python
{codigo}
Código paralelizado:
"""
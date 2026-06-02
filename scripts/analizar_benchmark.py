import pandas as pd

INPUT_CSV = "benchmark_modelos.csv"
OUTPUT_CSV = "resumen_benchmark_modelos.csv"

# Cargar resultados
results = pd.read_csv(INPUT_CSV)

# Convertir columnas numéricas
numeric_columns = [
    "total_duration_s",
    "wall_time_s",
    "load_duration_s",
    "prompt_eval_count",
    "eval_count",
    "eval_duration_s",
    "tokens_per_second",
    "response_chars",
    "quality_score",
]

for column in numeric_columns:
    results[column] = pd.to_numeric(results[column], errors="coerce")

# Resumen estadístico por modelo
summary = results.groupby("model").agg({
    "total_duration_s": ["mean", "std", "min", "max"],
    "prompt_eval_count": ["mean"],
    "eval_count": ["mean", "std", "min", "max"],
    "tokens_per_second": ["mean", "std", "min", "max"],
    "response_chars": ["mean", "std"],
    "quality_score": ["mean", "std", "min", "max"],
})

# Aplanar encabezados
summary.columns = ["_".join(col).strip() for col in summary.columns.values]
summary = summary.reset_index()

print("Resumen del benchmark:")
print(summary)

summary.to_csv(OUTPUT_CSV, index=False, encoding="utf-8")
print(f"Resumen guardado en {OUTPUT_CSV}")


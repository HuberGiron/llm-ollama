import csv
import time
from datetime import datetime

import requests

OLLAMA_URL = "http://localhost:11434/api/generate"

MODEL = "llama3.2:3b"

PROMPT = (
    "Explica en máximo 120 palabras qué es un sensor ultrasónico "
    "y cómo podría usarse en un robot móvil educativo."
)

BASE_OPTIONS = {
    "temperature": 0.7,
    "top_p": 0.9,
    "top_k": 40,
    "min_p": 0.0,
    "num_ctx": 4096,
    "num_predict": 160,
    "repeat_penalty": 1.1,
}

PARAMETER_TESTS = {
    "temperature": [0.0, 0.7, 1.1],
    "top_p": [0.7, 0.9, 0.95],
    "repeat_penalty": [1.0, 1.2, 1.5],
}

N_CYCLES = 100
OUTPUT_CSV = "benchmark_parametros.csv"


def run_ollama(model: str, prompt: str, options: dict) -> dict:
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "keep_alive": "30m",
        "options": options,
    }

    start = time.perf_counter()
    response = requests.post(OLLAMA_URL, json=payload, timeout=300)
    end = time.perf_counter()

    response.raise_for_status()
    data = response.json()

    eval_duration_s = data.get("eval_duration", 0) / 1e9
    eval_count = data.get("eval_count", 0)

    return {
        "response": data.get("response", ""),
        "total_duration_s": data.get("total_duration", 0) / 1e9,
        "wall_time_s": end - start,
        "load_duration_s": data.get("load_duration", 0) / 1e9,
        "prompt_eval_count": data.get("prompt_eval_count", 0),
        "eval_count": eval_count,
        "eval_duration_s": eval_duration_s,
        "tokens_per_second": eval_count / eval_duration_s if eval_duration_s > 0 else 0,
    }


fieldnames = [
    "timestamp",
    "experiment_id",
    "model",
    "parameter_changed",
    "parameter_value",
    "cycle",
    "prompt",
    "temperature",
    "top_p",
    "top_k",
    "min_p",
    "num_ctx",
    "num_predict",
    "repeat_penalty",
    "response",
    "total_duration_s",
    "wall_time_s",
    "load_duration_s",
    "prompt_eval_count",
    "eval_count",
    "eval_duration_s",
    "tokens_per_second",
    "response_chars",
    "notes",
]

with open(OUTPUT_CSV, mode="w", newline="", encoding="utf-8") as file:
    writer = csv.DictWriter(file, fieldnames=fieldnames)
    writer.writeheader()

    for parameter, values in PARAMETER_TESTS.items():
        for value in values:
            options = BASE_OPTIONS.copy()
            options[parameter] = value

            for cycle in range(1, N_CYCLES + 1):
                print(f"Parámetro: {parameter}={value} | Ciclo: {cycle}/{N_CYCLES}")

                row = {
                    "timestamp": datetime.now().isoformat(),
                    "experiment_id": "variacion_parametros",
                    "model": MODEL,
                    "parameter_changed": parameter,
                    "parameter_value": value,
                    "cycle": cycle,
                    "prompt": PROMPT,
                    "temperature": options["temperature"],
                    "top_p": options["top_p"],
                    "top_k": options["top_k"],
                    "min_p": options["min_p"],
                    "num_ctx": options["num_ctx"],
                    "num_predict": options["num_predict"],
                    "repeat_penalty": options["repeat_penalty"],
                    "response": "",
                    "total_duration_s": "",
                    "wall_time_s": "",
                    "load_duration_s": "",
                    "prompt_eval_count": "",
                    "eval_count": "",
                    "eval_duration_s": "",
                    "tokens_per_second": "",
                    "response_chars": "",
                    "notes": "",
                }

                try:
                    result = run_ollama(MODEL, PROMPT, options)
                    row.update({
                        "response": result["response"],
                        "total_duration_s": result["total_duration_s"],
                        "wall_time_s": result["wall_time_s"],
                        "load_duration_s": result["load_duration_s"],
                        "prompt_eval_count": result["prompt_eval_count"],
                        "eval_count": result["eval_count"],
                        "eval_duration_s": result["eval_duration_s"],
                        "tokens_per_second": result["tokens_per_second"],
                        "response_chars": len(result["response"]),
                    })

                except Exception as error:
                    row["notes"] = str(error)

                writer.writerow(row)

print(f"Benchmark terminado. Resultados guardados en {OUTPUT_CSV}")

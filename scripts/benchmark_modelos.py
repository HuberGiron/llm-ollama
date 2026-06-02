import csv
import time
from datetime import datetime

import requests

OLLAMA_URL = "http://localhost:11434/api/generate"

MODELS = [
    "llama3.2:3b",
    "qwen2.5:7b",
    "mistral:7b",
]

PROMPT = (
    "Explica en máximo 120 palabras cómo podría usarse un LLM "
    "como asistente de alto nivel para un robot móvil universitario."
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

N_CYCLES = 100
OUTPUT_CSV = "benchmark_modelos.csv"


def evaluate_basic_quality(response_text: str) -> int:
    """
    Evaluación heurística sencilla de 0 a 10.
    No sustituye una evaluación académica humana.
    """
    text = response_text.lower().strip()

    if not text:
        return 0

    score = 0
    keywords = ["llm", "robot", "alto nivel", "lenguaje", "tarea"]

    if 200 <= len(response_text) <= 900:
        score += 2

    matches = sum(1 for word in keywords if word in text)
    score += min(matches, 4)

    if len(text) > 50:
        score += 2

    words = text.split()
    unique_ratio = len(set(words)) / max(len(words), 1)
    if unique_ratio > 0.45:
        score += 2

    return min(score, 10)


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

    total_duration_s = data.get("total_duration", 0) / 1e9
    load_duration_s = data.get("load_duration", 0) / 1e9
    prompt_eval_count = data.get("prompt_eval_count", 0)
    eval_count = data.get("eval_count", 0)
    eval_duration_s = data.get("eval_duration", 0) / 1e9

    tokens_per_second = eval_count / eval_duration_s if eval_duration_s > 0 else 0

    return {
        "response": data.get("response", ""),
        "total_duration_s": total_duration_s,
        "wall_time_s": end - start,
        "load_duration_s": load_duration_s,
        "prompt_eval_count": prompt_eval_count,
        "eval_count": eval_count,
        "eval_duration_s": eval_duration_s,
        "tokens_per_second": tokens_per_second,
    }


fieldnames = [
    "timestamp",
    "experiment_id",
    "model",
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
    "quality_score",
    "notes",
]

with open(OUTPUT_CSV, mode="w", newline="", encoding="utf-8") as file:
    writer = csv.DictWriter(file, fieldnames=fieldnames)
    writer.writeheader()

    for model in MODELS:
        for cycle in range(1, N_CYCLES + 1):
            print(f"Modelo: {model} | Ciclo: {cycle}/{N_CYCLES}")

            row = {
                "timestamp": datetime.now().isoformat(),
                "experiment_id": "comparacion_modelos",
                "model": model,
                "cycle": cycle,
                "prompt": PROMPT,
                "temperature": BASE_OPTIONS["temperature"],
                "top_p": BASE_OPTIONS["top_p"],
                "top_k": BASE_OPTIONS["top_k"],
                "min_p": BASE_OPTIONS["min_p"],
                "num_ctx": BASE_OPTIONS["num_ctx"],
                "num_predict": BASE_OPTIONS["num_predict"],
                "repeat_penalty": BASE_OPTIONS["repeat_penalty"],
                "response": "",
                "total_duration_s": "",
                "wall_time_s": "",
                "load_duration_s": "",
                "prompt_eval_count": "",
                "eval_count": "",
                "eval_duration_s": "",
                "tokens_per_second": "",
                "response_chars": "",
                "quality_score": "",
                "notes": "",
            }

            try:
                result = run_ollama(model, PROMPT, BASE_OPTIONS)
                response_text = result["response"]
                quality_score = evaluate_basic_quality(response_text)

                row.update({
                    "response": response_text,
                    "total_duration_s": result["total_duration_s"],
                    "wall_time_s": result["wall_time_s"],
                    "load_duration_s": result["load_duration_s"],
                    "prompt_eval_count": result["prompt_eval_count"],
                    "eval_count": result["eval_count"],
                    "eval_duration_s": result["eval_duration_s"],
                    "tokens_per_second": result["tokens_per_second"],
                    "response_chars": len(response_text),
                    "quality_score": quality_score,
                })

            except Exception as error:
                row["notes"] = str(error)

            writer.writerow(row)

print(f"Benchmark terminado. Resultados guardados en {OUTPUT_CSV}")

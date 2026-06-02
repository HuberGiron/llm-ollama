import requests
import time

# ============================================================
# Prueba manual de un prompt con parámetros de generación
# Requiere Ollama ejecutándose localmente.
# Endpoint por defecto: http://localhost:11434/api/generate
# ============================================================

OLLAMA_URL = "http://localhost:11434/api/generate"

# Cambia este modelo por uno que ya tengas instalado en Ollama.
MODEL = "llama3.2:3b"

# Prompt fijo para observar cómo cambian las respuestas al modificar parámetros.
PROMPT = (
    "Explica en máximo 120 palabras qué es un sensor ultrasónico "
    "y cómo podría usarse en un robot móvil educativo. "
    "Usa lenguaje claro para estudiantes de primer semestre."
)

# Modifica manualmente estos parámetros y vuelve a ejecutar el script.
OPTIONS = {
    "temperature": 0.7,
    "top_p": 0.9,
    "top_k": 40,
    "min_p": 0.0,
    "num_ctx": 4096,
    "num_predict": 160,
    "repeat_penalty": 1.1,
    "repeat_last_n": 64,
    "seed": 42
}

payload = {
    "model": MODEL,
    "prompt": PROMPT,
    "stream": False,
    "keep_alive": "5m",
    "options": OPTIONS
}

print("=" * 70)
print("PRUEBA MANUAL DE PARÁMETROS CON OLLAMA")
print("=" * 70)
print(f"Modelo: {MODEL}")
print("\nPrompt:")
print(PROMPT)
print("\nParámetros:")
for key, value in OPTIONS.items():
    print(f"  {key}: {value}")
print("=" * 70)

try:
    start_time = time.perf_counter()
    response = requests.post(OLLAMA_URL, json=payload, timeout=300)
    end_time = time.perf_counter()

    response.raise_for_status()
    data = response.json()

    generated_text = data.get("response", "")

    total_duration_s = data.get("total_duration", 0) / 1e9
    load_duration_s = data.get("load_duration", 0) / 1e9
    prompt_eval_count = data.get("prompt_eval_count", 0)
    eval_count = data.get("eval_count", 0)
    eval_duration_s = data.get("eval_duration", 0) / 1e9

    tokens_per_second = (
        eval_count / eval_duration_s if eval_duration_s > 0 else 0
    )

    print("\nRESPUESTA DEL MODELO")
    print("-" * 70)
    print(generated_text)

    print("\nMÉTRICAS")
    print("-" * 70)
    print(f"Tiempo medido por Python: {end_time - start_time:.3f} s")
    print(f"Tiempo total reportado por Ollama: {total_duration_s:.3f} s")
    print(f"Tiempo de carga del modelo: {load_duration_s:.3f} s")
    print(f"Tokens de entrada: {prompt_eval_count}")
    print(f"Tokens de salida: {eval_count}")
    print(f"Tiempo de generación: {eval_duration_s:.3f} s")
    print(f"Tokens por segundo: {tokens_per_second:.2f}")

except requests.exceptions.ConnectionError:
    print("ERROR: No se pudo conectar con Ollama.")
    print("Verifica que Ollama esté instalado y ejecutándose.")
    print("Puedes probar en terminal: ollama run llama3.2:3b")

except requests.exceptions.Timeout:
    print("ERROR: La solicitud tardó demasiado tiempo.")
    print("Prueba con un modelo más pequeño o reduce num_predict.")

except requests.exceptions.HTTPError as error:
    print("ERROR HTTP:", error)
    print("Respuesta del servidor:", response.text)

except Exception as error:
    print("ERROR inesperado:", error)

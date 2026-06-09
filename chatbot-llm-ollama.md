---
layout: default
title: Chatbot LLM
nav_order: 3
---

# LLM como chatbot: arquitectura frontend/backend

Esta sección explica cómo integrar un modelo grande de lenguaje (*Large Language Model*, LLM) ejecutado localmente con Ollama dentro de una aplicación web tipo chatbot. El objetivo es pasar del uso del LLM en terminal o en scripts aislados a una arquitectura **cliente-servidor**, donde una interfaz web se comunica con una API en Python, y esta API funciona como intermediaria hacia Ollama.

El tema se apoya en documentación oficial de Ollama, FastAPI y MDN Web Docs. Ollama permite interactuar con modelos locales mediante endpoints HTTP como `/api/generate` y `/api/chat`, mientras que FastAPI permite construir APIs con validación de datos, documentación automática y configuración de CORS para comunicación entre frontend y backend [1]–[5]. Desde el navegador, JavaScript puede comunicarse con el backend mediante la API `fetch`, la cual permite realizar solicitudes HTTP y procesar respuestas de red [6], [7].

> 🎯 **Objetivo de aprendizaje:** Al finalizar esta actividad, el estudiante será capaz de explicar la arquitectura cliente-servidor de un chatbot con LLM local; implementar una API en Python como intermediaria entre una página web y Ollama; construir un frontend HTML/CSS/JS para conversar con el modelo; configurar parámetros de generación desde la interfaz; y mostrar métricas de latencia, tokens de entrada, tokens de salida y velocidad de generación.

---

## 1. Del modelo local al chatbot web

En los temas anteriores se trabajó con modelos LLM desde terminal, scripts de Python y pruebas de benchmark. Ese enfoque permite comprender cómo instalar modelos, modificar parámetros de generación, medir latencia, analizar tokens y comparar modelos. Sin embargo, una aplicación real normalmente requiere una interfaz más accesible para el usuario.

Un chatbot con LLM es una arquitectura de software compuesta por una interfaz, una API intermedia, un servicio de inferencia y un modelo. Cada componente tiene una función específica.

```text
Usuario
→ Frontend web
→ Backend Python
→ API local de Ollama
→ Modelo LLM
```

En esta arquitectura, el navegador no se comunica directamente con el modelo. El frontend envía una solicitud al backend; el backend valida los datos, construye la solicitud compatible con Ollama, consulta el modelo y devuelve una respuesta estructurada.

> ⚠️ **Consideración:** Aunque Ollama expone una API local, en una arquitectura académica o profesional es recomendable usar un backend intermedio. Esto facilita validación, control de modelos, registro de métricas, manejo de errores y extensión posterior hacia bases de datos, RAG, autenticación, sensores o robótica.

---

## 2. Arquitectura cliente-servidor para chatbot local

La arquitectura propuesta se divide en cuatro capas principales.

```text
┌──────────────────────────────────────────────┐
│ Usuario                                      │
│ Escribe una pregunta o instrucción            │
└───────────────────────┬──────────────────────┘
                        ↓
┌──────────────────────────────────────────────┐
│ Frontend web                                 │
│ HTML + CSS + JavaScript                      │
│ Formulario, parámetros, historial, métricas  │
└───────────────────────┬──────────────────────┘
                        ↓ HTTP POST /chat
┌──────────────────────────────────────────────┐
│ Backend Python                               │
│ FastAPI                                      │
│ Valida, construye payload, llama a Ollama    │
└───────────────────────┬──────────────────────┘
                        ↓ HTTP POST /api/chat
┌──────────────────────────────────────────────┐
│ Ollama API local                             │
│ Ejecuta el modelo LLM                        │
│ Devuelve respuesta y métricas                │
└───────────────────────┬──────────────────────┘
                        ↓
┌──────────────────────────────────────────────┐
│ Modelo LLM local                             │
│ llama3.2, gemma3, qwen, mistral, etc.        │
└──────────────────────────────────────────────┘
```

---

## 3. Componentes de la arquitectura

### 3.1 Frontend web

El frontend es la capa visible de la aplicación. Su función es permitir que el usuario escriba mensajes, seleccione el modelo, configure parámetros y observe la respuesta del LLM.

El frontend debe incluir:

- un área de conversación;
- un campo para escribir el mensaje;
- un selector de modelo;
- controles para parámetros del LLM;
- un botón de envío;
- un indicador de carga;
- un panel de métricas;
- manejo visual de errores.

JavaScript enviará la solicitud al backend usando `fetch()`. La API Fetch proporciona una interfaz para realizar solicitudes de red desde el navegador, y `window.fetch()` devuelve una promesa que se resuelve cuando la respuesta está disponible [6], [7].

---

### 3.2 Backend Python

El backend es la capa intermedia entre el navegador y Ollama. En esta práctica se implementa con **FastAPI**, porque permite construir endpoints HTTP con validación de datos, modelos de entrada y salida, documentación automática y configuración de CORS.

El backend se encarga de:

- recibir el mensaje del usuario;
- recibir parámetros del frontend;
- validar rangos de parámetros;
- construir el payload para Ollama;
- enviar la solicitud a `http://localhost:11434/api/chat`;
- medir latencia desde Python;
- extraer respuesta y métricas;
- devolver un JSON estructurado al frontend.

FastAPI permite configurar CORS mediante `CORSMiddleware`, lo cual es necesario cuando el frontend y el backend se ejecutan en orígenes diferentes, por ejemplo `localhost:5500` y `localhost:8000` [4].

---

### 3.3 Ollama API local

Ollama funciona como servicio local de inferencia. Por defecto, expone su API en:

```text
http://localhost:11434
```

Los endpoints más importantes para este tema son:

| Endpoint | Uso principal | Comentario |
|---|---|---|
| `/api/generate` | Generar texto a partir de un prompt único | Útil para pruebas simples |
| `/api/chat` | Generar el siguiente mensaje de una conversación | Recomendado para chatbot |

Ollama documenta `/api/chat` como el endpoint para generar el siguiente mensaje en una conversación entre usuario y asistente [2]. Para esta práctica se usará `/api/chat`, porque permite trabajar con mensajes con roles: `system`, `user` y `assistant`.

---

## 4. Prompt único vs conversación

### 4.1 Prompt único con `/api/generate`

El endpoint `/api/generate` recibe un prompt como texto. Es útil para pruebas sencillas.

<!-- code-open: true -->
```json
{
  "model": "llama3.2:3b",
  "prompt": "Explica qué es un sensor ultrasónico.",
  "stream": false
}
```

Este enfoque es simple, pero no representa naturalmente un chatbot. Si se quiere conservar historial, el programador tendría que concatenar manualmente las preguntas y respuestas anteriores.

---

### 4.2 Conversación con `/api/chat`

El endpoint `/api/chat` recibe una lista de mensajes.

<!-- code-open: true -->
```json
{
  "model": "llama3.2:3b",
  "messages": [
    {
      "role": "system",
      "content": "Eres un asistente académico claro y preciso."
    },
    {
      "role": "user",
      "content": "Explica qué es un sensor ultrasónico."
    }
  ],
  "stream": false
}
```

Este enfoque es más adecuado para chatbot porque la conversación se representa como una secuencia de mensajes con roles. En una primera versión, el historial puede manejarse en el frontend; en una versión más avanzada, puede almacenarse en el backend, una base de datos o una sesión de usuario.

---

## 5. Estructura de solicitud y respuesta

### 5.1 Solicitud del frontend al backend

El frontend enviará un JSON al endpoint propio del backend:

```text
POST http://localhost:8000/chat
```

Ejemplo:

<!-- code-open: true -->
```json
{
  "message": "Explica qué es un sensor ultrasónico.",
  "model": "llama3.2:3b",
  "temperature": 0.7,
  "top_p": 0.9,
  "num_predict": 160,
  "num_ctx": 4096,
  "repeat_penalty": 1.1
}
```

Esta solicitud pertenece a nuestra aplicación. El frontend no necesita conocer todos los detalles internos de Ollama.

---

### 5.2 Solicitud del backend hacia Ollama

El backend transforma la solicitud anterior en un payload compatible con Ollama:

<!-- code-open: true -->
```json
{
  "model": "llama3.2:3b",
  "messages": [
    {
      "role": "system",
      "content": "Eres un asistente académico claro, preciso y útil para estudiantes universitarios."
    },
    {
      "role": "user",
      "content": "Explica qué es un sensor ultrasónico."
    }
  ],
  "stream": false,
  "keep_alive": "5m",
  "options": {
    "temperature": 0.7,
    "top_p": 0.9,
    "num_predict": 160,
    "num_ctx": 4096,
    "repeat_penalty": 1.1
  }
}
```

Se recomienda usar `stream: false` en esta primera versión porque la respuesta completa incluye métricas de inferencia al final. Ollama documenta métricas como `total_duration`, `load_duration`, `prompt_eval_count`, `eval_count` y `eval_duration`; los tiempos se reportan en nanosegundos, por lo que el backend debe convertirlos a segundos dividiendo entre `1e9` [3].

---

### 5.3 Respuesta del backend al frontend

El backend debe devolver una respuesta simplificada:

<!-- code-open: true -->
```json
{
  "model": "llama3.2:3b",
  "reply": "Un sensor ultrasónico es un dispositivo que mide distancia...",
  "metrics": {
    "wall_time_s": 1.48,
    "total_duration_s": 1.42,
    "load_duration_s": 0.03,
    "prompt_eval_count": 58,
    "eval_count": 132,
    "total_tokens": 190,
    "eval_duration_s": 1.16,
    "tokens_per_second": 113.79
  }
}
```

Esta estructura permite mostrar dos niveles de información: la respuesta conversacional y el desempeño técnico del modelo.

---

## 6. Parámetros configurables desde la interfaz

Para la práctica no es necesario mostrar todos los parámetros posibles. Se recomienda usar los siguientes:

| Parámetro | Control sugerido | Rango sugerido | Propósito |
|---|---|---:|---|
| `model` | Selector | Modelos instalados | Elegir LLM local |
| `temperature` | Slider | 0.0 a 1.2 | Controlar aleatoriedad |
| `top_p` | Slider | 0.7 a 0.95 | Controlar diversidad probabilística |
| `num_predict` | Campo numérico | 50 a 500 | Limitar longitud de salida |
| `num_ctx` | Selector | 2048, 4096, 8192 | Cambiar ventana de contexto |
| `repeat_penalty` | Slider | 1.0 a 1.5 | Reducir repeticiones |

El backend debe validar estos valores. Esto evita solicitudes excesivas, configuraciones peligrosas o consumo innecesario de memoria.

---

## 7. Métricas visibles en el chatbot

Una parte central de esta práctica es mostrar métricas después de cada respuesta. El objetivo es que el estudiante observe la relación entre parámetros, tokens, latencia y comportamiento del modelo.

| Métrica | Fuente | Interpretación |
|---|---|---|
| `wall_time_s` | Backend Python | Tiempo real medido por el backend |
| `total_duration_s` | Ollama | Tiempo total reportado por el motor |
| `load_duration_s` | Ollama | Tiempo de carga del modelo |
| `prompt_eval_count` | Ollama | Tokens de entrada |
| `eval_count` | Ollama | Tokens de salida |
| `total_tokens` | Backend | Entrada + salida |
| `eval_duration_s` | Ollama | Tiempo de generación |
| `tokens_per_second` | Backend/Ollama | Velocidad de generación |

---

## 8. Estructura del proyecto

La estructura recomendada es:

```text
llm-chatbot-local/
├── backend/
│   ├── main.py
│   └── requirements.txt
└── frontend/
    ├── index.html
    ├── styles.css
    └── app.js
```

| Carpeta | Archivo | Función |
|---|---|---|
| `backend/` | `main.py` | API intermedia en Python |
| `backend/` | `requirements.txt` | Dependencias del backend |
| `frontend/` | `index.html` | Estructura de la interfaz |
| `frontend/` | `styles.css` | Estilos visuales |
| `frontend/` | `app.js` | Comunicación con el backend |

---

## 9. Desarrollo guiado paso a paso

### 9.1 Verificar Ollama y modelo instalado

```bash
ollama --version
ollama ls
ollama run llama3.2:3b
```

---

### 9.2 Crear estructura de carpetas

```bash
mkdir llm-chatbot-local
cd llm-chatbot-local
mkdir backend frontend
```

---

### 9.3 Crear entorno virtual

### 9.3.1 ¿Por qué usar un entorno virtual en Python?

En Python, un **entorno virtual** es una carpeta aislada que contiene una instalación propia de paquetes y dependencias para un proyecto específico. Su objetivo es evitar que las bibliotecas instaladas para una práctica afecten otros proyectos de Python instalados en la misma computadora.

Cuando se desarrolla una API con FastAPI para conectar un frontend web con Ollama, se requieren paquetes como `fastapi`, `uvicorn`, `requests` y `pydantic`. Si estos paquetes se instalan directamente en el Python global del sistema, pueden mezclarse con dependencias de otros proyectos, generar conflictos de versiones o dificultar la reproducción del proyecto en otra computadora.

Por ejemplo, un proyecto puede requerir una versión específica de `fastapi`, mientras que otro proyecto puede necesitar una versión distinta. El entorno virtual permite que cada proyecto tenga sus propias dependencias sin modificar el entorno global de Python. Esto mejora la organización, reduce errores y facilita compartir el proyecto mediante un archivo `requirements.txt`.

```text
Python global del sistema
├── Proyecto A
│   └── .venv con sus propias dependencias
├── Proyecto B
│   └── .venv con otras dependencias
└── Proyecto C
    └── .venv independiente
```

Windows PowerShell:

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

macOS / Linux:

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
```

---

### 9.4 Instalar dependencias

```bash
pip install fastapi uvicorn requests pydantic
pip freeze > requirements.txt
```

---

## 10. Backend FastAPI

Crea el archivo:

```text
backend/main.py
```

<!-- code-file: main.py -->
```python
import time

import requests
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field


OLLAMA_CHAT_URL = "http://localhost:11434/api/chat"


app = FastAPI(
    title="Chatbot LLM local con Ollama",
    description="API intermedia para conversar con modelos locales mediante Ollama.",
    version="1.0.0",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5500",
        "http://127.0.0.1:5500",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=4000)
    model: str = Field(default="llama3.2:3b", min_length=1)

    temperature: float = Field(default=0.7, ge=0.0, le=1.2)
    top_p: float = Field(default=0.9, ge=0.1, le=1.0)
    num_predict: int = Field(default=160, ge=20, le=1000)
    num_ctx: int = Field(default=4096, ge=512, le=8192)
    repeat_penalty: float = Field(default=1.1, ge=1.0, le=2.0)

    keep_alive: str = Field(default="5m")
    system_prompt: str = Field(
        default="Eres un asistente académico claro, preciso y útil para estudiantes universitarios."
    )


class ChatMetrics(BaseModel):
    wall_time_s: float
    total_duration_s: float
    load_duration_s: float
    prompt_eval_count: int
    eval_count: int
    total_tokens: int
    eval_duration_s: float
    tokens_per_second: float


class ChatResponse(BaseModel):
    model: str
    reply: str
    metrics: ChatMetrics


@app.get("/")
def root():
    return {
        "message": "API de chatbot local con Ollama",
        "docs": "/docs",
        "health": "/health",
    }


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    payload = {
        "model": request.model,
        "messages": [
            {
                "role": "system",
                "content": request.system_prompt,
            },
            {
                "role": "user",
                "content": request.message,
            },
        ],
        "stream": False,
        "keep_alive": request.keep_alive,
        "options": {
            "temperature": request.temperature,
            "top_p": request.top_p,
            "num_predict": request.num_predict,
            "num_ctx": request.num_ctx,
            "repeat_penalty": request.repeat_penalty,
        },
    }

    try:
        start_time = time.perf_counter()
        response = requests.post(OLLAMA_CHAT_URL, json=payload, timeout=300)
        end_time = time.perf_counter()

        response.raise_for_status()
        data = response.json()

    except requests.exceptions.ConnectionError as exc:
        raise HTTPException(
            status_code=503,
            detail="No se pudo conectar con Ollama. Verifica que Ollama esté ejecutándose.",
        ) from exc

    except requests.exceptions.Timeout as exc:
        raise HTTPException(
            status_code=504,
            detail="La solicitud a Ollama tardó demasiado tiempo.",
        ) from exc

    except requests.exceptions.HTTPError as exc:
        raise HTTPException(
            status_code=response.status_code,
            detail=f"Error devuelto por Ollama: {response.text}",
        ) from exc

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Error inesperado: {str(exc)}",
        ) from exc

    message = data.get("message", {})
    reply = message.get("content", "")

    total_duration_s = data.get("total_duration", 0) / 1e9
    load_duration_s = data.get("load_duration", 0) / 1e9
    prompt_eval_count = data.get("prompt_eval_count", 0)
    eval_count = data.get("eval_count", 0)
    eval_duration_s = data.get("eval_duration", 0) / 1e9

    total_tokens = prompt_eval_count + eval_count
    tokens_per_second = eval_count / eval_duration_s if eval_duration_s > 0 else 0

    return ChatResponse(
        model=request.model,
        reply=reply,
        metrics=ChatMetrics(
            wall_time_s=end_time - start_time,
            total_duration_s=total_duration_s,
            load_duration_s=load_duration_s,
            prompt_eval_count=prompt_eval_count,
            eval_count=eval_count,
            total_tokens=total_tokens,
            eval_duration_s=eval_duration_s,
            tokens_per_second=tokens_per_second,
        ),
    )
```

Crea el archivo:

```text
backend/requirements.txt
```

```text
fastapi
uvicorn
requests
pydantic
```

---

## 11. Probar backend sin frontend

Ejecutar servidor:

```bash
cd backend
uvicorn main:app --reload --port 8000
```

Abrir documentación automática:

```text
http://localhost:8000/docs
```

Probar endpoint de salud:

```bash
curl http://localhost:8000/health
```

Respuesta esperada:

```json
{
  "status": "ok"
}
```

Probar endpoint `/chat`:

```bash
curl -X POST http://localhost:8000/chat   -H "Content-Type: application/json"   -d '{
    "message": "Explica qué es un sensor ultrasónico en máximo 80 palabras.",
    "model": "llama3.2:3b",
    "temperature": 0.7,
    "top_p": 0.9,
    "num_predict": 120,
    "num_ctx": 4096,
    "repeat_penalty": 1.1
  }'
```

**Espacio para captura sugerida:**

```md
![Prueba endpoint chat](assets/img/chatbot/prueba-endpoint-chat.png)
```

---

## 12. Frontend web

### 12.1 Archivo `index.html`

Crea el archivo:

```text
frontend/index.html
```

<!-- code-file: index.html -->
```html
<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />

  <title>Chatbot LLM local con Ollama</title>

  <link rel="stylesheet" href="styles.css" />
</head>
<body>
  <main class="app">
    <section class="header">
      <h1>Chatbot LLM local con Ollama</h1>
      <p>
        Frontend HTML/CSS/JS conectado a una API en Python que consulta un modelo local mediante Ollama.
      </p>
    </section>

    <section class="layout">
      <aside class="controls">
        <h2>Configuración</h2>

        <label>
          Modelo
          <select id="model">
            <option value="llama3.2:3b">llama3.2:3b</option>
            <option value="gemma3:4b">gemma3:4b</option>
            <option value="qwen2.5:7b">qwen2.5:7b</option>
            <option value="mistral:7b">mistral:7b</option>
          </select>
        </label>

        <label>
          Temperatura
          <input id="temperature" type="number" min="0" max="1.2" step="0.1" value="0.7" />
        </label>

        <label>
          Top-p
          <input id="top_p" type="number" min="0.1" max="1" step="0.05" value="0.9" />
        </label>

        <label>
          Tokens máximos de salida
          <input id="num_predict" type="number" min="20" max="1000" step="10" value="160" />
        </label>

        <label>
          Contexto
          <select id="num_ctx">
            <option value="2048">2048</option>
            <option value="4096" selected>4096</option>
            <option value="8192">8192</option>
          </select>
        </label>

        <label>
          Repeat penalty
          <input id="repeat_penalty" type="number" min="1" max="2" step="0.1" value="1.1" />
        </label>

        <button id="clearBtn" type="button">Limpiar conversación</button>
      </aside>

      <section class="chat-panel">
        <div id="chat" class="chat"></div>

        <form id="chatForm" class="chat-form">
          <textarea
            id="message"
            rows="4"
            placeholder="Escribe tu mensaje para el modelo..."
            required
          ></textarea>

          <button id="sendBtn" type="submit">Enviar</button>
        </form>

        <section class="metrics">
          <h2>Métricas de la última respuesta</h2>
          <div id="metricsGrid" class="metrics-grid">
            <span>Sin datos todavía</span>
          </div>
        </section>
      </section>
    </section>
  </main>

  <script src="app.js"></script>
</body>
</html>
```

---

### 12.2 Archivo `styles.css`

Crea el archivo:

```text
frontend/styles.css
```

<!-- code-file: styles.css -->
```css
:root {
  --ibero-red: #E00034;
  --dark: #1f2937;
  --text: #333333;
  --muted: #6b7280;
  --border: #e5e7eb;
  --bg: #f8fafc;
  --card: #ffffff;
}

* {
  box-sizing: border-box;
}

body {
  margin: 0;
  font-family: Arial, Helvetica, sans-serif;
  color: var(--text);
  background: var(--bg);
}

.app {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
}

.header {
  margin-bottom: 1.5rem;
}

.header h1 {
  margin: 0 0 .5rem;
  color: var(--ibero-red);
}

.header p {
  margin: 0;
  color: var(--muted);
}

.layout {
  display: grid;
  grid-template-columns: 320px 1fr;
  gap: 1rem;
}

.controls,
.chat-panel,
.metrics {
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: 14px;
  padding: 1rem;
}

.controls h2,
.metrics h2 {
  margin-top: 0;
  font-size: 1.1rem;
}

label {
  display: block;
  margin-bottom: .9rem;
  font-weight: 600;
}

input,
select,
textarea,
button {
  width: 100%;
  margin-top: .35rem;
  padding: .65rem;
  border: 1px solid var(--border);
  border-radius: 10px;
  font: inherit;
}

textarea {
  resize: vertical;
}

button {
  border: none;
  color: #ffffff;
  background: var(--ibero-red);
  font-weight: 700;
  cursor: pointer;
}

button:disabled {
  opacity: .6;
  cursor: not-allowed;
}

#clearBtn {
  background: var(--dark);
}

.chat-panel {
  display: flex;
  flex-direction: column;
  min-height: 650px;
}

.chat {
  flex: 1;
  overflow-y: auto;
  padding: .5rem;
  border-radius: 12px;
  background: #f3f4f6;
  margin-bottom: 1rem;
}

.message {
  margin: .75rem 0;
  padding: .85rem 1rem;
  border-radius: 12px;
  line-height: 1.45;
  white-space: pre-wrap;
}

.message.user {
  background: #fee2e2;
  border-left: 4px solid var(--ibero-red);
}

.message.assistant {
  background: #ffffff;
  border-left: 4px solid #2563eb;
}

.message.error {
  background: #fef3c7;
  border-left: 4px solid #f59e0b;
}

.message strong {
  display: block;
  margin-bottom: .25rem;
}

.chat-form {
  display: grid;
  gap: .75rem;
}

.metrics {
  margin-top: 1rem;
}

.metrics-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(120px, 1fr));
  gap: .75rem;
}

.metric-card {
  background: #f8fafc;
  border: 1px solid var(--border);
  border-radius: 10px;
  padding: .75rem;
}

.metric-card small {
  display: block;
  color: var(--muted);
  margin-bottom: .25rem;
}

.metric-card strong {
  font-size: 1.05rem;
}

@media (max-width: 900px) {
  .layout {
    grid-template-columns: 1fr;
  }

  .metrics-grid {
    grid-template-columns: 1fr 1fr;
  }
}
```

---

### 12.3 Archivo `app.js`

Crea el archivo:

```text
frontend/app.js
```

<!-- code-file: app.js -->
```javascript
const API_URL = "http://localhost:8000/chat";

const form = document.getElementById("chatForm");
const chat = document.getElementById("chat");
const metricsGrid = document.getElementById("metricsGrid");
const sendBtn = document.getElementById("sendBtn");
const clearBtn = document.getElementById("clearBtn");

const messageInput = document.getElementById("message");

function getConfig() {
  return {
    model: document.getElementById("model").value,
    temperature: Number(document.getElementById("temperature").value),
    top_p: Number(document.getElementById("top_p").value),
    num_predict: Number(document.getElementById("num_predict").value),
    num_ctx: Number(document.getElementById("num_ctx").value),
    repeat_penalty: Number(document.getElementById("repeat_penalty").value)
  };
}

function addMessage(role, content, type = "assistant") {
  const div = document.createElement("div");
  div.className = `message ${type}`;
  div.innerHTML = `<strong>${role}</strong>${escapeHtml(content)}`;
  chat.appendChild(div);
  chat.scrollTop = chat.scrollHeight;
}

function renderMetrics(metrics) {
  const items = [
    ["Tiempo backend", `${metrics.wall_time_s.toFixed(3)} s`],
    ["Tiempo Ollama", `${metrics.total_duration_s.toFixed(3)} s`],
    ["Carga modelo", `${metrics.load_duration_s.toFixed(3)} s`],
    ["Tokens entrada", metrics.prompt_eval_count],
    ["Tokens salida", metrics.eval_count],
    ["Tokens totales", metrics.total_tokens],
    ["Generación", `${metrics.eval_duration_s.toFixed(3)} s`],
    ["Tokens/s", metrics.tokens_per_second.toFixed(2)]
  ];

  metricsGrid.innerHTML = items
    .map(([label, value]) => `
      <div class="metric-card">
        <small>${label}</small>
        <strong>${value}</strong>
      </div>
    `)
    .join("");
}

function escapeHtml(text) {
  return text
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;");
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();

  const message = messageInput.value.trim();

  if (!message) {
    return;
  }

  const payload = {
    message,
    ...getConfig()
  };

  addMessage("Usuario", message, "user");
  messageInput.value = "";
  sendBtn.disabled = true;
  sendBtn.textContent = "Generando...";

  try {
    const response = await fetch(API_URL, {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify(payload)
    });

    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.detail || "Error desconocido");
    }

    addMessage(`Modelo (${data.model})`, data.reply, "assistant");
    renderMetrics(data.metrics);

  } catch (error) {
    addMessage("Error", error.message, "error");

  } finally {
    sendBtn.disabled = false;
    sendBtn.textContent = "Enviar";
  }
});

clearBtn.addEventListener("click", () => {
  chat.innerHTML = "";
  metricsGrid.innerHTML = "<span>Sin datos todavía</span>";
});
```

---

## 13. Ejecutar frontend

Desde la carpeta `frontend`:

```bash
python -m http.server 5500
```

Abrir en el navegador:

```text
http://localhost:5500
```

**Espacio para captura sugerida:**

```md
![Chatbot funcionando](assets/img/chatbot/chatbot-funcionando.png)
```

---

## 14. Pruebas sugeridas

Usa estos prompts para validar la aplicación.

| Tipo | Prompt | Objetivo |
|---|---|---|
| Conceptual | `Explica qué es un sensor ultrasónico para estudiantes de primer semestre.` | Claridad |
| Técnico | `Dame un ejemplo de código Arduino para leer un sensor HC-SR04.` | Capacidad técnica |
| Comparativo | `Compara un sensor ultrasónico con un sensor infrarrojo.` | Organización y razonamiento |
| Robótica | `Explica cómo un robot móvil puede usar un sensor ultrasónico para evitar obstáculos.` | Aplicación al contexto físico |

También modifica parámetros y observa:

| Parámetro | Valores sugeridos | Qué observar |
|---|---|---|
| `temperature` | `0.0`, `0.7`, `1.1` | Variabilidad |
| `num_predict` | `80`, `160`, `300` | Longitud y latencia |
| `repeat_penalty` | `1.0`, `1.2`, `1.5` | Repetición |
| `num_ctx` | `2048`, `4096`, `8192` | Uso de contexto |

---

## 15. Actividad 3: Implementación de chatbot web con LLM local

### Objetivo

Implementar un chatbot web cliente-servidor que permita conversar con un LLM local mediante Ollama, configurar parámetros de generación desde el frontend y visualizar métricas técnicas por cada respuesta.

### Requerimientos mínimos

El sistema debe incluir:

```text
1. Backend en Python con FastAPI.
2. Endpoint POST /chat.
3. Conexión backend → Ollama API.
4. Frontend HTML/CSS/JS.
5. Formulario para enviar mensajes.
6. Selector de modelo.
7. Controles de parámetros:
   - temperature
   - top_p
   - num_predict
   - num_ctx
   - repeat_penalty
8. Visualización de respuesta del modelo.
9. Visualización de métricas:
   - tiempo total
   - tiempo medido por backend
   - tokens de entrada
   - tokens de salida
   - tokens totales
   - tokens por segundo
10. Manejo básico de errores.
```

### Entregables

```text
- Código del backend.
- Código del frontend.
- Captura de Ollama con modelo instalado.
- Captura del backend ejecutándose.
- Captura de prueba del endpoint /chat.
- Captura del frontend funcionando.
- Captura de métricas visibles.
- Reflexión técnica breve.
```

### Reflexión técnica

Responder:

```text
1. ¿Qué modelo local utilizaste?
2. ¿Qué parámetros configuraste desde el frontend?
3. ¿Qué ocurre al aumentar num_predict?
4. ¿Qué ocurre al modificar temperature?
5. ¿Por qué es útil mostrar tokens y latencia?
6. ¿Por qué se recomienda usar backend en vez de conectar el navegador directamente a Ollama?
7. ¿Cómo extenderías este chatbot para una aplicación robótica o de IA física?
```

---

## 16. Evaluación sugerida

| Criterio | Puntaje |
|---|---:|
| Backend funcional con `/chat` | 20 |
| Integración correcta con Ollama | 20 |
| Frontend funcional con formulario e historial | 20 |
| Parámetros configurables desde frontend | 15 |
| Métricas visibles y correctas | 15 |
| Evidencias y reflexión técnica | 10 |
| **Total** | **100** |

---

## 17. Consideraciones finales

El chatbot desarrollado en este tema representa una arquitectura mínima pero extensible. Aunque el ejemplo se ejecuta localmente, la misma estructura puede adaptarse a otras configuraciones.

```text
Frontend + Backend + Ollama local
Frontend + Backend + servidor GPU
Frontend + Backend + API comercial
Frontend + Backend + RAG
Frontend + Backend + robot físico
Frontend + Backend + base de datos
```

En aplicaciones reales, esta arquitectura puede ampliarse con autenticación, almacenamiento de conversaciones, historial persistente, recuperación aumentada por generación, conexión con sensores, ejecución de herramientas o validadores de seguridad.

En robótica e IA física, el chatbot no debe entenderse como un controlador directo de motores, sino como una capa de interacción, explicación, planificación o asistencia. Las acciones físicas deben pasar por una capa intermedia de validación y control determinista.

---

## 18. Referencias

[1] Ollama. (s. f.). *Generate API*. Documentación oficial del endpoint `/api/generate`, parámetros de generación, `stream`, `options`, `keep_alive` y métricas de inferencia. Disponible en: <https://docs.ollama.com/api/generate>

[2] Ollama. (s. f.). *Chat API*. Documentación oficial del endpoint `/api/chat` para conversaciones con modelos locales mediante mensajes con roles. Disponible en: <https://docs.ollama.com/api/chat>

[3] Ollama. (s. f.). *Usage*. Documentación oficial sobre métricas de uso y desempeño como `total_duration`, `load_duration`, `prompt_eval_count`, `eval_count` y `eval_duration`. Disponible en: <https://docs.ollama.com/api/usage>

[4] FastAPI. (s. f.). *CORS (Cross-Origin Resource Sharing)*. Documentación oficial sobre comunicación entre frontend y backend en orígenes diferentes mediante `CORSMiddleware`. Disponible en: <https://fastapi.tiangolo.com/tutorial/cors/>

[5] FastAPI. (s. f.). *Request body*. Documentación oficial sobre definición y validación de cuerpos de solicitud con modelos de datos. Disponible en: <https://fastapi.tiangolo.com/tutorial/body/>

[6] MDN Web Docs. (s. f.). *Fetch API*. Documentación oficial sobre solicitudes HTTP desde JavaScript en el navegador. Disponible en: <https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API>

[7] MDN Web Docs. (s. f.). *Window: fetch() method*. Documentación oficial del método `fetch()` para iniciar solicitudes de red desde el navegador. Disponible en: <https://developer.mozilla.org/en-US/docs/Web/API/Window/fetch>

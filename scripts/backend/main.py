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
    return {"message": "API de chatbot local con Ollama", "docs": "/docs", "health": "/health"}


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    payload = {
        "model": request.model,
        "messages": [
            {"role": "system", "content": request.system_prompt},
            {"role": "user", "content": request.message},
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
        raise HTTPException(status_code=503, detail="No se pudo conectar con Ollama.") from exc
    except requests.exceptions.Timeout as exc:
        raise HTTPException(status_code=504, detail="La solicitud a Ollama tardó demasiado tiempo.") from exc
    except requests.exceptions.HTTPError as exc:
        raise HTTPException(status_code=response.status_code, detail=f"Error devuelto por Ollama: {response.text}") from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Error inesperado: {str(exc)}") from exc

    reply = data.get("message", {}).get("content", "")
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

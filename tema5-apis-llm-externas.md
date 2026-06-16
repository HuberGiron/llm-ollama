---
layout: default
title: APIs LLM
nav_order: 5
---

# Tema 5. Uso de APIs externas para LLMs

## 1. Introducción

En los temas anteriores se construyó un chatbot local usando **Ollama**, un backend en **FastAPI** y un frontend en **HTML, CSS y JavaScript**. Esa arquitectura permitió ejecutar modelos de lenguaje en la computadora del estudiante o en un servidor propio, controlar parámetros de generación y observar métricas como latencia, tokens de entrada, tokens de salida y tokens por segundo.

En este tema se extiende esa arquitectura para usar **modelos de lenguaje alojados por proveedores externos**. En lugar de ejecutar el modelo localmente, el backend enviará una solicitud HTTP a una API en línea, recibirá la respuesta del modelo y la mostrará al usuario.

La idea central no es reemplazar el uso local de Ollama, sino comparar ambos enfoques:

```text
LLM local con Ollama
vs
LLM remoto mediante API externa
```

Esta comparación es importante porque en aplicaciones reales se deben tomar decisiones técnicas, económicas y éticas sobre:

```text
- costo;
- velocidad;
- privacidad;
- dependencia de internet;
- tamaño del modelo;
- límites de uso;
- facilidad de integración;
- calidad de respuesta;
- trazabilidad del consumo de tokens.
```

---

## 2. Objetivo del tema

El objetivo de este tema es que el estudiante integre y compare modelos de lenguaje accesibles mediante APIs externas, identificando sus características técnicas, sus límites de uso y sus diferencias frente a modelos ejecutados localmente con Ollama.

Al finalizar la práctica, el estudiante será capaz de:

```text
- explicar qué es una API de LLM;
- obtener una API key de un proveedor externo;
- enviar solicitudes a un modelo remoto;
- medir latencia y consumo de tokens;
- comparar dos modelos alojados en la nube;
- contrastar modelos externos contra modelos locales en Ollama;
- discutir ventajas y limitaciones de cada enfoque.
```

---

## 3. De Ollama local a APIs externas

En la arquitectura local usada anteriormente, el flujo era:

```text
Usuario
  ↓
Frontend
  ↓
Backend FastAPI
  ↓
Ollama /api/chat
  ↓
Modelo local
  ↓
Respuesta y métricas
```

En este tema, el flujo cambia:

```text
Usuario
  ↓
Frontend
  ↓
Backend FastAPI
  ↓
API externa del proveedor
  ↓
Modelo alojado en la nube
  ↓
Respuesta, uso de tokens y métricas
```

El frontend puede mantenerse casi igual. El cambio principal ocurre en el backend, porque ahora el backend debe decidir si llama a:

```text
- Ollama local;
- Gemini API;
- Groq API;
- Mistral API;
- Cohere API;
- Hugging Face Inference Providers;
- OpenRouter;
- otro proveedor compatible.
```

---

## 4. Espacio para diagrama de arquitectura

> Inserta aquí el diagrama general del tema.

```text
[IMAGEN 1: Arquitectura general del chatbot usando APIs externas]

Sugerencia visual:

Usuario
  ↓
Frontend
  - mensaje
  - proveedor
  - modelo
  - parámetros
  ↓
Backend FastAPI
  - valida entrada
  - selecciona proveedor
  - agrega API key desde .env
  - construye solicitud HTTP
  - mide tiempo
  ↓
Proveedor externo
  - Gemini / Groq / Mistral / Cohere / Hugging Face / OpenRouter
  - ejecuta modelo remoto
  - devuelve respuesta y tokens
  ↓
Backend FastAPI
  - normaliza respuesta
  - calcula métricas
  ↓
Frontend
  - muestra respuesta
  - muestra proveedor/modelo
  - muestra tokens y latencia
```

---

## 5. ¿Qué es una API de LLM?

Una **API de LLM** es una interfaz que permite enviar mensajes a un modelo de lenguaje alojado en un servidor externo. En lugar de instalar el modelo y ejecutarlo localmente, el usuario envía una solicitud por internet.

Una solicitud típica contiene:

```json
{
  "model": "nombre-del-modelo",
  "messages": [
    {
      "role": "system",
      "content": "Eres un asistente académico claro y preciso."
    },
    {
      "role": "user",
      "content": "Explica qué es una red neuronal en 3 oraciones."
    }
  ],
  "temperature": 0.7,
  "max_tokens": 200
}
```

Y una respuesta típica contiene:

```json
{
  "id": "chatcmpl-...",
  "model": "nombre-del-modelo",
  "choices": [
    {
      "message": {
        "role": "assistant",
        "content": "Una red neuronal es..."
      }
    }
  ],
  "usage": {
    "prompt_tokens": 35,
    "completion_tokens": 80,
    "total_tokens": 115
  }
}
```

La estructura exacta cambia entre proveedores, pero casi todos comparten la misma idea:

```text
entrada: mensajes + parámetros
salida: respuesta + uso de tokens
```

---

## 6. Conceptos clave

### 6.1 API key

Una **API key** es una llave privada que identifica al usuario o proyecto ante el proveedor.

Debe tratarse como una contraseña:

```text
- no se sube a GitHub;
- no se escribe directamente en el frontend;
- no se comparte con otros equipos;
- se guarda en variables de entorno;
- se puede revocar si se filtra.
```

En esta práctica, las llaves se guardarán en un archivo `.env` del backend:

```text
GEMINI_API_KEY=tu_llave
GROQ_API_KEY=tu_llave
MISTRAL_API_KEY=tu_llave
COHERE_API_KEY=tu_llave
OPENROUTER_API_KEY=tu_llave
HF_TOKEN=tu_llave
```

### 6.2 Tokens

Los modelos de lenguaje no procesan directamente palabras, sino **tokens**. Un token puede ser una palabra completa, una parte de una palabra, un signo o un fragmento de texto.

Ejemplo aproximado:

```text
"La robótica móvil es interesante"
```

puede dividirse en tokens parecidos a:

```text
["La", " rob", "ótica", " móvil", " es", " interesante"]
```

En APIs externas, el uso suele medirse con:

```text
- tokens de entrada;
- tokens de salida;
- tokens totales;
- tokens por minuto;
- solicitudes por minuto;
- solicitudes por día.
```

### 6.3 Ventana de contexto

La **ventana de contexto** es la cantidad máxima de tokens que el modelo puede considerar en una conversación o solicitud.

Un modelo con contexto de `8k` acepta aproximadamente 8,000 tokens.

Un modelo con contexto de `128k` acepta aproximadamente 128,000 tokens.

Una ventana más grande permite analizar documentos más largos, mantener conversaciones más extensas o trabajar con más instrucciones, pero también puede aumentar el costo y la latencia.

### 6.4 Parámetros del modelo

Cuando se dice que un modelo tiene `7B`, `8B`, `70B` o `111B`, se hace referencia a la cantidad aproximada de parámetros.

En este contexto:

```text
1B = 1 billion en inglés = 1,000 millones
```

Por lo tanto:

```text
7B  = 7,000 millones de parámetros
70B = 70,000 millones de parámetros
```

En español conviene decir **mil millones** para evitar confusión con el uso tradicional de la palabra "billón".

No todos los proveedores publican el número de parámetros. En modelos cerrados, como varios modelos comerciales de frontera, el número de parámetros puede no estar disponible públicamente.

---

## 7. APIs recomendadas para experimentar

La siguiente tabla resume opciones útiles para una práctica académica. Antes de impartir la clase, se recomienda revisar nuevamente los límites gratuitos, porque los proveedores pueden modificarlos.

| Logo | Proveedor | API / documentación | Tipo de acceso gratuito | Modelos sugeridos | Parámetros publicados | Comentario didáctico |
|---|---|---|---|---|---|---|
| `[LOGO: Google Gemini]` | Google Gemini API | https://ai.google.dev/gemini-api/docs | Tier gratuito por proyecto activo o free trial, con límites por proyecto | `gemini-2.5-flash`, `gemini-2.5-flash-lite` | No divulgado | Buena opción para comparar un modelo cerrado de alto rendimiento contra Ollama local. |
| `[LOGO: Groq]` | GroqCloud | https://console.groq.com/docs | Free plan con límites de solicitudes y tokens | `llama-3.3-70b-versatile`, `llama-3.1-8b-instant` | 70B, 8B aprox. | Excelente para medir velocidad de inferencia y comparar modelos abiertos alojados en nube. |
| `[LOGO: Mistral AI]` | Mistral AI La Plateforme | https://docs.mistral.ai/ | Free mode para evaluación y prototipado | `ministral-8b`, `mistral-small` | 8B en Ministral; otros no siempre divulgados | Buena opción para modelos eficientes y discusión sobre modelos europeos/open-weight. |
| `[LOGO: Cohere]` | Cohere API | https://docs.cohere.com/ | Evaluation key gratuita con uso limitado | `command-r`, `command-r7b`, `command-a` | 7B en Command R7B; 111B en Command A | Útil para discutir modelos enterprise, RAG, tool use y multilingüe. |
| `[LOGO: Hugging Face]` | Hugging Face Inference Providers | https://huggingface.co/docs/inference-providers | Créditos mensuales gratuitos para experimentar | Modelos Llama, Qwen, Mistral u otros según disponibilidad | Depende del modelo | Sirve para conectar el ecosistema de modelos abiertos con inferencia hospedada. |
| `[LOGO: OpenRouter]` | OpenRouter | https://openrouter.ai/docs | Modelos `:free` con límite diario | Modelos `:free` disponibles en el catálogo | Depende del modelo | Muy práctico para clase porque unifica muchos modelos con una API compatible con OpenAI. |
| `[LOGO: OpenAI]` | OpenAI API | https://platform.openai.com/docs | No se recomienda como opción gratuita principal; normalmente requiere facturación/créditos | `gpt-4.1-mini`, `gpt-4o-mini` o modelo vigente económico | No divulgado | Muy importante como referencia industrial, pero no ideal si se busca evitar cobros. |

---

## 8. Espacio para logos

> Puedes colocar aquí una fila de logos de los proveedores. Si el material se publica, usa logos desde los press kits oficiales o respeta las guías de marca de cada empresa.

```text
[IMAGEN 2: Logos de proveedores]

Google Gemini | Groq | Mistral AI | Cohere | Hugging Face | OpenRouter | OpenAI
```

También puedes usar una carpeta:

```text
imagenes/
├── logo-gemini.png
├── logo-groq.png
├── logo-mistral.png
├── logo-cohere.png
├── logo-huggingface.png
├── logo-openrouter.png
└── logo-openai.png
```

Y en la tabla reemplazar los espacios por:

```markdown
![Gemini](imagenes/logo-gemini.png)
```

---

## 9. Selección recomendada para la práctica

Para que la práctica sea clara y no se vuelva demasiado extensa, se recomienda probar solo **dos modelos remotos** y compararlos contra un modelo local en Ollama.

Selección sugerida:

```text
Modelo local:
- llama3.2:3b en Ollama

Modelo remoto 1:
- Gemini 2.5 Flash

Modelo remoto 2:
- Groq llama-3.3-70b-versatile
```

Esta selección permite comparar:

```text
- modelo pequeño local;
- modelo cerrado comercial;
- modelo abierto grande alojado en infraestructura optimizada.
```

---

## 10. Pregunta guía de la práctica

La pregunta central de la actividad será:

```text
¿Qué diferencias técnicas y prácticas existen entre usar un LLM local con Ollama y usar modelos remotos mediante APIs externas?
```

Para responderla, cada equipo deberá medir y comparar:

```text
- latencia total;
- tokens de entrada;
- tokens de salida;
- tokens totales;
- calidad de respuesta;
- estabilidad de la respuesta;
- facilidad de integración;
- límites gratuitos;
- privacidad;
- dependencia de internet;
- tamaño o parámetros del modelo, cuando estén publicados.
```

---

## 11. Arquitectura de la práctica

La arquitectura mantiene el mismo principio de los temas anteriores:

```text
Usuario
  ↓
Frontend
  - mensaje
  - proveedor
  - modelo
  - temperatura
  - tokens máximos
  ↓
Backend FastAPI
  - valida parámetros
  - selecciona cliente API
  - lee API key desde .env
  - envía solicitud HTTP
  - mide tiempo total
  - normaliza respuesta
  ↓
Proveedor externo
  - ejecuta modelo remoto
  - devuelve respuesta
  - devuelve uso de tokens, si está disponible
  ↓
Frontend
  - muestra respuesta
  - muestra proveedor y modelo
  - muestra latencia
  - muestra tokens
```

---

## 12. Espacio para diagrama comparativo

```text
[IMAGEN 3: Comparación Ollama local vs APIs externas]

Izquierda:
Usuario → Frontend → Backend → Ollama local → Modelo en la computadora

Derecha:
Usuario → Frontend → Backend → Internet → Proveedor externo → Modelo remoto

Variables comparadas:
- hardware;
- costo;
- privacidad;
- latencia;
- tamaño del modelo;
- dependencia de internet.
```

---

## 13. Preparación del entorno

### 13.1 Requisitos

Para esta práctica se requiere:

```text
- Python 3.10 o superior;
- FastAPI;
- Uvicorn;
- Requests o SDKs de proveedores;
- archivo .env;
- navegador web;
- conexión a internet;
- cuenta en al menos dos proveedores.
```

### 13.2 Instalación de dependencias

En la carpeta del backend:

```bash
pip install fastapi uvicorn requests python-dotenv
```

Si se usa el SDK oficial de Google Gemini:

```bash
pip install google-genai
```

Si se usa una API compatible con OpenAI, como Groq, OpenRouter o algunos endpoints de Mistral:

```bash
pip install openai
```

---

## 14. Manejo seguro de llaves

Crear un archivo llamado `.env` en el backend:

```text
GEMINI_API_KEY=pega_aqui_tu_llave_de_gemini
GROQ_API_KEY=pega_aqui_tu_llave_de_groq
OPENROUTER_API_KEY=pega_aqui_tu_llave_de_openrouter
MISTRAL_API_KEY=pega_aqui_tu_llave_de_mistral
COHERE_API_KEY=pega_aqui_tu_llave_de_cohere
HF_TOKEN=pega_aqui_tu_token_de_huggingface
```

Agregar `.env` al archivo `.gitignore`:

```text
.env
```

Nunca se debe colocar una API key en el frontend, porque cualquier persona podría verla desde el navegador.

---

## 15. Ejemplo conceptual de backend

El backend debe recibir una solicitud como esta:

```json
{
  "provider": "groq",
  "model": "llama-3.3-70b-versatile",
  "message": "Explica qué es la odometría diferencial en 3 oraciones.",
  "temperature": 0.7,
  "max_tokens": 200
}
```

Y devolver una respuesta normalizada:

```json
{
  "provider": "groq",
  "model": "llama-3.3-70b-versatile",
  "reply": "La odometría diferencial...",
  "metrics": {
    "wall_time_s": 0.82,
    "prompt_tokens": 38,
    "completion_tokens": 91,
    "total_tokens": 129,
    "tokens_per_second": 110.9
  }
}
```

El objetivo de normalizar la respuesta es que el frontend pueda mostrar métricas similares sin importar qué proveedor se use.

---

## 16. Ejemplo de llamada a Gemini API

Página oficial:

```text
https://ai.google.dev/gemini-api/docs
```

Ejemplo mínimo en Python:

```python
import os
import time
from google import genai
from dotenv import load_dotenv

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

prompt = "Explica qué es una red neuronal en 3 oraciones."

start = time.perf_counter()

response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=prompt
)

end = time.perf_counter()

print(response.text)
print("Tiempo total:", round(end - start, 3), "s")
```

En Gemini, los nombres de modelos pueden cambiar con el tiempo. Antes de la práctica, revisar la lista oficial de modelos:

```text
https://ai.google.dev/gemini-api/docs/models
```

---

## 17. Ejemplo de llamada a Groq

Página oficial:

```text
https://console.groq.com/docs
```

Groq ofrece una API compatible con el estilo de OpenAI. Esto permite usar el SDK de `openai` cambiando la URL base.

Ejemplo mínimo:

```python
import os
import time
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1"
)

messages = [
    {
        "role": "system",
        "content": "Eres un asistente académico claro y preciso."
    },
    {
        "role": "user",
        "content": "Explica qué es la odometría diferencial en 3 oraciones."
    }
]

start = time.perf_counter()

response = client.chat.completions.create(
    model="llama-3.3-70b-versatile",
    messages=messages,
    temperature=0.7,
    max_tokens=200
)

end = time.perf_counter()

reply = response.choices[0].message.content
usage = response.usage

print(reply)
print("Tiempo total:", round(end - start, 3), "s")
print("Tokens entrada:", usage.prompt_tokens)
print("Tokens salida:", usage.completion_tokens)
print("Tokens totales:", usage.total_tokens)
```

---

## 18. Ejemplo de llamada a OpenRouter

Página oficial:

```text
https://openrouter.ai/docs
```

OpenRouter también usa una API compatible con OpenAI. Es útil para clase porque permite probar varios modelos desde una sola integración.

Ejemplo mínimo:

```python
import os
import time
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1"
)

messages = [
    {
        "role": "system",
        "content": "Eres un asistente académico claro y preciso."
    },
    {
        "role": "user",
        "content": "Explica qué es una API de LLM en 3 oraciones."
    }
]

start = time.perf_counter()

response = client.chat.completions.create(
    model="meta-llama/llama-3.1-8b-instruct:free",
    messages=messages,
    temperature=0.7,
    max_tokens=200
)

end = time.perf_counter()

print(response.choices[0].message.content)
print("Tiempo total:", round(end - start, 3), "s")

if response.usage:
    print("Tokens entrada:", response.usage.prompt_tokens)
    print("Tokens salida:", response.usage.completion_tokens)
    print("Tokens totales:", response.usage.total_tokens)
```

Antes de usar OpenRouter, revisar el catálogo de modelos gratuitos:

```text
https://openrouter.ai/models
```

---

## 19. Actividad práctica

### 19.1 Instrucciones generales

Cada equipo deberá probar:

```text
- un modelo local con Ollama;
- un modelo remoto de Gemini;
- un modelo remoto de Groq u OpenRouter.
```

El mismo prompt debe ejecutarse en los tres modelos para que la comparación sea justa.

### 19.2 Prompt base

Usar el siguiente prompt:

```text
Explica qué es la odometría diferencial en un robot móvil de dos ruedas.
Incluye:
1. explicación conceptual;
2. ecuaciones básicas;
3. ejemplo para estudiantes de ingeniería;
4. una limitación práctica.
Responde en máximo 250 palabras.
```

### 19.3 Configuración sugerida

Usar parámetros similares:

```text
temperature: 0.7
max_tokens / num_predict: 300
top_p: 0.9, si el proveedor lo permite
```

En Ollama:

```text
modelo: llama3.2:3b
```

En Gemini:

```text
modelo: gemini-2.5-flash
```

En Groq:

```text
modelo: llama-3.3-70b-versatile
```

---

## 20. Tabla de caracterización técnica

Cada equipo deberá completar una tabla como la siguiente:

| Variable | Ollama local | Gemini API | Groq API |
|---|---:|---:|---:|
| Proveedor | Local | Google | Groq |
| Modelo | `llama3.2:3b` | `gemini-2.5-flash` | `llama-3.3-70b-versatile` |
| Tipo de modelo | Abierto/local | Cerrado/API | Abierto/API |
| Parámetros | 3B aprox. | No divulgado | 70B |
| Ventana de contexto | | | |
| Tokens de entrada | | | |
| Tokens de salida | | | |
| Tokens totales | | | |
| Tiempo total | | | |
| Tokens/s | | | |
| ¿Requiere internet? | No, después de instalar | Sí | Sí |
| ¿Requiere API key? | No | Sí | Sí |
| ¿Tiene costo? | Hardware local | Tier gratuito limitado / pago posterior | Free plan limitado / pago posterior |
| Privacidad | Alta | Depende de políticas del proveedor | Depende de políticas del proveedor |
| Facilidad de uso | Media | Alta | Alta |

---

## 21. Tabla de evaluación cualitativa

Además de las métricas numéricas, evaluar la respuesta del modelo:

| Criterio | Ollama local | Gemini API | Groq API |
|---|---:|---:|---:|
| Claridad conceptual | | | |
| Precisión técnica | | | |
| Uso correcto de ecuaciones | | | |
| Calidad del ejemplo | | | |
| Nivel adecuado para ingeniería | | | |
| Identificación de limitaciones | | | |
| Alucinaciones o errores | | | |
| Utilidad final | | | |

Escala sugerida:

```text
1 = deficiente
2 = básico
3 = aceptable
4 = bueno
5 = excelente
```

---

## 22. Preguntas de análisis

Responder individualmente o por equipo:

1. ¿Qué modelo respondió más rápido?
2. ¿Qué modelo generó la mejor explicación técnica?
3. ¿El modelo más grande fue siempre mejor?
4. ¿Qué diferencia hubo entre ejecutar localmente y usar una API?
5. ¿Qué riesgos aparecen al enviar datos a un proveedor externo?
6. ¿Qué pasaría si la API cambia de precio o deja de estar disponible?
7. ¿En qué casos conviene usar Ollama local?
8. ¿En qué casos conviene usar una API externa?
9. ¿Qué proveedor fue más fácil de integrar?
10. ¿Qué información técnica no fue publicada por el proveedor?

---

## 23. Discusión: modelo local vs modelo remoto

### 23.1 Ventajas de Ollama local

```text
- Mayor control sobre el entorno.
- No requiere enviar datos a terceros.
- No depende de cuotas por token.
- Puede funcionar sin internet después de instalar el modelo.
- Permite experimentar con modelos abiertos.
```

### 23.2 Limitaciones de Ollama local

```text
- Depende mucho del hardware disponible.
- Modelos grandes requieren mucha RAM o VRAM.
- La velocidad puede ser baja en computadoras modestas.
- La instalación inicial puede ser pesada.
- No siempre se tiene acceso a modelos de frontera.
```

### 23.3 Ventajas de APIs externas

```text
- Acceso rápido a modelos grandes.
- No requiere GPU local.
- Integración sencilla por HTTP.
- Escalabilidad mayor para prototipos.
- Algunos proveedores ofrecen modelos multimodales.
- Métricas de uso de tokens integradas.
```

### 23.4 Limitaciones de APIs externas

```text
- Requieren internet.
- Requieren API key.
- Pueden tener costo por tokens.
- Tienen límites de solicitudes por minuto o por día.
- El proveedor puede cambiar modelos, precios o políticas.
- Hay implicaciones de privacidad y gobernanza de datos.
```

---

## 24. Espacio para imagen de comparación

```text
[IMAGEN 4: Matriz de decisión]

Eje X: control local ←→ dependencia externa
Eje Y: bajo costo inicial ←→ alto rendimiento

Colocar:
- Ollama local
- Gemini API
- Groq API
- OpenRouter
- Hugging Face
```

---

## 25. Entregable de la práctica

Cada equipo entregará un reporte breve en formato Markdown o PDF con:

```text
1. proveedores y modelos usados;
2. capturas de pantalla de las pruebas;
3. tabla de métricas;
4. tabla de evaluación cualitativa;
5. reflexión comparativa;
6. conclusión sobre cuándo usar Ollama y cuándo usar APIs externas.
```

---

## 26. Rúbrica de evaluación

| Criterio | Puntos |
|---|---:|
| Configuración correcta de al menos dos APIs externas | 15 |
| Uso seguro de API keys mediante `.env` | 10 |
| Ejecución del mismo prompt en tres modelos | 15 |
| Registro correcto de tokens y latencia | 15 |
| Caracterización técnica de modelos y proveedores | 15 |
| Comparación crítica contra Ollama local | 15 |
| Claridad del reporte y evidencias | 10 |
| Reflexión sobre costos, privacidad y límites | 5 |
| **Total** | **100** |

---

## 27. Consideraciones éticas y de privacidad

Cuando se usan APIs externas, el texto enviado al modelo puede salir del entorno local. Por eso, en una práctica académica se recomienda:

```text
- no enviar datos personales;
- no enviar credenciales;
- no enviar documentos confidenciales;
- no enviar información institucional sensible;
- revisar las políticas del proveedor;
- informar a los estudiantes que están usando servicios externos.
```

Para ejercicios de clase, usar prompts genéricos o técnicos que no contengan información privada.

---

## 28. Conclusión

El uso de APIs externas permite acceder a modelos más grandes y potentes sin necesidad de contar con hardware especializado. Sin embargo, esta comodidad introduce nuevas dependencias: costos por uso, límites de cuota, necesidad de internet, gestión de llaves y consideraciones de privacidad.

Por otro lado, Ollama permite ejecutar modelos localmente, mantener mayor control y experimentar con modelos abiertos, aunque con limitaciones de hardware y velocidad.

La decisión entre un modelo local y un modelo remoto no debe verse como una competencia absoluta, sino como una decisión de arquitectura:

```text
Si necesito privacidad, control y bajo costo recurrente:
  puede convenir Ollama local.

Si necesito modelos grandes, baja latencia o capacidades avanzadas:
  puede convenir una API externa.

Si necesito prototipar rápido:
  puede convenir una API compatible con OpenAI.

Si necesito enseñar fundamentos:
  conviene comparar ambos enfoques.
```

---

## 29. Referencias y ligas útiles

[1] Google AI for Developers. Gemini API Documentation.  
https://ai.google.dev/gemini-api/docs

[2] Google AI for Developers. Gemini API Rate Limits.  
https://ai.google.dev/gemini-api/docs/rate-limits

[3] Google AI for Developers. Gemini Models.  
https://ai.google.dev/gemini-api/docs/models

[4] Groq. GroqCloud Documentation.  
https://console.groq.com/docs

[5] Groq. Rate Limits.  
https://console.groq.com/docs/rate-limits

[6] Groq. Supported Models.  
https://console.groq.com/docs/models

[7] Mistral AI. Documentation.  
https://docs.mistral.ai/

[8] Mistral AI. Rate limits and usage tiers.  
https://docs.mistral.ai/admin/user-management-finops/tier

[9] Cohere. Documentation.  
https://docs.cohere.com/

[10] Cohere. API keys and rate limits.  
https://docs.cohere.com/docs/rate-limits

[11] Cohere. Models overview.  
https://docs.cohere.com/docs/models

[12] Hugging Face. Inference Providers.  
https://huggingface.co/docs/inference-providers

[13] Hugging Face. Inference Providers Pricing and Billing.  
https://huggingface.co/docs/inference-providers/pricing

[14] OpenRouter. Documentation.  
https://openrouter.ai/docs

[15] OpenRouter. Models.  
https://openrouter.ai/models

[16] OpenRouter. Pricing and free limits.  
https://openrouter.ai/pricing

[17] OpenAI. API Documentation.  
https://platform.openai.com/docs

[18] OpenAI Help Center. Prepaid billing.  
https://help.openai.com/en/articles/8264644-how-can-i-set-up-prepaid-billing

---

## 30. Anexo: plantilla de reporte del estudiante

# Reporte de práctica: APIs externas para LLMs

## Equipo

```text
Nombre de integrantes:
Fecha:
Curso:
```

## Modelos evaluados

| Proveedor | Modelo | Tipo | Parámetros | Liga |
|---|---|---|---:|---|
| Ollama | | Local | | |
| | | API externa | | |
| | | API externa | | |

## Prompt usado

```text
Pegar aquí el prompt utilizado.
```

## Resultados cuantitativos

| Modelo | Tiempo total | Tokens entrada | Tokens salida | Tokens totales | Tokens/s |
|---|---:|---:|---:|---:|---:|
| Ollama | | | | | |
| API 1 | | | | | |
| API 2 | | | | | |

## Resultados cualitativos

| Modelo | Claridad | Precisión | Ejemplo | Errores | Comentario |
|---|---:|---:|---:|---:|---|
| Ollama | | | | | |
| API 1 | | | | | |
| API 2 | | | | | |

## Evidencias

```text
[CAPTURA 1: Prueba con Ollama]
[CAPTURA 2: Prueba con API externa 1]
[CAPTURA 3: Prueba con API externa 2]
```

## Análisis

```text
Responder:
- ¿Qué modelo fue más rápido?
- ¿Qué modelo fue más claro?
- ¿Qué modelo fue más preciso?
- ¿Qué modelo convendría usar en una aplicación real?
- ¿Qué riesgos tendría usar una API externa?
```

## Conclusión

```text
Escribir una conclusión de 150 a 250 palabras.
```


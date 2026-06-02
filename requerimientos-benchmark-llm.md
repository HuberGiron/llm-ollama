---
layout: default
title: Requerimientos y ajustes LLM
nav_order: 2
---

# Requerimientos técnicos, costos, parámetros y benchmarking de LLM

Esta sección aborda los criterios técnicos para ejecutar modelos grandes de lenguaje (*Large Language Models*, LLM) en una computadora local, un servidor, una API en la nube o una plataforma embebida. El propósito es que el estudiante comprenda la relación entre **memoria**, **cómputo**, **latencia**, **tokens**, **costo**, **parámetros de generación** y **calidad de respuesta** antes de seleccionar un modelo o una arquitectura de implementación.

El tema se apoya en documentación oficial de Ollama, Hugging Face, OpenAI, Google AI, NVIDIA y Espressif, así como en literatura sobre eficiencia, cuantización, consumo energético e integración de modelos de lenguaje en robótica [1]–[11].

> 🎯 **Objetivo de aprendizaje:** Al finalizar esta actividad, el estudiante será capaz de explicar los requerimientos técnicos para ejecutar LLM; distinguir entre CPU, GPU, RAM y VRAM; estimar costos locales y en la nube; configurar parámetros de generación; diseñar un benchmark con Python y Ollama; exportar resultados en CSV; y justificar la selección de un modelo en alguna plataforma de cómputo.

---

## 1. Elegir “el mejor modelo”

Seleccionar un LLM no consiste únicamente en escoger el modelo con mayor número de parámetros o el que aparece mejor posicionado en una tabla de evaluación. En una aplicación real, especialmente si se relaciona con sistemas al borde o **edge computing** como en robótica, automatización o sistemas ciberfísicos, la decisión debe considerar simultáneamente:

- Si el modelo cabe en la memoria disponible;
- Si la velocidad de respuesta es aceptable;
- Si la latencia permite interactuar con el usuario o con el sistema;
- Si el costo local o en la nube es sostenible;
- Si el modelo puede ejecutarse con privacidad suficiente;
- Si la calidad de respuesta justifica los recursos usados;
- Si el modelo es adecuado para la tarea específica.

En este contexto, el uso de LLM en robótica y sistemas ciberfísicos puede entenderse como parte del campo emergente de la **IA física** (Physical AI). A diferencia de una IA limitada al procesamiento de texto, imágenes o datos en entornos digitales, la IA física se refiere a sistemas capaces de percibir el mundo real mediante sensores, razonar o planificar a partir de esa información, y actuar sobre el entorno mediante actuadores, robots, vehículos o máquinas autónomas. Por ello, cuando un LLM se integra con plataformas robóticas, sistemas embebidos, cámaras, sensores, motores o servicios de control, deja de ser únicamente un modelo conversacional y se convierte en un componente de una arquitectura que conecta lenguaje, percepción, decisión y acción física. Esta distinción es importante porque los requerimientos técnicos ya no dependen solo de la calidad del modelo, sino también de la latencia, memoria, consumo energético, seguridad, conectividad y capacidad de operar en tiempo real o cerca del tiempo real [14].

En la IA física, un LLM no es un controlador de bajo nivel en tiempo real. normalmente se utiliza como interfaz conversacional, planificador de alto nivel, generador de instrucciones, traductor de lenguaje natural a comandos estructurados o asistente de diagnóstico. Sin embargo, el control directo de motores, la lectura de sensores críticos y los lazos de realimentación de baja latencia deben mantenerse en componentes deterministas y verificables.

Un modelo de lenguaje aporta conocimiento semántico de alto nivel, pero sus propuestas se combinan con funciones de valor asociadas a habilidades robóticas para seleccionar acciones que sean no solo lingüísticamente plausibles, sino también físicamente ejecutables por el robot [10], [11].

> ⚠️ **Consideración:** En aplicaciones robóticas, un LLM debe tratarse como un componente de razonamiento, planificación o interacción, no como sustituto directo de los controladores de seguridad, navegación, cinemática, dinámica o control de motores.

![Modelo](assets/img/benchmark/)

---

## 2. Requerimientos técnicos para ejecutar LLM

### 2.1 RAM, VRAM y pesos del modelo

La memoria es uno de los factores más importantes para ejecutar un LLM. Un modelo no puede responder si sus pesos, su contexto y sus estructuras temporales no caben en la memoria disponible.

La **RAM** es la memoria principal del sistema. Se utiliza cuando el modelo se ejecuta en CPU o cuando parte del modelo no cabe en la GPU. La **VRAM** es la memoria de la tarjeta gráfica. Si el modelo cabe en VRAM, la inferencia suele ser más rápida porque la GPU puede realizar operaciones matriciales en paralelo y con mayor ancho de banda de memoria.

Durante la inferencia se requiere memoria para:

- Cargar los pesos del modelo;
- Almacenar el prompt y el contexto de conversación;
- Mantener la caché de atención o *KV cache*;
- Procesar tokens de entrada;
- Generar tokens de salida;
- Almacenar buffers internos del sistema de inferencia.

Una aproximación inicial para estimar memoria es:

```text
memoria_pesos ≈ número_de_parámetros × bytes_por_parámetro
```

Por ejemplo, un modelo de 7 mil millones de parámetros puede requerir aproximadamente:

| Precisión o cuantización | Bytes aproximados por parámetro | Memoria aproximada para 7B parámetros |
|---|---:|---:|
| FP32 | 4 bytes | 28 GB |
| FP16 / BF16 | 2 bytes | 14 GB |
| INT8 | 1 byte | 7 GB |
| INT4 | 0.5 bytes | 3.5 GB |

Hugging Face explica que la cuantización reduce el costo de memoria y cómputo al representar pesos y activaciones con tipos de menor precisión, como 8 bits o 4 bits. Esto permite cargar modelos más grandes en hardware limitado, aunque puede introducir compromisos en precisión, compatibilidad o velocidad [4].

---

### 2.2 CPU vs GPU

La **CPU** es flexible y está presente en prácticamente cualquier computadora. Puede ejecutar modelos pequeños o medianos, sobre todo si están cuantizados. Sin embargo, suele ser más lenta para inferencia de LLM porque estos modelos requieren muchas operaciones matriciales y acceso intensivo a memoria.

La **GPU** está diseñada para cómputo paralelo. Cuando el modelo cabe en VRAM, puede generar más tokens por segundo y reducir la latencia. Por esa razón, las GPUs son ampliamente utilizadas para entrenamiento e inferencia de modelos profundos.

| Elemento | CPU | GPU |
|---|---|---|
| Ventaja principal | Flexibilidad y disponibilidad | Paralelismo y velocidad |
| Limitación principal | Baja velocidad en modelos grandes | VRAM limitada y mayor costo |
| Memoria usada | RAM del sistema | VRAM de la tarjeta gráfica |
| Uso recomendado | Pruebas, modelos pequeños, equipos sin GPU | Modelos medianos, baja latencia, experimentación intensiva |
| Ejemplos de modelos viables | TinyLlama, Llama 3.2 1B/3B cuantizados | Llama 3.2 3B, Qwen 7B, Mistral 7B cuantizados |

En LLM, el cuello de botella no siempre es solo la capacidad de cómputo; también puede ser el ancho de banda de memoria. La literatura sobre cuantización y eficiencia en LLM muestra que reducir precisión puede disminuir memoria y acelerar inferencia, especialmente en hardware limitado [5], [6].

---

### 2.3 Tamaño de contexto y memoria

La **ventana de contexto** indica cuántos tokens puede considerar el modelo durante una interacción. No debe confundirse con memoria humana ni memoria permanente. El contexto es la información disponible para el modelo en una solicitud o conversación activa.

Ejemplos de configuración:

```text
num_ctx = 2048   → contexto corto
num_ctx = 4096   → contexto medio
num_ctx = 8192   → contexto amplio
num_ctx = 64000  → contexto largo para documentos, agentes o código
```

Ollama define la longitud de contexto como el número máximo de tokens accesibles en memoria para el modelo. Su documentación indica que, por defecto, Ollama ajusta la longitud de contexto según la VRAM disponible: menos de 24 GiB usa 4k, entre 24 y 48 GiB usa 32k y 48 GiB o más usa 256k. También advierte que incrementar la ventana de contexto incrementa la memoria requerida [3].

Para una práctica de clase, es recomendable iniciar con valores moderados:

```text
num_ctx = 2048 o 4096
num_predict = 100 a 200
```

Esto ayuda a evitar que equipos con poca RAM o VRAM se saturen y permite comparar modelos bajo condiciones más controladas.

> ⚠️ **Consideración técnica:** Aumentar `num_ctx` puede mejorar la capacidad para procesar documentos largos, pero también puede aumentar memoria, tiempo de procesamiento y riesgo de saturar la GPU.

---

## 3. Comparativa de plataformas de cómputo

### 3.1 PC local

Una PC local es una plataforma adecuada para aprendizaje, pruebas, desarrollo de prototipos y ejecución de modelos pequeños o medianos. Su ventaja principal es que permite trabajar sin pagar por tokens y sin depender de una API externa. Su limitación es que el rendimiento depende directamente del hardware disponible.

En una PC local deben revisarse:

- memoria RAM;
- CPU;
- GPU;
- VRAM;
- almacenamiento disponible;
- ventilación y consumo energético;
- sistema operativo;
- compatibilidad con Ollama, drivers y bibliotecas.

**Uso recomendado:** clase práctica, experimentación con Ollama, comparación de modelos pequeños, pruebas de prompts, desarrollo de prototipos y conexión con robots mediante una computadora intermedia.

---

### 3.2 API en la nube

Una API en la nube permite usar modelos potentes sin administrar directamente servidores ni GPUs. El proveedor se encarga del modelo, infraestructura, escalabilidad y disponibilidad. En este esquema, el costo suele calcularse por tokens de entrada y salida. OpenAI y Google AI publican precios por millón de tokens, con tarifas diferenciadas por modelo, entrada, salida y, en algunos casos, caché de contexto o herramientas adicionales [8], [9].

**Ventajas:**

- no requiere GPU local;
- acceso a modelos avanzados;
- implementación rápida;
- escalabilidad;
- mantenimiento reducido.

**Desventajas:**

- costo variable por uso;
- dependencia de internet;
- latencia de red;
- restricciones de privacidad;
- límites de tasa;
- cambios de precio o disponibilidad;
- dependencia del proveedor.

---

### 3.3 Servidor propio en la nube con GPU

Un servidor en la nube con GPU permite ejecutar modelos open-source o personalizados con mayor control que una API comercial. A diferencia de una API, aquí se paga por la máquina virtual, almacenamiento, tráfico, administración y tiempo de uso.

**Ventajas:**

- control del modelo;
- posibilidad de servir múltiples usuarios;
- integración con backend propio;
- uso de modelos específicos;
- despliegue de servicios con Ollama, vLLM, TGI u otras herramientas.

**Desventajas:**

- configuración de drivers y dependencias;
- administración de seguridad;
- monitoreo;
- costo por hora aunque no haya uso constante;
- necesidad de mantenimiento técnico.

---

### 3.4 Sistemas embebidos: microcontroladores y tarjetas de IA

Es importante diferenciar entre **microcontroladores** y **computadoras embebidas para IA**.

Un microcontrolador como ESP32, Arduino o STM32 no es una plataforma adecuada para ejecutar localmente un LLM moderno. Puede leer sensores, controlar motores, comunicarse por WiFi/BLE/MQTT y enviar datos a un servidor o API, pero no tiene memoria suficiente para cargar modelos de lenguaje generales. Por ejemplo, módulos ESP32-S3-MINI pueden tener hasta 8 MB de flash y opcionalmente 2 MB de PSRAM, cantidades muy por debajo de los GB requeridos por modelos LLM incluso cuantizados [7].

En cambio, una tarjeta como NVIDIA Jetson Orin Nano Super Developer Kit es una computadora embebida orientada a IA. NVIDIA reporta hasta 67 INT8 TOPS, GPU Ampere con 1024 núcleos CUDA y 32 Tensor Cores, CPU Arm de 6 núcleos, 8 GB LPDDR5 y consumo de 7 W a 25 W [6]. Esta clase de plataforma puede ejecutar modelos pequeños o medianos cuantizados, especialmente en aplicaciones de borde, robótica, visión e inferencia local.

| Plataforma | ¿Puede ejecutar LLM local? | Uso recomendado |
|---|---|---|
| Microcontrolador ESP32 | No para LLM modernos generales | Sensores, actuadores, comunicación, adquisición de datos |
| Raspberry Pi | Limitado; modelos pequeños cuantizados con baja velocidad | Prototipos educativos, cliente local, interfaz |
| Jetson Orin Nano | Sí, con modelos pequeños/medianos cuantizados y restricciones | Robótica móvil, visión, inferencia en borde |
| PC con CPU | Sí, modelos pequeños/medianos cuantizados | Clase, pruebas, prototipos |
| PC con GPU | Sí, mejor velocidad si el modelo cabe en VRAM | Desarrollo, evaluación, integración robótica |
| Servidor GPU | Sí, modelos medianos o grandes | Producción, investigación, múltiples usuarios |
| API comercial | Sí, como servicio externo | Aplicaciones web, prototipos rápidos, modelos avanzados |

> 🖼️ **Espacio para imagen sugerida:** mapa comparativo desde microcontrolador → Jetson → PC local → servidor GPU → API nube.  
> Archivo sugerido: `assets/img/llm/tema2/04-plataformas-computo-llm.png`

---

## 4. Tokens, latencia, memoria y costos

### 4.1 Tokens

Un **token** es una unidad de texto procesada por el modelo. Puede ser una palabra, una parte de una palabra, un signo de puntuación, un número o una pieza de código. En LLM, la memoria, el tiempo y el costo dependen principalmente de:

```text
tokens_totales = tokens_entrada + tokens_salida
```

Un prompt más largo exige más procesamiento de entrada. Una respuesta más larga exige más generación autoregresiva. Por esta razón, en aplicaciones robóticas conviene diseñar prompts compactos y respuestas estructuradas.

Ejemplo:

```text
Prompt corto:
"Resume qué es un sensor ultrasónico en 50 palabras."

Prompt largo:
"Lee todo este manual técnico, analiza sus limitaciones, identifica riesgos,
extrae instrucciones y genera un plan de integración robótica..."
```

El segundo prompt consume más tokens, requiere más memoria y normalmente produce mayor latencia.

---

### 4.2 Latencia

La **latencia** es el tiempo que tarda el sistema en responder. En un LLM puede descomponerse en varios componentes:

| Componente | Descripción |
|---|---|
| Tiempo de carga | Tiempo para cargar el modelo en memoria |
| Evaluación del prompt | Tiempo para procesar tokens de entrada |
| Generación | Tiempo para producir tokens de salida |
| Latencia de red | Aplica si se usa nube o servidor remoto |
| Postprocesamiento | Validar JSON, guardar resultados o ejecutar acciones |

Ollama permite obtener métricas de inferencia cuando se usa su API con `stream: false`. Entre los campos útiles se encuentran `total_duration`, `load_duration`, `prompt_eval_count`, `prompt_eval_duration`, `eval_count` y `eval_duration` [2].

Métricas recomendadas:

```text
tiempo_total_s = total_duration / 1e9
tiempo_carga_s = load_duration / 1e9
tokens_entrada = prompt_eval_count
tokens_salida = eval_count
tiempo_generacion_s = eval_duration / 1e9
tokens_por_segundo = eval_count / tiempo_generacion_s
```

> 🖼️ **Espacio para imagen sugerida:** línea de tiempo de una solicitud LLM: cargar modelo → procesar prompt → generar respuesta → guardar métricas.  
> Archivo sugerido: `assets/img/llm/tema2/05-latencia-inferencia-llm.png`

---

### 4.3 Memoria durante la inferencia

La memoria durante una prueba depende de varios factores:

- tamaño del modelo;
- nivel de cuantización;
- longitud de contexto;
- número de solicitudes paralelas;
- uso de CPU o GPU;
- cantidad de modelos cargados simultáneamente;
- tiempo que el modelo permanece cargado con `keep_alive`.

Ollama permite mantener un modelo cargado cierto tiempo mediante `keep_alive`, lo que reduce el tiempo de carga en solicitudes posteriores. Esto mejora la latencia en experimentos repetidos, pero aumenta el tiempo durante el cual RAM o VRAM permanecen ocupadas [2].

---

### 4.4 Costo energético local

El costo energético local puede estimarse con:

```text
energía_kWh = (potencia_W / 1000) × tiempo_horas
costo = energía_kWh × precio_kWh
```

Ejemplo:

```text
Una PC que consume 180 W durante 2 horas:
energía = (180 / 1000) × 2 = 0.36 kWh
```

Este costo puede parecer bajo para una práctica individual, pero crece cuando se ejecutan muchos experimentos, se usan GPUs de alto consumo, se realizan pruebas durante varias horas o se atienden múltiples usuarios.

La literatura académica sobre NLP y LLM ha señalado que el cómputo profundo implica costos financieros y ambientales, tanto en entrenamiento como en inferencia. Strubell, Ganesh y McCallum documentaron la relevancia del costo energético en NLP moderno, y estudios recientes han analizado cómo las optimizaciones de inferencia pueden modificar significativamente el consumo energético en LLM [12], [13].

---

### 4.5 Costo por tokens en la nube

En servicios API, el costo depende del número de tokens procesados y del modelo seleccionado. Generalmente se cobra por millón de tokens de entrada y salida. La salida suele ser más costosa que la entrada porque generar texto implica inferencia autoregresiva.

Fórmula general:

```text
costo_total =
(tokens_entrada / 1,000,000 × precio_entrada)
+
(tokens_salida / 1,000,000 × precio_salida)
```

Ejemplo de plantilla para cálculo:

| Variable | Valor de ejemplo |
|---|---:|
| Tokens de entrada | 100,000 |
| Tokens de salida | 50,000 |
| Precio entrada por 1M tokens | Consultar proveedor |
| Precio salida por 1M tokens | Consultar proveedor |
| Costo total | Calcular con la fórmula |

> ⚠️ **Consideración:** Los precios de APIs cambian con frecuencia. Para un documento académico o práctica de clase, se recomienda consultar siempre la página oficial del proveedor el día de la actividad [8], [9].

---

### 4.6 Costo de implementación

El costo de implementación no se limita al pago de energía o tokens. También incluye:

- tiempo de instalación y configuración;
- selección del modelo;
- evaluación de calidad;
- integración con backend;
- seguridad;
- monitoreo;
- almacenamiento de logs;
- pruebas;
- documentación;
- mantenimiento;
- capacitación de usuarios;
- mitigación de errores y alucinaciones.

En un proyecto robótico, además deben considerarse sensores, comunicación, sistemas de seguridad, pruebas de campo y mecanismos de recuperación ante errores.

---

## 5. Parámetros de configuración de un LLM

Los parámetros de generación modifican el comportamiento del modelo. No cambian los pesos entrenados, pero sí afectan cómo se seleccionan los tokens durante la respuesta. Ollama permite configurar muchos de estos parámetros desde el `Modelfile` o desde la API mediante el campo `options` [1], [2].

| Parámetro | Para qué sirve | Valores típicos | Efecto esperado |
|---|---|---|---|
| `temperature` | Controla creatividad o aleatoriedad. Bajo = más determinista; alto = más creativo. | `0.0` a `1.2` | Aumentar puede producir respuestas más variadas, pero también más errores. |
| `top_p` | Filtra tokens por probabilidad acumulada. Bajo = más conservador. | `0.7` a `0.95` | Reduce o amplía el conjunto de tokens candidatos. |
| `top_k` | Limita cuántos tokens candidatos considera. | `20`, `40`, `80` | Bajo = generación más cerrada; alto = más diversidad. |
| `min_p` | Filtra tokens demasiado improbables respecto al token más probable. | `0.0` a `0.1` | Alternativa moderna para controlar variedad sin abrir excesivamente la distribución. |
| `num_predict` | Máximo de tokens que puede generar la respuesta. | `100`, `500`, `1000` | Limita longitud, costo, memoria y latencia. |
| `num_ctx` | Tamaño de ventana de contexto. | `2048`, `4096`, `8192` | A mayor contexto, mayor memoria requerida. |
| `repeat_penalty` | Penaliza repeticiones. Mayor = menos repetitivo. | `1.1` a `1.5` | Reduce bucles o frases repetidas, pero valores altos pueden afectar fluidez. |
| `repeat_last_n` | Define cuántos tokens recientes revisa para evitar repetición. | `64`, `128`, `-1` | `-1` suele indicar revisar toda la ventana disponible. |
| `seed` | Semilla para reproducibilidad. | `42`, `123`, `2026` | Permite comparar salidas de forma más controlada. |
| `stop` | Secuencias donde debe detenerse la generación. | `["\nUsuario:", "</final>"]` | Útil en chat, agentes o respuestas estructuradas. |
| `num_thread` | Hilos de CPU usados. | `4`, `8`, `12` | Puede mejorar rendimiento en CPU, según procesador. |
| `num_gpu` | Capas o uso de GPU según backend y hardware. | `0`, `1`, `-1`, depende | Permite controlar si se usa GPU o CPU, según compatibilidad. |
| `keep_alive` | Tiempo que el modelo queda cargado en memoria. | `"5m"`, `"30m"`, `0` | Reduce tiempo de carga entre solicitudes, pero ocupa memoria. |
| `format` | Fuerza salida JSON o esquema estructurado. | `"json"` o JSON Schema | Útil para evaluación automática, APIs y robótica. |
| `stream` | Devuelve respuesta por partes o completa. | `true` / `false` | `false` facilita benchmark porque devuelve métricas al final. |

Ejemplo de uso desde la API de Ollama:

```json
{
  "model": "llama3.2:3b",
  "prompt": "Explica qué es un sensor ultrasónico en máximo 100 palabras.",
  "stream": false,
  "keep_alive": "30m",
  "options": {
    "temperature": 0.7,
    "top_p": 0.9,
    "top_k": 40,
    "num_ctx": 4096,
    "num_predict": 120,
    "repeat_penalty": 1.1
  }
}
```

> 🖼️ **Espacio para imagen sugerida:** diagrama de parámetros de generación: diversidad (`temperature`, `top_p`, `top_k`), longitud (`num_predict`, `num_ctx`) y rendimiento (`num_thread`, `num_gpu`, `keep_alive`).  
> Archivo sugerido: `assets/img/llm/tema2/06-parametros-generacion-llm.png`

---

## 6. Metodología de benchmark con Python y Ollama

### 6.1 Objetivo del benchmark

Un benchmark no debe limitarse a preguntar “qué modelo responde mejor”. Debe medir el comportamiento del modelo bajo condiciones controladas. En esta práctica se propone evaluar:

- tiempo total de respuesta;
- tiempo de carga;
- tokens de entrada;
- tokens de salida;
- tokens por segundo;
- longitud de la respuesta;
- variabilidad entre ciclos;
- calidad conceptual;
- cumplimiento del límite de tokens;
- viabilidad para la aplicación robótica.

Ollama expone una API local en `http://localhost:11434/api`, lo que permite automatizar pruebas desde Python y guardar resultados en CSV [2].

---

### 6.2 Preparación del entorno

Antes de ejecutar el benchmark, se recomienda instalar los modelos seleccionados:

```bash
ollama pull llama3.2:3b
ollama pull qwen2.5:7b
ollama pull mistral:7b
```

Verificar los modelos instalados:

```bash
ollama ls
```

Verificar modelos cargados en memoria:

```bash
ollama ps
```

Instalar dependencias de Python:

```bash
python -m venv .venv

# Windows PowerShell
.\.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate

pip install requests pandas
```

> 🖼️ **Espacio para captura:** terminal con `ollama ls`.  
> Archivo sugerido: `assets/img/llm/tema2/captura-ollama-ls.png`

---

### 6.3 Diseño experimental A: comparación entre modelos

El primer experimento compara mínimo tres modelos con el mismo prompt y los mismos parámetros.

```text
Modelos:
- llama3.2:3b
- qwen2.5:7b
- mistral:7b

Prompt fijo:
"Explica en máximo 120 palabras cómo podría usarse un LLM
como asistente de alto nivel para un robot móvil universitario."

Ciclos:
100 repeticiones por modelo

Total:
3 modelos × 100 ciclos = 300 ejecuciones
```

Condiciones recomendadas:

```json
{
  "temperature": 0.7,
  "top_p": 0.9,
  "top_k": 40,
  "min_p": 0.0,
  "num_ctx": 4096,
  "num_predict": 160,
  "repeat_penalty": 1.1
}
```

Para observar variabilidad, no se debe fijar una misma `seed` en todas las repeticiones. Para una comparación más reproducible, sí puede fijarse una semilla, pero eso reduce la variabilidad esperada.

---

### 6.4 Diseño experimental B: variación de parámetros

El segundo experimento usa un solo modelo y modifica tres parámetros, cada uno con tres configuraciones.

```text
Modelo sugerido:
llama3.2:3b

Prompt fijo:
"Explica en máximo 120 palabras qué es un sensor ultrasónico
y cómo podría usarse en un robot móvil educativo."
```

| Parámetro | Configuración 1 | Configuración 2 | Configuración 3 |
|---|---:|---:|---:|
| `temperature` | `0.0` | `0.7` | `1.1` |
| `top_p` | `0.7` | `0.9` | `0.95` |
| `repeat_penalty` | `1.0` | `1.2` | `1.5` |

Diseño total:

```text
3 parámetros × 3 configuraciones × 100 ciclos = 900 ejecuciones
```

Este experimento permite observar cómo cambian estabilidad, longitud, repetición, diversidad y calidad de respuesta.

---

### 6.5 Campos mínimos del CSV

El CSV debe incluir variables suficientes para reproducir y analizar el experimento.

| Campo | Descripción |
|---|---|
| `timestamp` | Fecha y hora de la ejecución |
| `experiment_id` | Identificador del experimento |
| `model` | Modelo usado |
| `cycle` | Número de ciclo |
| `prompt` | Prompt utilizado |
| `temperature` | Valor usado |
| `top_p` | Valor usado |
| `top_k` | Valor usado |
| `min_p` | Valor usado |
| `num_ctx` | Ventana de contexto |
| `num_predict` | Límite de tokens generados |
| `repeat_penalty` | Penalización por repetición |
| `response` | Respuesta generada |
| `total_duration_s` | Tiempo total |
| `load_duration_s` | Tiempo de carga |
| `prompt_eval_count` | Tokens de entrada |
| `eval_count` | Tokens de salida |
| `eval_duration_s` | Tiempo de generación |
| `tokens_per_second` | Velocidad de generación |
| `response_chars` | Longitud en caracteres |
| `quality_score` | Evaluación de calidad |
| `notes` | Errores u observaciones |

---

### 6.6 Evaluación de calidad de respuesta

La calidad no debe medirse únicamente por velocidad. Para esta práctica se propone una rúbrica de 0 a 10:

| Criterio | Puntaje |
|---|---:|
| Corrección conceptual | 0 a 3 |
| Claridad para el público objetivo | 0 a 2 |
| Concisión y respeto al límite de tokens | 0 a 2 |
| Utilidad para la aplicación robótica | 0 a 2 |
| Ausencia de errores graves o alucinaciones | 0 a 1 |
| **Total** | **10** |

La evaluación puede realizarse de tres maneras:

1. evaluación manual por el estudiante;
2. revisión cruzada entre equipos;
3. evaluación asistida por otro modelo, aclarando que no sustituye la validación humana.

Para iniciar de forma sencilla, el script puede calcular una **evaluación heurística** mediante longitud, palabras clave, respuesta no vacía y repetición extrema. Esta métrica no reemplaza la revisión humana, pero ayuda a automatizar una primera comparación.

> 🖼️ **Espacio para imagen sugerida:** flujo de benchmark: prompt → Ollama API → CSV → análisis → matriz de decisión.  
> Archivo sugerido: `assets/img/llm/tema2/07-flujo-benchmark-ollama-python.png`

---

## 7. Script 1: benchmark comparativo entre modelos

Guarda el siguiente archivo como `benchmark_modelos.py`.

```python
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

    # Longitud razonable para una respuesta breve.
    if 200 <= len(response_text) <= 900:
        score += 2

    # Presencia de palabras clave esperadas.
    matches = sum(1 for word in keywords if word in text)
    score += min(matches, 4)

    # Respuesta no vacía y con desarrollo mínimo.
    if len(text) > 50:
        score += 2

    # Penalización simple por repetición extrema.
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
```

Ejecutar:

```bash
python benchmark_modelos.py
```

---

## 8. Script 2: benchmark por variación de parámetros

Guarda el siguiente archivo como `benchmark_parametros.py`.

```python
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
```

Ejecutar:

```bash
python benchmark_parametros.py
```

---

## 9. Script 3: análisis del CSV

Guarda el siguiente archivo como `analizar_benchmark.py`.

```python
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
```

Ejecutar:

```bash
python analizar_benchmark.py
```

Tabla esperada:

| Modelo | Tiempo promedio | Tokens entrada | Tokens salida | Tokens/s | Calidad promedio | Observación |
|---|---:|---:|---:|---:|---:|---|
| `llama3.2:3b` | | | | | | |
| `qwen2.5:7b` | | | | | | |
| `mistral:7b` | | | | | | |

> 🖼️ **Espacio para captura:** CSV generado y resumen estadístico en terminal.  
> Archivo sugerido: `assets/img/llm/tema2/captura-csv-benchmark.png`

---

## 10. Actividad 2

### Actividad 2. Selección de plataforma y benchmark de modelos LLM

#### Objetivo

Construir una matriz de decisión para seleccionar una plataforma de cómputo adecuada para ejecutar o consumir LLM en una aplicación robótica, considerando presupuesto, recursos de hardware, latencia, privacidad, costo energético, costo por tokens y calidad de respuesta.

---

### Parte A. Matriz de decisión

El estudiante debe comparar al menos cuatro plataformas. Se recomienda incluir:

1. PC local con CPU;
2. PC local con GPU;
3. API en la nube;
4. servidor GPU en nube;
5. sistema embebido tipo Jetson;
6. microcontrolador conectado a API.

Criterios sugeridos:

| Criterio | Peso sugerido |
|---|---:|
| Costo inicial | 10 % |
| Costo operativo | 15 % |
| Latencia | 15 % |
| Privacidad | 10 % |
| Facilidad de implementación | 10 % |
| Capacidad de ejecutar modelos locales | 15 % |
| Compatibilidad con robótica | 15 % |
| Escalabilidad | 10 % |

Cada plataforma se evalúa de 1 a 5.

```text
Puntaje final = suma(puntaje × peso)
```

Plantilla:

| Plataforma | Costo inicial | Costo operativo | Latencia | Privacidad | Implementación | Modelo local | Robótica | Escalabilidad | Puntaje final |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| PC local CPU | | | | | | | | | |
| PC local GPU | | | | | | | | | |
| API nube | | | | | | | | | |
| Servidor GPU nube | | | | | | | | | |
| Jetson | | | | | | | | | |
| Microcontrolador + API | | | | | | | | | |

---

### Parte B. Benchmark de modelos

El estudiante debe:

1. seleccionar mínimo 3 modelos;
2. ejecutar 100 ciclos por modelo;
3. usar el mismo prompt;
4. limitar la respuesta con `num_predict`;
5. exportar un CSV con las respuestas;
6. calcular promedio, desviación estándar, mínimo y máximo de:
   - tiempo total;
   - tokens de entrada;
   - tokens de salida;
   - tokens por segundo;
   - calidad estimada.

Tabla final esperada:

| Modelo | Tiempo promedio | Tokens entrada | Tokens salida | Tokens/s | Calidad promedio | Justificación |
|---|---:|---:|---:|---:|---:|---|
| Modelo 1 | | | | | | |
| Modelo 2 | | | | | | |
| Modelo 3 | | | | | | |

---

### Parte C. Evaluación de calidad

Con el CSV de salida, el estudiante debe evaluar la calidad de al menos 10 respuestas por modelo. Puede usar la rúbrica de 0 a 10 propuesta en la sección 6.6.

Preguntas guía:

1. ¿El modelo responde correctamente al prompt?
2. ¿Respeta el límite de longitud?
3. ¿La respuesta es clara para el público objetivo?
4. ¿Incluye errores conceptuales?
5. ¿La respuesta es útil para una aplicación robótica?
6. ¿El modelo repite frases o genera contenido innecesario?

---

### Parte D. Variación de parámetros

El estudiante debe seleccionar un solo modelo, usar un prompt fijo y variar tres parámetros diferentes, cada uno con tres configuraciones.

Ejemplo:

| Parámetro | Configuraciones |
|---|---|
| `temperature` | `0.0`, `0.7`, `1.1` |
| `top_p` | `0.7`, `0.9`, `0.95` |
| `repeat_penalty` | `1.0`, `1.2`, `1.5` |

Debe ejecutar 100 ciclos por configuración y exportar un CSV.

Preguntas guía:

1. ¿Qué configuración produjo respuestas más consistentes?
2. ¿Qué configuración produjo mayor variabilidad?
3. ¿Qué parámetro afectó más la longitud de la respuesta?
4. ¿Qué parámetro afectó más la calidad?
5. ¿Qué configuración sería más adecuada para una aplicación robótica?
6. ¿Qué configuración sería más adecuada para lluvia de ideas o generación creativa?

---

## 11. Entregables

Cada estudiante o equipo debe entregar:

1. Captura de `ollama ls` con los modelos instalados.
2. Captura de ejecución de al menos un modelo desde terminal.
3. Archivo `benchmark_modelos.csv`.
4. Archivo `resumen_benchmark_modelos.csv`.
5. Archivo `benchmark_parametros.csv`.
6. Matriz de decisión de plataformas.
7. Tabla comparativa final de modelos.
8. Breve justificación de selección de plataforma y modelo.
9. Reflexión sobre limitaciones del experimento.

---

## 12. Criterios de evaluación

| Criterio | Porcentaje |
|---|---:|
| Instalación y ejecución correcta de Ollama | 10 % |
| Diseño adecuado del benchmark | 20 % |
| CSV completo y correctamente estructurado | 20 % |
| Análisis estadístico de resultados | 15 % |
| Evaluación de calidad de respuestas | 15 % |
| Matriz de decisión de plataforma | 10 % |
| Justificación técnica y académica | 10 % |

---

## 13. Consideraciones finales

Los LLM pueden ejecutarse localmente, en servidores propios, mediante APIs en la nube o como parte de arquitecturas híbridas. Cada opción implica compromisos. Una PC local puede ser adecuada para aprendizaje y prototipado, pero puede tener limitaciones de memoria y velocidad. Una API en la nube permite acceder a modelos avanzados, pero introduce costos por token, dependencia de internet y consideraciones de privacidad. Una tarjeta Jetson puede ser útil en robótica de borde, pero requiere seleccionar modelos pequeños o cuantizados. Un microcontrolador, por su parte, debe entenderse como un nodo de sensores, actuadores y comunicación, no como plataforma principal para ejecutar LLM modernos.

La selección responsable de un modelo requiere medir. Por ello, el benchmark debe registrar no solo la respuesta del modelo, sino también tiempo, tokens, velocidad, variabilidad, longitud, calidad y condiciones de ejecución. Sin estos datos, la elección del modelo se vuelve subjetiva y poco reproducible.

---

## 14. Referencias

[1] Ollama. “Modelfile Reference.” Disponible en: <https://docs.ollama.com/modelfile>

[2] Ollama. “Generate a response / API Reference.” Disponible en: <https://docs.ollama.com/api/generate>

[3] Ollama. “Context length.” Disponible en: <https://docs.ollama.com/context-length>

[4] Hugging Face. “Quantization.” *Transformers Documentation*. Disponible en: <https://huggingface.co/docs/transformers/en/main_classes/quantization>

[5] Hugging Face. “Optimizing LLMs for Speed and Memory.” *Transformers Documentation*. Disponible en: <https://huggingface.co/docs/transformers/llm_tutorial_optimization>

[6] NVIDIA. “Jetson Orin Nano Super Developer Kit.” Disponible en: <https://www.nvidia.com/en-us/autonomous-machines/embedded-systems/jetson-orin/nano-super-developer-kit/>

[7] Espressif Systems. “ESP32-S3-MINI-1 & ESP32-S3-MINI-1U Datasheet.” Disponible en: <https://documentation.espressif.com/esp32-s3-mini-1_mini-1u_datasheet_en.pdf>

[8] OpenAI. “API Pricing.” Disponible en: <https://developers.openai.com/api/docs/pricing>

[9] Google AI for Developers. “Gemini Developer API Pricing.” Disponible en: <https://ai.google.dev/gemini-api/docs/pricing>

[10] Ahn, M. et al. “Do As I Can, Not As I Say: Grounding Language in Robotic Affordances.” *arXiv*, 2022. Disponible en: <https://arxiv.org/abs/2204.01691>

[11] SayCan Project. “SayCan: Grounding Language in Robotic Affordances.” Disponible en: <https://say-can.github.io/>

[12] Strubell, E., Ganesh, A., & McCallum, A. “Energy and Policy Considerations for Deep Learning in NLP.” *Proceedings of ACL*, 2019. Disponible en: <https://aclanthology.org/P19-1355/>

[13] Fernandez, J., Na, C., Tiwari, V., Bisk, Y., Luccioni, S., & Strubell, E. “Energy Considerations of Large Language Model Inference and Efficiency Optimizations.” *ACL Anthology*, 2025. Disponible en: <https://aclanthology.org/2025.acl-long.1563/>

[14] NVIDIA. (s. f.). *What is Physical AI?* NVIDIA Glossary. Define la IA física como sistemas que permiten a máquinas autónomas percibir, comprender y realizar acciones complejas en el mundo físico.
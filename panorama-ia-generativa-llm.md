---
layout: default
title: IA generativa y LLM
nav_order: 2
---

# Panorama de IA generativa y LLM

Esta sección presenta un panorama académico de la **inteligencia artificial generativa** y los **modelos grandes de lenguaje** (*Large Language Models*, LLM). El propósito es distinguir los conceptos de inteligencia artificial, aprendizaje automático, aprendizaje profundo, IA generativa, embeddings, transformers y LLM, y después llevar esos conceptos a una práctica con **Ollama** y **Hugging Face**.

El contenido toma como base conceptual el *Machine Learning Crash Course* de Google, en particular los módulos de aprendizaje automático, embeddings, modelos grandes de lenguaje y transformers [1]–[3]. También se integran referencias oficiales de Ollama y Hugging Face para la parte práctica [4]–[6].

> 🎯 **Objetivo de aprendizaje:** Al finalizar esta actividad, el estudiante será capaz de explicar la diferencia entre IA, aprendizaje automático, IA generativa, embeddings, transformers y LLM; instalar y usar Ollama desde terminal; consultar modelos en Hugging Face; y comparar modelos según fabricante, licencia, tamaño, idioma y requerimientos técnicos.

---

## 1. De inteligencia artificial a LLM

La **inteligencia artificial** es el campo general que estudia y desarrolla sistemas capaces de realizar tareas asociadas con percepción, razonamiento, aprendizaje, lenguaje, toma de decisiones o generación de contenido. Dentro de ese campo, el **aprendizaje automático** (*machine learning*) se enfoca en construir modelos que aprenden patrones a partir de datos, en lugar de depender únicamente de reglas programadas manualmente.

Una forma útil de entender la relación entre los conceptos es la siguiente:

```text
Inteligencia artificial (IA)
└── Aprendizaje automático (Machine Learning, ML)
    └── Aprendizaje profundo (Deep Learning)
        └── Modelos generativos modernos
            └── Transformers y modelos grandes de lenguaje (LLM)
```

---

## 2. Aprendizaje automático

En aprendizaje automático, un modelo aprende una relación entre **entradas** y **salidas esperadas**. En un problema supervisado, las entradas suelen describirse mediante **características** (*features*) y la salida esperada se conoce como **etiqueta** (*label*). El objetivo del entrenamiento es ajustar los parámetros del modelo para reducir el error entre las predicciones y las respuestas correctas.

Ejemplo sencillo:

![Modelo](assets/img/llm/01-modelo.png)

En este caso, el modelo no está generando contenido nuevo. Está aprendiendo una relación estadística para clasificar o predecir una salida. Esta distinción será importante para diferenciar modelos predictivos tradicionales de modelos generativos.

### 2.1 Diferencia entre regresión, clasificación y generación

| Tipo de tarea | Pregunta principal | Ejemplo de entrada | Ejemplo de salida |
|---|---|---|---|
| Regresión | ¿Qué valor numérico se espera? | Temperatura, humedad, presión | Consumo energético estimado |
| Clasificación | ¿A qué categoría pertenece? | Texto de correo electrónico | Spam / No spam |
| Generación | ¿Qué contenido nuevo puede producirse? | Prompt textual | Explicación, resumen, código o imagen |

![Regresión vs Clasificasión vs Generación](assets/img/llm/02-regresion-clasificacion-generacion.png)

---

## 3. IA generativa

La **IA generativa** se refiere a modelos capaces de producir contenido nuevo a partir de una entrada. Ese contenido puede ser texto, imagen, audio, video, código o una combinación de modalidades.

En lugar de limitarse a responder con una clase o un valor numérico, un modelo generativo puede construir una respuesta completa. Por ejemplo:

![Prompt](assets/img/llm/03-flujo-ia-generativa.png)

La IA generativa no significa que el sistema “comprenda” como un humano. En términos técnicos, el modelo aprende patrones estadísticos en grandes conjuntos de datos y utiliza esos patrones para generar una salida plausible. Por eso sus respuestas pueden ser útiles, pero también pueden contener errores, omisiones o afirmaciones no verificadas.

> ⚠️ **Consideración:** Una respuesta fluida no equivale necesariamente a una respuesta correcta. Los LLM pueden producir información falsa con apariencia convincente; a este fenómeno se le conoce comúnmente como *alucinación*.

---

## 4. Modelos de lenguaje, tokens y LLM

Un **modelo de lenguaje** estima la probabilidad de que un **token** o una secuencia de tokens aparezca dentro de una secuencia más larga. De acuerdo con Google, un token puede ser una palabra, una subpalabra o incluso un carácter [2].

Ejemplo conceptual:

```text
Frase incompleta:
El aprendizaje automático permite que una computadora ________.

Posibles continuaciones:
- aprenda
- clasifique
- prediga
- genere
```

El modelo asigna probabilidades a posibles continuaciones y selecciona una respuesta con base en su entrenamiento y en los parámetros de generación.

Un **LLM** es un modelo de lenguaje de gran escala. Normalmente se caracteriza por:

- una gran cantidad de parámetros;
- entrenamiento con grandes volúmenes de texto y código;
- capacidad de procesar contexto amplio;
- arquitectura basada en transformers;
- habilidad para generar lenguaje, resumir, traducir, responder preguntas, seguir instrucciones y producir código.

---

## 5. Embeddings

Los **embeddings** son representaciones vectoriales de datos. Una palabra, frase, documento, imagen o fragmento de código puede representarse como un vector numérico. La utilidad de un embedding es que elementos con significado parecido tienden a quedar cercanos en el espacio vectorial.

Ejemplo simplificado:

```text
"perro"       → [0.12, -0.45, 0.88, ...]
"gato"        → [0.10, -0.40, 0.81, ...]
"Tornillo"  → [0.72,  0.33, -0.21, ...]
```

En una aplicación real, estos vectores pueden tener cientos o miles de dimensiones. Su uso es importante para:

- búsqueda semántica;
- recuperación aumentada por generación (*Retrieval-Augmented Generation*, RAG);
- clasificación de documentos;
- recomendación de contenido;
- comparación de similitud entre textos.

![Similitud Semantica](assets/img/llm/05-embeddings-espacio-vectorial.png)

---

## 6. Transformers y autoatención

El **transformer** es la arquitectura dominante en muchos modelos modernos de lenguaje. Google presenta el transformer como una arquitectura exitosa para construir LLM y explica que puede estar formado por codificadores, decodificadores o combinaciones de ambos [3].

La idea central es la **autoatención** (*self-attention*). Este mecanismo permite que el modelo evalúe qué tokens del contexto son más importantes para interpretar otro token.

Ejemplo conceptual:

```text
Frase:
El robot tomó la herramienta porque la necesitaba para cortar madera.

Pregunta:
¿A qué se refiere "la"?

La autoatención ayuda a relacionar "la" con "herramienta".
```

Los modelos solo de decodificador son especialmente importantes en generación de texto, porque generan nuevos tokens a partir del texto previo. Muchos LLM conversacionales modernos utilizan arquitecturas de este tipo.

[Simulador de Transformer](https://poloclub.github.io/transformer-explainer/)

---

## 7. Diferencias principales entre conceptos

| Concepto | Definición breve | Ejemplo |
|---|---|---|
| IA | Campo general de sistemas capaces de realizar tareas asociadas con inteligencia | Un asistente que interpreta lenguaje natural |
| Aprendizaje automático | Subcampo donde los modelos aprenden patrones a partir de datos | Clasificador de correos spam |
| Deep Learning | Aprendizaje automático con redes neuronales profundas | Reconocimiento de imágenes |
| IA generativa | Modelos que producen contenido nuevo | Generación de texto, imagen o código |
| Embeddings | Representaciones vectoriales de datos | Vectores para búsqueda semántica |
| Transformer | Arquitectura neuronal basada en mecanismos de atención | Base de muchos LLM modernos |
| LLM | Modelo grande de lenguaje entrenado para procesar y generar texto | Llama, Gemma, Qwen, Mistral, Phi |

> 🖼️ **Espacio para imagen sugerida:** tabla visual o mapa conceptual para usar como resumen de la primera parte de la clase.  
> Archivo sugerido: `assets/img/llm/07-resumen-conceptos.png`

---

## 8. Repositorios y modelos: Hugging Face

**Hugging Face** es una plataforma donde la comunidad de aprendizaje automático comparte modelos, datasets y aplicaciones. Para esta clase, se utilizará como fuente para consultar información técnica y documental de modelos.

Un elemento central es la **model card**. Según la documentación de Hugging Face, una model card es un archivo que acompaña al modelo y contiene información útil; normalmente corresponde al archivo `README.md` del repositorio del modelo [6].

Al revisar un modelo en Hugging Face, el estudiante debe identificar:

| Elemento | Pregunta guía |
|---|---|
| Fabricante o desarrollador | ¿Quién creó el modelo? |
| Tipo de modelo | ¿Es base, instruct, chat, embedding, multimodal o código? |
| Licencia | ¿Permite uso académico, comercial, redistribución o modificación? |
| Parámetros | ¿Cuántos parámetros tiene? |
| Tamaño de descarga | ¿Cuánto ocupa en disco la versión usada? |
| Idiomas | ¿Qué idiomas soporta oficialmente? |
| Ventana de contexto | ¿Cuántos tokens puede procesar? |
| Formato | ¿Está en Safetensors, GGUF u otro formato? |
| Requerimientos | ¿Necesita GPU? ¿Puede ejecutarse cuantizado? |
| Limitaciones | ¿Reporta sesgos, restricciones, riesgos o alucinaciones? |

> 🖼️ **Espacio para captura sugerida:** página de un modelo en Hugging Face resaltando nombre, licencia, tipo, archivos y model card.  
> Archivo sugerido: `assets/img/llm/08-huggingface-model-card.png`

---

## 9. Tipos de modelos que se pueden encontrar

| Tipo de modelo | Uso principal | Ejemplo de uso en clase |
|---|---|---|
| Base / pretrained | Continuación de texto e investigación | Analizar cómo completa texto sin estar optimizado para chat |
| Instruct / chat | Seguimiento de instrucciones y conversación | Preguntar conceptos de IA en lenguaje natural |
| Embedding | Representación vectorial para búsqueda semántica | Buscar documentos parecidos dentro de un repositorio |
| Multimodal | Procesar texto e imagen | Describir una imagen o responder sobre una captura |
| Code model | Generar, completar o explicar código | Pedir un script simple de Python o JavaScript |
| Clasificador | Asignar categorías | Detección de sentimiento o moderación |
| GGUF cuantizado | Ejecución local eficiente | Ejecutar modelos en Ollama o llama.cpp |

> ⚠️ **Consideración importante:** No todos los modelos de Hugging Face pueden instalarse directamente con Ollama. Ollama trabaja especialmente bien con modelos disponibles en formato GGUF o con modelos ya publicados en la biblioteca de Ollama. Los modelos en Safetensors pueden requerir otra herramienta, conversión o una versión GGUF preparada por la comunidad.

---

## 10. Ollama

**Ollama** es una herramienta para descargar, ejecutar y administrar modelos localmente desde la terminal. Es útil para docencia porque permite experimentar con LLM en la computadora del estudiante sin depender necesariamente de una API comercial externa.

La documentación oficial de Ollama incluye comandos para ejecutar modelos, descargar modelos, listar modelos instalados, generar embeddings, eliminar modelos, ver modelos en ejecución y detener modelos [4].

> 🖼️ **Espacio para captura sugerida:** página oficial de Ollama o biblioteca de modelos.  
> Archivo sugerido: `assets/img/llm/09-ollama-library.png`

---

## 11. Instalación de Ollama

### 11.1 Windows

En Windows, se puede instalar desde el instalador oficial de Ollama o desde PowerShell.

```powershell
irm https://ollama.com/install.ps1 | iex
ollama --version
```

> 🖼️ **Espacio para captura requerida:** terminal de PowerShell mostrando `ollama --version`.  
> Archivo sugerido: `assets/img/llm/10-windows-ollama-version.png`

### 11.2 macOS y Linux

En macOS y Linux, la instalación puede realizarse desde terminal con:

```bash
curl -fsSL https://ollama.com/install.sh | sh
ollama --version
```

> 🖼️ **Espacio para captura requerida:** terminal de macOS o Linux mostrando `ollama --version`.  
> Archivo sugerido: `assets/img/llm/11-linux-mac-ollama-version.png`

---

## 12. Comandos básicos de Ollama

### 12.1 Descargar un modelo

```bash
ollama pull llama3.2:3b
```

### 12.2 Ejecutar un modelo

```bash
ollama run llama3.2:3b
```

### 12.3 Listar modelos instalados

```bash
ollama ls
```

### 12.4 Ver modelos cargados en memoria

```bash
ollama ps
```

### 12.5 Detener un modelo

```bash
ollama stop llama3.2:3b
```

### 12.6 Eliminar un modelo

```bash
ollama rm llama3.2:3b
```

### 12.7 Ejecutar un prompt directo

```bash
ollama run llama3.2:3b "Explica qué es un LLM en máximo 100 palabras."
```

> 🖼️ **Espacio para captura requerida:** terminal mostrando `ollama pull`, `ollama run` y una respuesta del modelo.  
> Archivo sugerido: `assets/img/llm/12-terminal-ollama-run.png`

---

## 13. Ejecución de modelos de embeddings con Ollama

Ollama también puede ejecutar modelos de embeddings. Estos modelos no están pensados principalmente para conversación, sino para convertir texto en vectores numéricos.

```bash
ollama pull nomic-embed-text
echo "Inteligencia artificial generativa" | ollama run nomic-embed-text
```

También puede utilizarse un modelo como `embeddinggemma`, siguiendo la documentación de Ollama:

```bash
ollama run embeddinggemma "Hello world"
```

> 🖼️ **Espacio para captura sugerida:** salida JSON o vector generada por un modelo de embeddings.  
> Archivo sugerido: `assets/img/llm/13-ollama-embeddings.png`

---

## 14. Uso de modelos de Hugging Face con Ollama

Hugging Face documenta que Ollama puede ejecutar modelos GGUF del Hub directamente con el formato [5]:

```bash
ollama run hf.co/{usuario}/{repositorio}
```

También permite indicar una cuantización específica:

```bash
ollama run hf.co/{usuario}/{repositorio}:{cuantizacion}
```

Ejemplo con un modelo GGUF de Qwen:

```bash
ollama run hf.co/Qwen/Qwen2.5-7B-Instruct-GGUF:Q4_K_M
```

> ⚠️ **Consideración importante:** usar `hf.co/...` con Ollama requiere que el repositorio sea compatible, normalmente porque contiene archivos GGUF. Si el modelo solo está en Safetensors, no necesariamente podrá ejecutarse directamente con Ollama.

> 🖼️ **Espacio para captura requerida:** página de Hugging Face con el menú `Use this model` → `Ollama`.  
> Archivo sugerido: `assets/img/llm/14-huggingface-use-with-ollama.png`

---

## 15. Modelos sugeridos para la actividad

Para la práctica, se recomiendan modelos pequeños o medianos que puedan ejecutarse en laptops con recursos razonables. Los modelos de 1B a 4B parámetros son más accesibles para equipos modestos. Los modelos de 7B pueden requerir más RAM, tardar más o beneficiarse claramente de GPU.

```bash
ollama pull llama3.2:3b
ollama pull gemma3:4b
ollama pull qwen2.5:7b
ollama pull mistral:7b
ollama pull phi4-mini
ollama pull tinyllama:1.1b-chat-v1-q8_0
```

> 🖼️ **Espacio para captura requerida:** terminal mostrando descarga de modelos.  
> Archivo sugerido: `assets/img/llm/15-ollama-pull-modelos.png`

Después de descargarlos, revisar los modelos instalados:

```bash
ollama ls
```

> 🖼️ **Espacio para captura requerida:** terminal mostrando `ollama ls` con nombre, ID, tamaño y fecha de instalación.  
> Archivo sugerido: `assets/img/llm/16-ollama-ls-modelos.png`

---

## 16. Prompts de prueba

Para comparar modelos, todos los equipos deben usar los mismos prompts.

### Prompt 1: explicación conceptual

```text
Explica la diferencia entre inteligencia artificial, aprendizaje automático,
IA generativa y LLM para estudiantes universitarios. Responde en español,
con tono académico y máximo 200 palabras.
```

### Prompt 2: embeddings

```text
Dame un ejemplo sencillo de uso de embeddings en una búsqueda semántica
dentro de un repositorio de documentos académicos.
```

### Prompt 3: evaluación crítica

```text
Menciona tres riesgos académicos de usar LLM sin verificar fuentes.
Incluye un ejemplo breve para cada riesgo.
```

### Prompt 4: uso técnico

```text
Dame un ejemplo de cómo un estudiante de ingeniería podría usar un LLM
para apoyar el desarrollo de un proyecto con ESP32, sin sustituir su aprendizaje.
```

> 🖼️ **Espacio para captura requerida:** respuesta de al menos tres modelos al mismo prompt.  
> Archivo sugerido: `assets/img/llm/17-comparacion-respuestas-modelos.png`

---

## 17. Tabla comparativa de modelos

La siguiente tabla se llena con información de Hugging Face, Ollama y la terminal del estudiante. Algunos campos se proporcionan como referencia inicial; el estudiante debe confirmar la información en la model card oficial y con `ollama ls`.

| Modelo | Fabricante / desarrollador | Tipo | Licencia | Parámetros | Idiomas reportados | Requerimiento sugerido para clase | Comando sugerido | Tamaño en Ollama |
|---|---|---|---|---:|---|---|---|---|
| Llama 3.2 3B Instruct | Meta | LLM instruct, texto a texto | Llama 3.2 Community License | 3.21B | Inglés, alemán, francés, italiano, portugués, hindi, español y tailandés [7] | Recomendable para equipos con recursos moderados; mejor con 8 GB RAM o más | `ollama run llama3.2:3b` | Completar con `ollama ls` |
| Gemma 3 4B IT | Google | LLM instruct multimodal, texto e imagen a texto | Gemma License | 4B | Más de 140 idiomas [8] | Requiere Ollama 0.6 o posterior; recomendable 8 GB RAM o más | `ollama run gemma3:4b` | Completar con `ollama ls` |
| Qwen2.5 7B Instruct | Qwen / Alibaba | LLM instruct | Apache 2.0 | 7.61B | Más de 29 idiomas, incluyendo español, inglés, chino, francés, portugués, alemán, italiano, ruso, japonés, coreano y otros [9] | Recomendable 16 GB RAM o GPU para mejor desempeño | `ollama run qwen2.5:7b` o `ollama run hf.co/Qwen/Qwen2.5-7B-Instruct-GGUF:Q4_K_M` | Completar con `ollama ls` |
| Mistral 7B Instruct v0.3 | Mistral AI | LLM instruct | Apache 2.0 | 7B | No siempre declara lista cerrada de idiomas; evaluar respuesta en español e inglés | Recomendable 16 GB RAM o GPU para mejor desempeño | `ollama run mistral:7b` | Completar con `ollama ls` |
| Phi-4-mini-instruct | Microsoft | LLM instruct compacto | MIT | 3.8B | Árabe, chino, checo, danés, neerlandés, inglés, finés, francés, alemán, hebreo, húngaro, italiano, japonés, coreano, noruego, polaco, portugués, ruso, español, sueco, tailandés, turco y ucraniano [11] | Diseñado para entornos con memoria/cómputo restringidos; requiere Ollama 0.5.13 o posterior según biblioteca de Ollama | `ollama run phi4-mini` | Completar con `ollama ls` |
| TinyLlama 1.1B Chat | TinyLlama | LLM chat compacto | Apache 2.0 | 1.1B | Principalmente inglés según tags de Hugging Face | Útil para equipos con recursos limitados; menor calidad esperada que modelos más grandes | `ollama run tinyllama:1.1b-chat-v1-q8_0` | Completar con `ollama ls` |

> ⚠️ **Nota sobre el tamaño:** En la tabla, “parámetros” se refiere al tamaño arquitectónico del modelo. El “tamaño en Ollama” es el espacio que ocupa la variante descargada en la computadora y depende del tag, formato y cuantización. Por eso debe registrarse desde `ollama ls`.

> 🖼️ **Espacio para captura requerida:** tabla llenada por el equipo o captura de la terminal usada para obtener el tamaño local de los modelos.  
> Archivo sugerido: `assets/img/llm/18-tabla-comparativa-modelos.png`

---

## 18. Actividad práctica

### Nombre de la actividad

**Instalación, ejecución y comparación de modelos LLM locales con Ollama y Hugging Face**

### Modalidad

Trabajo individual o en equipos de 2 a 3 estudiantes.

### Duración sugerida

Entre 90 y 120 minutos.

### Instrucciones

1. Instalar Ollama en la computadora.
2. Verificar la instalación con:

   ```bash
   ollama --version
   ```

3. Descargar al menos tres modelos desde Ollama.
4. Ejecutar al menos tres modelos con el mismo prompt.
5. Revisar los modelos instalados con:

   ```bash
   ollama ls
   ```

6. Consultar en Hugging Face la model card de al menos dos modelos.
7. Identificar fabricante, tipo de modelo, licencia, parámetros, idiomas y requerimientos.
8. Completar la tabla comparativa de seis modelos.
9. Escribir una reflexión breve sobre la experiencia.

---

## 19. Evidencias requeridas

El equipo debe entregar las siguientes evidencias:

1. Captura de instalación o verificación de Ollama.
2. Captura de `ollama --version`.
3. Captura de `ollama pull` para al menos tres modelos.
4. Captura de `ollama ls`.
5. Captura de ejecución de al menos tres modelos.
6. Captura de Hugging Face mostrando model card, licencia y archivos.
7. Tabla comparativa de seis modelos.
8. Reflexión final de 150 a 250 palabras.

> 🖼️ **Espacio para imagen sugerida:** collage de evidencias de terminal y navegador.  
> Archivo sugerido: `assets/img/llm/19-evidencias-actividad.png`

---

## 20. Preguntas de reflexión

Responder brevemente:

1. ¿Qué modelo fue más fácil de instalar y ejecutar?
2. ¿Qué modelo respondió mejor en español?
3. ¿Qué diferencia observaste entre un modelo pequeño y uno más grande?
4. ¿Qué importancia tiene la licencia del modelo?
5. ¿Por qué no debe usarse un LLM como única fuente académica?
6. ¿Qué ventajas y limitaciones tiene ejecutar modelos localmente?

---

## 21. Criterios de evaluación sugeridos

| Criterio | Ponderación |
|---|---:|
| Instalación y ejecución correcta de Ollama | 20% |
| Evidencias de terminal y navegador | 20% |
| Tabla comparativa completa y verificada | 30% |
| Análisis crítico de licencia, tamaño e idioma | 15% |
| Reflexión final clara y académica | 15% |

---

## 22. Consideraciones finales

1. **Verificar fuentes:** Las respuestas de un LLM deben contrastarse con documentación oficial, artículos académicos o fuentes institucionales.
2. **Revisar licencias:** No todos los modelos permiten los mismos usos. Antes de usar un modelo en investigación, docencia, producto o servicio, debe revisarse su licencia.
3. **Distinguir parámetros y tamaño en disco:** Un modelo de 7B parámetros no siempre ocupa lo mismo en todas sus versiones. La cuantización modifica el tamaño y el desempeño.
4. **Cuidar privacidad:** Ejecutar localmente puede reducir dependencia de servicios externos, pero no elimina todos los riesgos. No se deben usar datos sensibles sin una política clara de manejo de información.
5. **Evaluar idioma:** Un modelo puede ser multilingüe pero responder con distinta calidad según el idioma, el dominio técnico y el prompt.
6. **No confundir fluidez con verdad:** Un texto bien redactado puede ser incorrecto. La validación sigue siendo responsabilidad del usuario.

---

## Referencias

[1] Google for Developers, “Machine Learning Crash Course,” *Google Machine Learning Education*. [En línea]. Disponible en: https://developers.google.com/machine-learning/crash-course?hl=es-419

[2] Google for Developers, “Introducción a los modelos de lenguaje grandes,” *Machine Learning Crash Course*. [En línea]. Disponible en: https://developers.google.com/machine-learning/crash-course/llm?hl=es-419

[3] Google for Developers, “LLM: ¿Cuál es un modelo grande de lenguaje? Transformers y autoatención,” *Machine Learning Crash Course*. [En línea]. Disponible en: https://developers.google.com/machine-learning/crash-course/llm/transformers?hl=es-419

[4] Ollama, “CLI Reference,” *Ollama Documentation*. [En línea]. Disponible en: https://docs.ollama.com/cli

[5] Hugging Face, “Use Ollama with any GGUF Model on Hugging Face Hub,” *Hugging Face Docs*. [En línea]. Disponible en: https://huggingface.co/docs/hub/ollama

[6] Hugging Face, “Model Cards,” *Hugging Face Docs*. [En línea]. Disponible en: https://huggingface.co/docs/hub/en/model-cards

[7] Meta, “Llama-3.2-3B-Instruct,” *Hugging Face Model Card*. [En línea]. Disponible en: https://huggingface.co/meta-llama/Llama-3.2-3B-Instruct

[8] Google, “Gemma 3 4B IT,” *Hugging Face Model Card*. [En línea]. Disponible en: https://huggingface.co/google/gemma-3-4b-it

[9] Qwen, “Qwen2.5-7B-Instruct,” *Hugging Face Model Card*. [En línea]. Disponible en: https://huggingface.co/Qwen/Qwen2.5-7B-Instruct

[10] Mistral AI, “Mistral-7B-Instruct-v0.3,” *Hugging Face Model Card*. [En línea]. Disponible en: https://huggingface.co/mistralai/Mistral-7B-Instruct-v0.3

[11] Microsoft, “Phi-4-mini-instruct,” *Hugging Face Model Card*. [En línea]. Disponible en: https://huggingface.co/microsoft/Phi-4-mini-instruct

[12] TinyLlama, “TinyLlama-1.1B-Chat-v1.0,” *Hugging Face Model Card*. [En línea]. Disponible en: https://huggingface.co/TinyLlama/TinyLlama-1.1B-Chat-v1.0

[13] Ollama, “llama3.2,” *Ollama Library*. [En línea]. Disponible en: https://ollama.com/library/llama3.2

[14] Ollama, “gemma3:4b,” *Ollama Library*. [En línea]. Disponible en: https://ollama.com/library/gemma3:4b

[15] Ollama, “phi4-mini,” *Ollama Library*. [En línea]. Disponible en: https://ollama.com/library/phi4-mini

[16] Qwen, “Qwen2.5-7B-Instruct-GGUF,” *Hugging Face Model Card*. [En línea]. Disponible en: https://huggingface.co/Qwen/Qwen2.5-7B-Instruct-GGUF

---

## Siguiente sección

[Volver al inicio](index.md)

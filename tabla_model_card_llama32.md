# Tabla de revisión de modelos en Hugging Face

Al revisar un modelo en Hugging Face, no basta con observar el nombre del modelo. Es necesario leer su *model card*, revisar sus archivos, identificar su licencia y comprender si el modelo puede ejecutarse localmente o si requiere infraestructura especializada. La siguiente tabla muestra los elementos principales usando como ejemplo el modelo **Llama 3.2 3B Instruct**.

| Elemento | Pregunta guía | Ejemplo real: Llama 3.2 3B Instruct | ¿Cómo interpretarlo en clase? |
|---|---|---|---|
| Fabricante o desarrollador | ¿Quién creó el modelo? | **Meta**. En la model card aparece como *Model Developer: Meta*. | Permite identificar la institución, empresa o comunidad responsable del modelo. Esto es importante para evaluar confianza, documentación, soporte y condiciones de uso. |
| Nombre del modelo | ¿Cómo se identifica exactamente el modelo? | `meta-llama/Llama-3.2-3B-Instruct` en Hugging Face. En Ollama puede ejecutarse como `llama3.2:3b` o `llama3.2`, según la variante instalada. | El nombre exacto evita confundir versiones. No es lo mismo un modelo base, un modelo *instruct*, una versión cuantizada o una variante modificada por otra comunidad. |
| Tipo de modelo | ¿Es base, instruct, chat, embedding, multimodal o código? | Es un modelo **instruct** de generación de texto. Está optimizado para diálogo multilingüe, recuperación de información, resumen y tareas tipo asistente. | Un modelo *instruct* está ajustado para seguir instrucciones del usuario. Es más adecuado para clase y uso conversacional que un modelo base sin ajuste instruccional. |
| Arquitectura | ¿Qué arquitectura técnica utiliza? | Modelo de lenguaje **autoregresivo** basado en una arquitectura **transformer optimizada**. | Esto significa que genera texto prediciendo tokens de manera secuencial, usando mecanismos de atención para considerar el contexto. |
| Licencia | ¿Permite uso académico, comercial, redistribución o modificación? | Usa la **Llama 3.2 Community License**, una licencia propia de Meta. | No debe asumirse que todos los modelos de Hugging Face son “libres” o “open source” en el mismo sentido. La licencia debe leerse antes de usar el modelo en proyectos, productos o repositorios públicos. |
| Parámetros | ¿Cuántos parámetros tiene? | La versión 3B reporta aproximadamente **3.21 mil millones de parámetros**. | Los parámetros son valores internos aprendidos durante el entrenamiento. En general, más parámetros pueden implicar mayor capacidad, pero también mayor consumo de memoria y cómputo. |
| Tamaño de descarga | ¿Cuánto ocupa en disco la versión usada? | En Ollama, la variante `llama3.2:3b` aparece como modelo de aproximadamente **2 GB** en una versión cuantizada. En Hugging Face, el tamaño puede variar según los archivos y formato descargado. | El tamaño de descarga no siempre coincide con el número de parámetros. Una versión cuantizada ocupa menos espacio que una versión en precisión completa o BF16. Para la actividad, el estudiante debe registrar el tamaño real con `ollama ls`. |
| Idiomas | ¿Qué idiomas soporta oficialmente? | Soporta oficialmente **inglés, alemán, francés, italiano, portugués, hindi, español y tailandés**. | Que un modelo “pueda responder” en un idioma no significa que ese idioma esté oficialmente soportado. Para clase, es importante distinguir entre soporte declarado y desempeño observado. |
| Modalidad de entrada | ¿Qué tipo de datos recibe? | Texto multilingüe. | Este modelo es de entrada textual. No debe confundirse con modelos multimodales que aceptan imágenes, audio o video. |
| Modalidad de salida | ¿Qué tipo de resultado produce? | Texto y código. | Puede generar explicaciones, respuestas, resúmenes, instrucciones y fragmentos de código, pero no genera imágenes directamente. |
| Ventana de contexto | ¿Cuántos tokens puede procesar? | La versión text-only reporta una ventana de contexto de hasta **128k tokens**. | La ventana de contexto indica cuánta información puede considerar el modelo en una sola interacción. No equivale a memoria permanente ni garantiza razonamiento correcto sobre todo el texto. |
| Formato | ¿Está en Safetensors, GGUF u otro formato? | En Hugging Face aparece asociado con **Transformers**, **PyTorch** y **Safetensors**. En Ollama se usa una variante cuantizada lista para ejecución local. | El formato define con qué herramientas puede usarse. Safetensors suele utilizarse con bibliotecas como Transformers; GGUF o variantes cuantizadas suelen usarse para ejecución local eficiente. |
| Requerimientos técnicos | ¿Necesita GPU? ¿Puede ejecutarse cuantizado? | En Hugging Face puede usarse con `transformers`, `vLLM`, Docker u otros entornos. En Ollama, la versión cuantizada de aproximadamente 2 GB puede ejecutarse localmente con menor consumo de memoria. | Para una clase práctica conviene usar Ollama porque simplifica instalación y ejecución. Para uso avanzado con Hugging Face, una GPU mejora mucho el rendimiento. |
| Comando de prueba | ¿Cómo puedo ejecutarlo? | `ollama run llama3.2:3b` | El comando permite validar rápidamente que el modelo está instalado y responde desde la terminal. |
| Caso de uso recomendado | ¿Para qué tareas fue diseñado? | Asistentes conversacionales, recuperación de conocimiento, resumen, reescritura de prompts y aplicaciones de lenguaje. | Ayuda a seleccionar el modelo correcto. No todos los modelos sirven para lo mismo: algunos son para texto, otros para código, embeddings, visión o clasificación. |
| Limitaciones | ¿Reporta sesgos, restricciones, riesgos o alucinaciones? | La model card advierte que, como otros LLM, puede producir respuestas inexactas, sesgadas u objetables, y recomienda realizar pruebas de seguridad según la aplicación. | El estudiante debe entender que una respuesta convincente no siempre es correcta. Todo uso académico o profesional requiere verificación, especialmente si se trabaja con información técnica, legal, médica o sensible. |
| Acceso | ¿Está disponible directamente o requiere aceptar condiciones? | En Hugging Face puede requerir aceptar condiciones de acceso y compartir información de contacto. | Algunos modelos no se descargan automáticamente desde Hugging Face hasta aceptar su licencia o condiciones. Esto debe explicarse para evitar confusión durante la práctica. |

> **Nota:** el número de parámetros, el tamaño de descarga y los requerimientos técnicos no son lo mismo. Un modelo puede tener 3B parámetros, pero ocupar diferentes cantidades de espacio según el formato y la cuantización. Por eso, en la actividad práctica se debe registrar el tamaño real del modelo instalado usando el comando:
>
> ```bash
> ollama ls
> ```

## Espacio sugerido para captura

> **Imagen sugerida:** captura de la página del modelo en Hugging Face, resaltando el nombre del modelo, desarrollador, licencia, parámetros, idiomas y formato.
>
> Ruta sugerida:
>
> ```markdown
> ![Página de Hugging Face de Llama 3.2 3B Instruct](assets/img/llm/huggingface-llama32-3b-model-card.png)
> ```

> **Imagen sugerida:** captura de terminal después de ejecutar `ollama ls`, donde se observe el nombre del modelo y el tamaño descargado.
>
> Ruta sugerida:
>
> ```markdown
> ![Modelos instalados en Ollama](assets/img/llm/ollama-ls-llama32.png)
> ```

## Referencias

[1] Meta. *Llama 3.2 3B Instruct Model Card*. Hugging Face. Disponible en: https://huggingface.co/meta-llama/Llama-3.2-3B-Instruct

[2] Ollama. *llama3.2*. Ollama Library. Disponible en: https://ollama.com/library/llama3.2

[3] Hugging Face. *Model Cards*. Hugging Face Hub Documentation. Disponible en: https://huggingface.co/docs/hub/en/model-cards

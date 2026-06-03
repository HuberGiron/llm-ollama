document.addEventListener("DOMContentLoaded", function () {
  const codeBlocks = document.querySelectorAll("div.highlighter-rouge, figure.highlight");

  const terminalLanguages = [
    "bash",
    "shell",
    "sh",
    "zsh",
    "console",
    "terminal",
    "powershell",
    "ps1"
  ];

  const textLanguages = [
    "text",
    "plaintext",
    "txt"
  ];

  const collapsibleLanguages = [
    "python",
    "javascript",
    "js",
    "json",
    "yaml",
    "yml",
    "html",
    "css"
  ];

  const MAX_LINES_BEFORE_COLLAPSE = 18;

  codeBlocks.forEach((block, index) => {
    if (block.dataset.enhanced === "true") return;

    const pre = block.querySelector("pre");
    const code = block.querySelector("code");

    if (!pre || !code) return;

    const language = detectLanguage(block, code);
    const codeText = code.innerText || code.textContent || "";
    const lineCount = codeText.split("\n").length;

    /*
      Bloques tipo text/plaintext:
      - Fondo negro
      - Sin etiqueta
      - Sin botones
      - Sin descargar
      - Sin copiar
    */
    if (textLanguages.includes(language)) {
      block.classList.add("code-text-box");
      block.dataset.enhanced = "true";
      return;
    }

    const wrapper = document.createElement("div");
    wrapper.className = "code-enhanced";
    wrapper.dataset.enhanced = "true";

    const isTerminal = terminalLanguages.includes(language);
    const shouldCollapse =
      lineCount > MAX_LINES_BEFORE_COLLAPSE ||
      collapsibleLanguages.includes(language);

    if (isTerminal) {
      wrapper.classList.add("is-terminal");
    }

    if (shouldCollapse) {
      wrapper.classList.add("is-collapsible");
      wrapper.classList.remove("is-open");
    }

    const toolbar = document.createElement("div");
    toolbar.className = "code-enhanced__toolbar";

    const label = document.createElement("span");
    label.className = "code-enhanced__label";
    label.textContent = buildLabel(language, isTerminal);

    const actions = document.createElement("div");
    actions.className = "code-enhanced__actions";

    const copyButton = document.createElement("button");
    copyButton.className = "code-enhanced__button";
    copyButton.type = "button";
    copyButton.textContent = "Copiar";
    copyButton.addEventListener("click", async () => {
      try {
        await navigator.clipboard.writeText(codeText);
        copyButton.textContent = "Copiado";
        setTimeout(() => {
          copyButton.textContent = "Copiar";
        }, 1500);
      } catch (error) {
        fallbackCopy(codeText);
        copyButton.textContent = "Copiado";
        setTimeout(() => {
          copyButton.textContent = "Copiar";
        }, 1500);
      }
    });

    const downloadButton = document.createElement("button");
    downloadButton.className = "code-enhanced__button";
    downloadButton.type = "button";
    downloadButton.textContent = "Descargar";
    downloadButton.addEventListener("click", () => {
      const filename =
        getConfiguredFilename(block) ||
        `codigo_${String(index + 1).padStart(2, "0")}.${extensionForLanguage(language)}`;

      downloadTextFile(filename, codeText);
    });

    actions.appendChild(copyButton);
    actions.appendChild(downloadButton);

    if (shouldCollapse) {
      const toggleButton = document.createElement("button");
      toggleButton.className = "code-enhanced__button";
      toggleButton.type = "button";
      toggleButton.textContent = "Mostrar";
      toggleButton.addEventListener("click", () => {
        const isOpen = wrapper.classList.toggle("is-open");
        toggleButton.textContent = isOpen ? "Ocultar" : "Mostrar";
      });

      actions.prepend(toggleButton);
    }

    toolbar.appendChild(label);
    toolbar.appendChild(actions);

    const collapsedNote = document.createElement("div");
    collapsedNote.className = "code-enhanced__collapsed-note";
    collapsedNote.textContent = "Bloque de código replegado. Usa “Mostrar” para verlo completo.";

    block.parentNode.insertBefore(wrapper, block);
    wrapper.appendChild(toolbar);
    wrapper.appendChild(collapsedNote);
    wrapper.appendChild(block);

    block.dataset.enhanced = "true";
  });
});


function detectLanguage(block, code) {
  const classSources = [
    block.className || "",
    code.className || "",
    block.parentElement ? block.parentElement.className || "" : ""
  ].join(" ");

  const match = classSources.match(/language-([a-zA-Z0-9_+-]+)/);

  if (match && match[1]) {
    return match[1].toLowerCase();
  }

  return "text";
}


function buildLabel(language, isTerminal) {
  const readable = {
    bash: "Bash",
    shell: "Bash",
    sh: "Bash",
    zsh: "Bash",
    console: "Bash",
    terminal: "Bash",
    powershell: "PowerShell",
    ps1: "PowerShell",
    python: "Python",
    json: "JSON",
    yaml: "YAML",
    yml: "YAML",
    html: "HTML",
    css: "CSS",
    javascript: "JavaScript",
    js: "JavaScript"
  };

  if (isTerminal) {
    return "Bash";
  }

  return readable[language] || language.toUpperCase();
}


function extensionForLanguage(language) {
  const extensions = {
    bash: "sh",
    shell: "sh",
    sh: "sh",
    zsh: "sh",
    console: "sh",
    terminal: "sh",
    powershell: "ps1",
    ps1: "ps1",
    python: "py",
    javascript: "js",
    js: "js",
    json: "json",
    yaml: "yml",
    yml: "yml",
    html: "html",
    css: "css"
  };

  return extensions[language] || "txt";
}


/*
  Nombre de archivo personalizado para descarga.

  Opción recomendada en Markdown:

  <!-- code-file: benchmark_modelos.py -->
  ```python
  ...
  ```

  También acepta:
  <!-- filename: benchmark_modelos.py -->
  <!-- file: benchmark_modelos.py -->

  Nota:
  El comentario HTML debe estar justo antes del bloque de código.
*/
function getConfiguredFilename(block) {
  const fromParent = findFilenameInParents(block);
  if (fromParent) return sanitizeFilename(fromParent);

  let node = block.previousSibling;
  let safetyCounter = 0;

  while (node && safetyCounter < 6) {
    safetyCounter += 1;

    if (node.nodeType === Node.COMMENT_NODE) {
      const match = node.nodeValue.match(/(?:code-file|filename|file)\s*:\s*([^\n\r]+)/i);
      if (match && match[1]) {
        return sanitizeFilename(match[1].trim());
      }
    }

    if (node.nodeType === Node.TEXT_NODE && node.textContent.trim() === "") {
      node = node.previousSibling;
      continue;
    }

    break;
  }

  return null;
}


function findFilenameInParents(block) {
  let node = block.parentElement;

  while (node && node !== document.body) {
    if (node.dataset && node.dataset.codeFile) return node.dataset.codeFile;
    if (node.dataset && node.dataset.filename) return node.dataset.filename;
    node = node.parentElement;
  }

  return null;
}


function sanitizeFilename(filename) {
  return filename
    .replace(/[\\/:*?"<>|]/g, "_")
    .replace(/\s+/g, "_")
    .trim();
}


function downloadTextFile(filename, text) {
  const blob = new Blob([text], { type: "text/plain;charset=utf-8" });
  const url = URL.createObjectURL(blob);

  const link = document.createElement("a");
  link.href = url;
  link.download = filename;

  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);

  URL.revokeObjectURL(url);
}


function fallbackCopy(text) {
  const textarea = document.createElement("textarea");
  textarea.value = text;
  textarea.setAttribute("readonly", "");
  textarea.style.position = "absolute";
  textarea.style.left = "-9999px";

  document.body.appendChild(textarea);
  textarea.select();
  document.execCommand("copy");
  document.body.removeChild(textarea);
}

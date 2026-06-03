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

  const textLanguages = [
    "text",
    "plaintext",
    "txt"
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
    const directives = readDirectives(block);

    /* Los bloques text/plaintext son cajas simples:
       no toolbar, no copiar, no descargar, no plegado. */
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
      directives.open !== true &&
      (
        lineCount > MAX_LINES_BEFORE_COLLAPSE ||
        collapsibleLanguages.includes(language)
      );

    if (isTerminal) {
      wrapper.classList.add("is-terminal");
    }

    if (shouldCollapse) {
      wrapper.classList.add("is-collapsible");
      wrapper.classList.remove("is-open");
    } else if (directives.open === true) {
      wrapper.classList.add("is-open");
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

    actions.appendChild(copyButton);

    /* Descarga:
       - Terminal: sin botón descargar por default.
       - Código: descarga activada por default.
       - Cualquier bloque: se puede desactivar con:
         <!-- code-download: false -->
         <!-- no-download -->
    */
    const allowDownload =
      !isTerminal &&
      directives.download !== false;

    if (allowDownload) {
      const downloadButton = document.createElement("button");
      downloadButton.className = "code-enhanced__button";
      downloadButton.type = "button";
      downloadButton.textContent = "Descargar";
      downloadButton.addEventListener("click", () => {
        const extension = extensionForLanguage(language);
        const filename =
          directives.filename ||
          `codigo_${String(index + 1).padStart(2, "0")}.${extension}`;

        downloadTextFile(filename, codeText);
      });

      actions.appendChild(downloadButton);
    }

    if (shouldCollapse || directives.open === true) {
      const toggleButton = document.createElement("button");
      toggleButton.className = "code-enhanced__button";
      toggleButton.type = "button";
      toggleButton.textContent = wrapper.classList.contains("is-open") ? "Ocultar" : "Mostrar";
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
  if (isTerminal) {
    return "Bash";
  }

  const readable = {
    python: "Python",
    json: "JSON",
    yaml: "YAML",
    yml: "YAML",
    html: "HTML",
    css: "CSS",
    javascript: "JavaScript",
    js: "JavaScript"
  };

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
    css: "css",
    text: "txt",
    plaintext: "txt",
    txt: "txt"
  };

  return extensions[language] || "txt";
}


function readDirectives(block) {
  const directives = {
    filename: null,
    open: false,
    download: true
  };

  let node = block.previousSibling;
  let scanned = 0;

  while (node && scanned < 8) {
    scanned += 1;

    if (node.nodeType === Node.TEXT_NODE && node.textContent.trim() === "") {
      node = node.previousSibling;
      continue;
    }

    if (node.nodeType === Node.COMMENT_NODE) {
      const text = node.textContent.trim();

      const fileMatch = text.match(/(?:code-file|filename|file)\s*:\s*([^\n\r]+)/i);
      if (fileMatch && fileMatch[1]) {
        directives.filename = sanitizeFilename(fileMatch[1].trim());
      }

      const openMatch = text.match(/code-open\s*:\s*(true|false)/i);
      if (openMatch && openMatch[1]) {
        directives.open = openMatch[1].toLowerCase() === "true";
      }

      const downloadMatch = text.match(/code-download\s*:\s*(true|false)/i);
      if (downloadMatch && downloadMatch[1]) {
        directives.download = downloadMatch[1].toLowerCase() === "true";
      }

      if (/no-download/i.test(text)) {
        directives.download = false;
      }

      node = node.previousSibling;
      continue;
    }

    break;
  }

  return directives;
}


function sanitizeFilename(filename) {
  return filename
    .replace(/[<>:"/\\|?*\x00-\x1F]/g, "_")
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

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

  const MAX_LINES_BEFORE_COLLAPSE = 18;

  codeBlocks.forEach((block, index) => {
    if (block.dataset.enhanced === "true") return;

    const pre = block.querySelector("pre");
    const code = block.querySelector("code");

    if (!pre || !code) return;

    const language = detectLanguage(block, code);
    const codeText = code.innerText || code.textContent || "";
    const lineCount = codeText.split("\n").length;

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
    label.textContent = buildLabel(language, lineCount, isTerminal);

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
      const extension = extensionForLanguage(language);
      const filename = `codigo_${String(index + 1).padStart(2, "0")}.${extension}`;
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
    collapsedNote.textContent = `Bloque de código replegado (${lineCount} líneas). Usa “Mostrar” para verlo completo.`;

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


function buildLabel(language, lineCount, isTerminal) {
  const readable = {
    bash: "Terminal / Bash",
    shell: "Terminal / Shell",
    sh: "Terminal / sh",
    zsh: "Terminal / zsh",
    console: "Terminal",
    terminal: "Terminal",
    powershell: "PowerShell",
    ps1: "PowerShell",
    python: "Python",
    json: "JSON",
    yaml: "YAML",
    yml: "YAML",
    html: "HTML",
    css: "CSS",
    javascript: "JavaScript",
    js: "JavaScript",
    text: "Texto"
  };

  const name = readable[language] || language.toUpperCase();

  if (isTerminal) {
    return `💻 ${name} · ${lineCount} líneas`;
  }

  return `Código · ${name} · ${lineCount} líneas`;
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
    text: "txt"
  };

  return extensions[language] || "txt";
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
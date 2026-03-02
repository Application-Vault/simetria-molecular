/******************************/
/* ENDPOINTS BACKEND          */
/******************************/

const baseUrlAnalise = 'https://x8clyvj53d.execute-api.us-east-2.amazonaws.com/api/analise';
const baseUrlGrupos = 'https://x8clyvj53d.execute-api.us-east-2.amazonaws.com/api/grupo/';
const baseUrlMoleculas = 'https://x8clyvj53d.execute-api.us-east-2.amazonaws.com/api/molecula/';

/******************************/
/* STATE + UTIL               */
/******************************/

let __pdfObjectUrl = null;

function revokePdfUrl() {
  if (__pdfObjectUrl) {
    URL.revokeObjectURL(__pdfObjectUrl);
    __pdfObjectUrl = null;
  }
}

function $(id) {
  return document.getElementById(id);
}

function safeValue(id, fallback = "") {
  return $(id)?.value ?? fallback;
}

function selectedValue(selector, fallback = null) {
  return document.querySelector(selector)?.value ?? fallback;
}

function setDisabled(el, disabled) {
  if (!el) return;
  el.disabled = !!disabled;
  el.style.opacity = disabled ? "0.65" : "1";
  el.style.cursor = disabled ? "not-allowed" : "pointer";
}

function showError(msg) {
  alert("Erro na análise: " + msg);
}

function showStatus(msg) {
  const el = $("status");
  if (!el) return;
  el.textContent = msg;
  el.style.display = msg ? "block" : "none";
}

function ensureTextAreaResultado() {
  // ✅ você quer TEX em resultado. Então #resultado precisa ser textarea
  // se não existir, cria (fallback).
  let el = $("resultado");
  if (el) return el;

  el = document.createElement("textarea");
  el.id = "resultado";
  el.rows = 12;
  el.style.width = "100%";
  el.style.marginTop = "16px";
  document.body.appendChild(el);
  return el;
}

function clearPdfUi() {
  // se você tiver um botão/link/placeholder, limpa aqui.
  const pdfBtn = $("abrirPdf");
  if (pdfBtn) pdfBtn.style.display = "none";
  revokePdfUrl();
}

/******************************/
/* SELECT MOLECULA            */
/******************************/

const moleculaSelect = $("moleculaSelect");
const moleculaOutput = $("moleculaOutput");

moleculaSelect?.addEventListener("change", async () => {
  const moleculaSelecionada = moleculaSelect.value;

  if (!moleculaOutput) return;

  if (moleculaSelecionada === "outro") {
    moleculaOutput.readOnly = false;
    moleculaOutput.value = "";
    return;
  }

  if (!moleculaSelecionada) {
    moleculaOutput.value = "";
    moleculaOutput.readOnly = true;
    return;
  }

  try {
    showStatus("Carregando molécula...");
    const resp = await fetch(baseUrlMoleculas + moleculaSelecionada);
    if (!resp.ok) throw new Error("Erro ao carregar o XYZ");
    const xyz = await resp.text();
    moleculaOutput.value = xyz;
    moleculaOutput.readOnly = true;
    showStatus("");
  } catch (e) {
    moleculaOutput.value = String(e?.message ?? e);
    showStatus("");
  }
});

/******************************/
/* TROCA ENTRE TEXTO/GRÁFICO  */
/******************************/

function trocarRender() {
  const tipo = selectedValue('input[name="renderTipo"]:checked', "texto");
  const divTexto = $("render-texto");
  const divGrafico = $("render-grafico");

  if (!divTexto || !divGrafico) return;

  if (tipo === "texto") {
    divTexto.style.display = "block";
    divGrafico.style.display = "none";
  } else {
    divTexto.style.display = "none";
    divGrafico.style.display = "block";
  }

  // quando troca, limpa PDF anterior e mantém TEX
  clearPdfUi();
}

document.addEventListener("DOMContentLoaded", () => {
  trocarRender();

  // se seus radios tiverem onchange, isso garante
  document.querySelectorAll('input[name="renderTipo"]').forEach(r => {
    r.addEventListener("change", trocarRender);
  });
});

/******************************/
/* BOTÃO ANÁLISE              */
/******************************/

const analiseBtn = $("botaoAnalise");

// (opcional) botão/link para abrir pdf em outra aba
// crie um elemento no HTML com id="abrirPdf" (button ou a). Se não existir, a gente cria.
function ensureAbrirPdfButton() {
  let btn = $("abrirPdf");
  if (btn) return btn;

  btn = document.createElement("button");
  btn.id = "abrirPdf";
  btn.textContent = "📝 Abrir PDF em outra aba";
  btn.type = "button";
  btn.className = "btn";
  btn.style.display = "none";

  // NOVO: ancora no slot do HTML
  const slot = $("pdfSlot");
  if (slot) {
    slot.appendChild(btn);
  } else {
    // fallback antigo
    const after = ensureTextAreaResultado();
    after.insertAdjacentElement("afterend", btn);
  }
  return btn;
}

function openPdfInNewTab(url) {
  // abre em outra aba
  window.open(url, "_blank", "noopener,noreferrer");
}

analiseBtn?.addEventListener("click", async () => {
  const tipo = selectedValue('input[name="renderTipo"]:checked', "texto");
  const formatoTexto = selectedValue('input[name="formatoTexto"]:checked', "tex"); // "tex" ou "pdf"
  const formatoGrafico = selectedValue('input[name="formatoGrafico"]:checked', "3d");
  const paleta = selectedValue('input[name="paletaCores"]:checked', "PASTEL");

  // TEX sempre aparece em resultado: então só vamos mandar pdf quando user escolher pdf
  const querPdf = (tipo === "texto" && String(formatoTexto).toLowerCase() === "pdf");

  // monta FormData
  const formData = new FormData();

  const moleculaText = safeValue("moleculaOutput", "");
  const moleculaBlob = new Blob([moleculaText], { type: "text/plain" });
  formData.append("molecula", moleculaBlob, "molecula.xyz");

  // analises (checkboxes)
  const analises = {};
  if (tipo === "texto") {
    document.querySelectorAll('input[name="analises"]:checked').forEach(input => {
      analises[input.value] = true;
    });
  }

  const payload = {
    render: {
      tipo,
      formato: tipo === "grafico" ? formatoGrafico : (querPdf ? "pdf" : "tex"),
      paleta: tipo === "grafico" ? paleta : null,
    },
    analises
  };

  formData.append("payload", JSON.stringify(payload));

  // UI
  setDisabled(analiseBtn, true);
  showStatus("Processando...");
  clearPdfUi();

  try {
    const response = await fetch(baseUrlAnalise, {
      method: "POST",
      body: formData
    });

    // backend novo: JSON sempre
    const raw = await response.text();
    if (!response.ok) {
      throw new Error(raw || "Erro na requisição");
    }

    let data;
    try {
      data = JSON.parse(raw);
    } catch {
      throw new Error("Resposta do backend não é JSON. Atualize o backend para retornar { tex, pdf_base64? }.");
    }

    // TEX → sempre no Resultado (textarea)
    const resultadoEl = ensureTextAreaResultado();
    resultadoEl.value = data?.tex ?? "";

    // PDF → se veio, abre em outra aba (e opcionalmente mostra botão)
    if (data?.pdf_base64) {
      const bytes = Uint8Array.from(atob(data.pdf_base64), c => c.charCodeAt(0));
      const blob = new Blob([bytes], { type: "application/pdf" });

      revokePdfUrl();
      __pdfObjectUrl = URL.createObjectURL(blob);

      // abre direto em nova aba
      openPdfInNewTab(__pdfObjectUrl);

      // e também mostra botão caso pop-up bloqueie
      const btn = ensureAbrirPdfButton();
      btn.style.display = "inline-block";
      btn.onclick = () => openPdfInNewTab(__pdfObjectUrl);
    }

    showStatus("");

  } catch (err) {
    showStatus("");
    showError(err?.message ?? String(err));
  } finally {
    setDisabled(analiseBtn, false);
  }
});
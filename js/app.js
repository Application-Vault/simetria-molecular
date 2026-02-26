/******************************/
/* ENDPOINTS BACKEND          */
/******************************/

// const baseUrlAnalise = 'https://naraavila-simetria-molecular.hf.space/api/analise'
// const baseUrlGrupos = 'https://naraavila-simetria-molecular.hf.space/api/grupo/';
// const baseUrlMoleculas = 'https://naraavila-simetria-molecular.hf.space/api/molecula/';

// const baseUrlAnalise = 'http://localhost:8000/api/analise'
// const baseUrlGrupos = 'http://localhost:8000/api/grupo/';
// const baseUrlMoleculas = 'http://localhost:8000/api/molecula/';

const baseUrlAnalise = 'https://x8clyvj53d.execute-api.us-east-2.amazonaws.com/api/analise';
const baseUrlGrupos = 'https://x8clyvj53d.execute-api.us-east-2.amazonaws.com/api/grupo/';
const baseUrlMoleculas = 'https://x8clyvj53d.execute-api.us-east-2.amazonaws.com/api/molecula/';

/******************************/
/* UTILIDADES RESULTADO       */
/******************************/

let __resultadoObjectUrl = null;

function getResultadoEl() {
  let el = document.getElementById("resultado");
  if (el) return el;

  // fallback automático se não existir no HTML
  el = document.createElement("div");
  el.id = "resultado";
  el.style.marginTop = "20px";
  document.body.appendChild(el);
  return el;
}

function cleanupResultadoUrl() {
  if (__resultadoObjectUrl) {
    URL.revokeObjectURL(__resultadoObjectUrl);
    __resultadoObjectUrl = null;
  }
}

function getFilenameFromDisposition(disposition, fallback) {
  if (!disposition) return fallback;

  const m1 = disposition.match(/filename\*\s*=\s*UTF-8''([^;]+)/i);
  if (m1 && m1[1]) return decodeURIComponent(m1[1]);

  const m2 = disposition.match(/filename\s*=\s*"([^"]+)"/i);
  if (m2 && m2[1]) return m2[1];

  const m3 = disposition.match(/filename\s*=\s*([^;]+)/i);
  if (m3 && m3[1]) return m3[1].trim();

  return fallback;
}

/******************************/
/* SELECT MOLECULA            */
/******************************/

const moleculaSelect = document.getElementById("moleculaSelect");
const moleculaOutput = document.getElementById("moleculaOutput");

moleculaSelect?.addEventListener('change', () => {

  const moleculaSelecionada = moleculaSelect.value;

  if (moleculaSelecionada === 'outro') {
    moleculaOutput.readOnly = false;
    moleculaOutput.value = "";
    return;
  }

  if (!moleculaSelecionada) {
    moleculaOutput.value = "";
    return;
  }

  fetch(baseUrlMoleculas + moleculaSelecionada)
    .then(response => response.ok ? response.text() : Promise.reject("Erro ao carregar o XYZ"))
    .then(data => {
      moleculaOutput.value = data;
      moleculaOutput.readOnly = true;
    })
    .catch(err => {
      moleculaOutput.value = err;
    });
});

/******************************/
/* BOTÃO ANÁLISE              */
/******************************/

const analiseBtn = document.getElementById("botaoAnalise");

analiseBtn?.addEventListener("click", async () => {

  const tipo = document.querySelector('input[name="renderTipo"]:checked')?.value;

  const formData = new FormData();

  const moleculaText = document.getElementById("moleculaOutput")?.value ?? "";
  const moleculaBlob = new Blob([moleculaText], { type: "text/plain" });
  formData.append("molecula", moleculaBlob, "molecula.xyz");

  let paleta = null;
  let analises = {};
  let formato = null;

  if (tipo === "grafico") {
    paleta = document.querySelector('input[name="paletaCores"]:checked')?.value ?? "PASTEL";
    formato = document.querySelector('input[name="formatoGrafico"]:checked')?.value ?? "3d";
  } else {
    formato = document.querySelector('input[name="formatoTexto"]:checked')?.value ?? "tex";
    document.querySelectorAll('input[name="analises"]:checked').forEach(input => {
      analises[input.value] = true;
    });
  }

  const payload = {
    render: {
      tipo,
      formato,
      paleta
    },
    analises
  };

  formData.append("payload", JSON.stringify(payload));

  try {
    const response = await fetch(baseUrlAnalise, {
      method: "POST",
      body: formData
    });

    const contentType = response.headers.get("Content-Type") || "";
    const disposition = response.headers.get("Content-Disposition") || "";

    if (!response.ok) {
      const text = await response.text();
      throw new Error(text || "Erro na requisição");
    }

    const blob = await response.blob();
    const isPdf = contentType.includes("application/pdf");

    cleanupResultadoUrl();

    if (isPdf) {
      // PDF → EXIBE
      __resultadoObjectUrl = URL.createObjectURL(blob);

      const el = getResultadoEl();
      el.innerHTML = `
        <iframe 
          src="${__resultadoObjectUrl}" 
          style="width:100%; height:80vh; border:1px solid #444; border-radius:8px;">
        </iframe>
      `;
    } else {
      // TEX → BAIXA
      __resultadoObjectUrl = URL.createObjectURL(blob);

      const filename = getFilenameFromDisposition(disposition, "resultado.tex");

      const a = document.createElement("a");
      a.href = __resultadoObjectUrl;
      a.download = filename;
      document.body.appendChild(a);
      a.click();
      a.remove();

      setTimeout(cleanupResultadoUrl, 2000);
    }

  } catch (err) {
    alert("Erro na análise: " + err.message);
  }
});

/******************************/
/* TROCA ENTRE TEXTO/GRÁFICO */
/******************************/

function trocarRender() {
  const tipo = document.querySelector('input[name="renderTipo"]:checked')?.value;

  const divTexto = document.getElementById("render-texto");
  const divGrafico = document.getElementById("render-grafico");

  if (!divTexto || !divGrafico) return;

  if (tipo === "texto") {
    divTexto.style.display = "block";
    divGrafico.style.display = "none";
  } else {
    divTexto.style.display = "none";
    divGrafico.style.display = "block";
  }
}

document.addEventListener("DOMContentLoaded", trocarRender);
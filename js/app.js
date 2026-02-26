/******************************/
/* ENDPOINTS BACKEND          */
/******************************/

// const baseUrlAnalise = 'https://naraavila-simetria-molecular.hf.space/api/analise'
// const baseUrlGrupos = 'https://naraavila-simetria-molecular.hf.space/api/grupo/';
// const baseUrlMoleculas = 'https://naraavila-simetria-molecular.hf.space/api/molecula/';

const baseUrlAnalise = 'https://x8clyvj53d.execute-api.us-east-2.amazonaws.com/api/analise'
const baseUrlGrupos = 'https://x8clyvj53d.execute-api.us-east-2.amazonaws.com/api/grupo/';
const baseUrlMoleculas = 'https://x8clyvj53d.execute-api.us-east-2.amazonaws.com/api/molecula/';


// const baseUrlAnalise = 'http://localhost:8000/api/analise'
// const baseUrlGrupos = 'http://localhost:8000/api/grupo/';
// const baseUrlMoleculas = 'http://localhost:8000/api/molecula/';

/******************************/
/* AÇÃO SELECT MOLECULE*/
/******************************/
moleculaSelect.addEventListener('change', () => {
  const moleculaSelecionada = moleculaSelect.value;
  if (moleculaSelecionada === 'outro') {
    moleculaOutput.readOnly = false;
    moleculaOutput.value = "";
  } else {
    if (moleculaSelecionada) {
      fetch(baseUrlMoleculas + moleculaSelecionada)
        .then(response => response.ok ? response.text() : Promise.reject('Erro ao carregar o XYZ'))
        .then(data => moleculaOutput.value = data)
        .catch(err => moleculaOutput.value = err);
      moleculaOutput.readOnly = true;
    } else {
      moleculaOutput.value = '';
    }
  }
});

/******************************/
/* AÇÃO BOTÃO ANÁLISE SIMETRIA*/
/******************************/
const analiseBtn = document.getElementById("botaoAnalise");

analiseBtn.addEventListener("click", async () => {

  const tipo = document.querySelector('input[name="renderTipo"]:checked')?.value;

  const formData = new FormData();

  // Captura da molécula (sempre necessária)
  const moleculaText = document.getElementById("moleculaOutput")?.value ?? "";
  const moleculaBlob = new Blob([moleculaText], { type: "text/plain" });
  formData.append("molecula", moleculaBlob, "molecula.xyz");

  let paleta = null;
  const analises = {};
  let formato = null;


  // Apenas se renderização for gráfica
  if (tipo === "grafico") {
    paleta = document.querySelector('input[name="paletaCores"]:checked')?.value ?? "PASTEL";
    formato = document.querySelector('input[name="formatoGrafico"]:checked')?.value ?? "3d";
  }
  else {
    formato = document.querySelector(`input[name="formatoTexto"]:checked`)?.value ?? "";
    document.querySelectorAll('input[name="analises"]:checked').forEach(input => {
      analises[input.value] = true;
    });
  }

  try {
    const payload = {
      render: {
        tipo,
        formato,
        paleta
      },
      analises
    };

    formData.append("payload", JSON.stringify(payload));

    const response = await fetch(baseUrlAnalise, {
      method: "POST",
      body: formData
    });

    const contentType = response.headers.get("Content-Type") || "";

    if (!response.ok) {
      const text = await response.text();
      throw new Error(text || "Erro na requisição");
    }

    const blob = await response.blob();

    if (contentType.includes("application/pdf")) {
      // PDF → EXIBE
      const url = URL.createObjectURL(blob);

      document.getElementById("resultado").innerHTML = `
    <iframe 
      src="${url}" 
      style="width:100%; height:80vh; border:1px solid #444; border-radius:8px;">
    </iframe>
  `;

    } else {
      // TEX → BAIXA
      const url = URL.createObjectURL(blob);

      const a = document.createElement("a");
      a.href = url;
      a.download = "resultado.tex";
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
    }
  } catch (err) {
    alert("Erro na análise: " + err.message);
  }
});

function trocarRender() {
  const tipo = document.querySelector('input[name="renderTipo"]:checked').value;
  const divTexto = document.getElementById("render-texto");
  const divGrafico = document.getElementById("render-grafico");

  if (tipo === "texto") {
    divTexto.style.display = "block";
    divGrafico.style.display = "none";
  } else {
    divTexto.style.display = "none";
    divGrafico.style.display = "block";
  }
}

// Executa na inicialização da página
document.addEventListener("DOMContentLoaded", trocarRender);
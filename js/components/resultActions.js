import { API_CONFIG } from '../config.js';
import { $, showInfo } from '../utils/dom.js';

export function initResultActions() {
  const btnCopiarTex = $('btnCopiarTex');
  const btnGerarPdf = $('btnGerarPdf');
  const resultadoEl = $('resultado');

  if (btnCopiarTex) {
    btnCopiarTex.addEventListener('click', async () => {
      const tex = resultadoEl?.value || '';
      if (!tex.trim()) {
        alert('Ainda não há conteúdo TeX para copiar.');
        return;
      }

      try {
        await navigator.clipboard.writeText(tex);
        btnCopiarTex.innerHTML = '<i class="fa-solid fa-check"></i> Copiado';
        setTimeout(() => {
          btnCopiarTex.innerHTML = '<i class="fa-regular fa-copy"></i> Copiar';
        }, 1400);
      } catch (error) {
        alert('Não foi possível copiar o conteúdo.');
        console.error(error);
      }
    });
  }

  if (btnGerarPdf) {
    btnGerarPdf.addEventListener("click", async () => {
      const tex = resultadoEl?.value || "";

      if (!tex.trim()) {
        alert("Ainda não há conteúdo TeX para enviar.");
        return;
      }

      const newTab = window.open("", "_blank");

      try {
        btnGerarPdf.disabled = true;
        btnGerarPdf.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Gerando...';

        const response = await fetch(API_CONFIG.baseUrlPdf, {
          method: "POST",
          headers: {
            "Content-Type": "application/json"
          },
          body: JSON.stringify({ tex })
        });

        if (!response.ok) {
          const msg = await response.text();
          throw new Error(msg || "Falha ao gerar PDF.");
        }

        const data = await response.json();

        if (!data?.pdf_base64) {
          throw new Error("Resposta sem pdf_base64.");
        }

        const binary = atob(data.pdf_base64);
        const bytes = new Uint8Array(binary.length);

        for (let i = 0; i < binary.length; i++) {
          bytes[i] = binary.charCodeAt(i);
        }

        const blob = new Blob([bytes], { type: "application/pdf" });
        const pdfUrl = URL.createObjectURL(blob);

        if (newTab) {
          newTab.location.href = pdfUrl;
        } else {
          window.open(pdfUrl, "_blank", "noopener,noreferrer");
        }

        setTimeout(() => URL.revokeObjectURL(pdfUrl), 60000);

      } catch (err) {
        console.error(err);
        if (newTab) newTab.close();
        alert("Erro ao gerar PDF: " + err.message);
      } finally {
        btnGerarPdf.disabled = false;
        btnGerarPdf.innerHTML = '<i class="fa-regular fa-file-pdf"></i> Gerar PDF';
      }
    });
  }
}

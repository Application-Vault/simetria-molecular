import { API_CONFIG } from '../config.js';
import { $, safeValue, selectedValue, setDisabled, showError, showStatus, ensureTextAreaResultado } from '../utils/dom.js';
import { clearUi, ensureAbrirPdfButton, openPdfInNewTab, setPdfObjectUrl } from '../services/pdfState.js';

export function initAnalysis() {
  const analiseBtn = $('botaoAnalise');
  if (!analiseBtn) return;

  analiseBtn.addEventListener('click', async () => {
    const tipo = selectedValue('input[name="renderTipo"]:checked', 'texto');
    const formatoTexto = selectedValue('input[name="formatoTexto"]:checked', 'tex');
    const formatoGrafico = selectedValue('input[name="formatoGrafico"]:checked', '3d');
    const paleta = selectedValue('input[name="paletaCores"]:checked', 'PASTEL');
    const querPdf = (tipo === 'texto' && String(formatoTexto).toLowerCase() === 'pdf');

    const formData = new FormData();
    const moleculaText = safeValue('moleculaOutput', '');
    const moleculaBlob = new Blob([moleculaText], { type: 'text/plain' });
    formData.append('molecula', moleculaBlob, 'molecula.xyz');

    const analises = {};
    if (tipo === 'texto') {
      document.querySelectorAll('input[name="analises"]:checked').forEach((input) => {
        analises[input.value] = true;
      });
    }

    const payload = {
      render: {
        tipo,
        formato: tipo === 'grafico' ? formatoGrafico : (querPdf ? 'pdf' : 'tex'),
        paleta: tipo === 'grafico' ? paleta : null,
      },
      analises
    };

    formData.append('payload', JSON.stringify(payload));

    setDisabled(analiseBtn, true);
    showStatus('Processando...');
    clearUi();

    try {
      const response = await fetch(API_CONFIG.baseUrlAnalise, {
        method: 'POST',
        body: formData
      });

      const raw = await response.text();
      if (!response.ok) {
        throw new Error(raw || 'Erro na requisição');
      }

      let data;
      try {
        data = JSON.parse(raw);
      } catch {
        throw new Error('Resposta do backend não é JSON. Atualize o backend para retornar { tex, pdf_base64? }.');
      }

      const resultadoEl = ensureTextAreaResultado();
      resultadoEl.value = data?.tex ?? '';

      if (data?.pdf_base64) {
        const bytes = Uint8Array.from(atob(data.pdf_base64), (c) => c.charCodeAt(0));
        const blob = new Blob([bytes], { type: 'application/pdf' });
        const objectUrl = URL.createObjectURL(blob);

        setPdfObjectUrl(objectUrl);
        openPdfInNewTab(objectUrl);

        const btn = ensureAbrirPdfButton();
        btn.style.display = 'inline-block';
        btn.onclick = () => openPdfInNewTab(objectUrl);
      }

      showStatus('');
    } catch (error) {
      showStatus('');
      showError(error?.message ?? String(error));
    } finally {
      setDisabled(analiseBtn, false);
    }
  });
}

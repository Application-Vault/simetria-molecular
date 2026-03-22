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
    btnGerarPdf.addEventListener('click', async () => {
      const tex = resultadoEl?.value || '';

      if (!tex.trim()) {
        alert('Ainda não há conteúdo TeX para enviar.');
        return;
      }

      if (!API_CONFIG.baseUrlPdf) {
        showInfo('O endpoint do Lambda de PDF ainda não foi configurado em js/config.js.');
        return;
      }

      try {
        console.log('[PDF] clique detectado');
        console.log('[PDF] endpoint:', API_CONFIG.baseUrlPdf);

        btnGerarPdf.disabled = true;
        btnGerarPdf.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Gerando...';

        const response = await fetch(API_CONFIG.baseUrlPdf, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({ tex })
        });

        console.log('[PDF] status:', response.status);

        if (!response.ok) {
          const erro = await response.text();
          throw new Error(erro || 'Falha ao gerar PDF.');
        }

        const data = await response.json();
        console.log('[PDF] resposta:', data);

        if (data.pdf_base64) {
          const bytes = Uint8Array.from(atob(data.pdf_base64), c => c.charCodeAt(0));
          const blob = new Blob([bytes], { type: 'application/pdf' });
          const url = URL.createObjectURL(blob);
          window.open(url, '_blank', 'noopener,noreferrer');
        } else if (data.pdf_url) {
          window.open(data.pdf_url, '_blank', 'noopener,noreferrer');
        } else {
          alert('O Lambda respondeu, mas não retornou pdf_base64 nem pdf_url.');
        }

      } catch (err) {
        console.error('[PDF] erro:', err);
        alert('Erro ao gerar PDF: ' + err.message);
      } finally {
        btnGerarPdf.disabled = false;
        btnGerarPdf.innerHTML = '<i class="fa-regular fa-file-pdf"></i> Gerar PDF';
      }
    });
  }
}

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

      // ponto de ligação futuro
      console.log('Lambda PDF:', API_CONFIG.baseUrlPdf, { tex });
    });
  }
}

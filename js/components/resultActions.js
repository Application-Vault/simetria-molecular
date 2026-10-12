import { $ } from '../utils/dom.js';
import { t } from '../i18n.js';
import { initPdfJobs } from '../services/pdfJobs.js';

export function initResultActions() {
  const btnCopiarTex = $('btnCopiarTex');
  const resultadoEl = $('resultado');

  if (btnCopiarTex) {
    btnCopiarTex.addEventListener('click', async () => {
      const tex = resultadoEl?.value || '';
      if (!tex.trim()) {
        alert(t('Ainda não há conteúdo TeX para copiar.'));
        return;
      }

      try {
        await navigator.clipboard.writeText(tex);
        btnCopiarTex.innerHTML = `<i class="fa-solid fa-check"></i> ${t('Copiado')}`;
        setTimeout(() => {
          btnCopiarTex.innerHTML = `<i class="fa-regular fa-copy"></i> ${t('Copiar')}`;
        }, 1400);
      } catch (error) {
        alert(t('Não foi possível copiar o conteúdo.'));
        console.error(error);
      }
    });
  }

  initPdfJobs();
}

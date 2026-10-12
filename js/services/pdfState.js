import { $, ensureTextAreaResultado } from '../utils/dom.js';
import { t } from '../i18n.js';

let pdfObjectUrl = null;

export function revokePdfUrl() {
  if (pdfObjectUrl) {
    URL.revokeObjectURL(pdfObjectUrl);
    pdfObjectUrl = null;
  }
}

export function setPdfObjectUrl(url) {
  revokePdfUrl();
  pdfObjectUrl = url;
}

export function getPdfObjectUrl() {
  return pdfObjectUrl;
}

export function clearPdfUi() {
  document.dispatchEvent(new CustomEvent('pdf-reset'));
  const pdfBtn = $('abrirPdf');
  if (pdfBtn) pdfBtn.style.display = 'none';
  revokePdfUrl();
}

export function clearResultadoUi() {
  const resultadoEl = $('resultado');
  if (resultadoEl) resultadoEl.value = '';
}

export function clearUi() {
  clearResultadoUi();
  clearPdfUi();
}

export function ensureAbrirPdfButton() {
  let btn = $('abrirPdf');
  if (btn) return btn;

  btn = document.createElement('button');
  btn.id = 'abrirPdf';
  btn.innerHTML = `<i class="fa-regular fa-file-pdf" aria-hidden="true"></i> ${t('Abrir PDF')}`;
  btn.type = 'button';
  btn.className = 'btn';
  btn.style.display = 'none';

  const slot = $('pdfSlot');
  if (slot) {
    slot.appendChild(btn);
  } else {
    const after = ensureTextAreaResultado();
    after.insertAdjacentElement('afterend', btn);
  }

  return btn;
}

export function openPdfInNewTab(url) {
  window.open(url, '_blank', 'noopener,noreferrer');
}

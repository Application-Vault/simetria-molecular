import { $, selectedValue } from '../utils/dom.js';
import { clearUi } from '../services/pdfState.js';

export function trocarRender() {
  const tipo = selectedValue('input[name="renderTipo"]:checked', 'texto');
  const divTexto = $('render-texto');
  const divGrafico = $('render-grafico');

  if (!divTexto || !divGrafico) return;

  if (tipo === 'texto') {
    divTexto.style.display = 'block';
    divGrafico.style.display = 'none';
  } else {
    divTexto.style.display = 'none';
    divGrafico.style.display = 'block';
  }

  clearUi();
}

export function initRenderMode() {
  trocarRender();
  document.querySelectorAll('input[name="renderTipo"]').forEach((radio) => {
    radio.addEventListener('change', trocarRender);
  });
}

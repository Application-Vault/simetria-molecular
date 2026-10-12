import { t } from '../i18n.js';

export function $(id) {
  return document.getElementById(id);
}

export function safeValue(id, fallback = '') {
  return $(id)?.value ?? fallback;
}

export function selectedValue(selector, fallback = null) {
  return document.querySelector(selector)?.value ?? fallback;
}

export function setDisabled(el, disabled) {
  if (!el) return;
  el.disabled = !!disabled;
  el.style.opacity = disabled ? '0.65' : '1';
  el.style.cursor = disabled ? 'not-allowed' : 'pointer';
}

export function showError(msg) {
  alert(t('Erro na análise: {message}', { message: t(String(msg)) }));
}

export function showInfo(msg) {
  alert(t(msg));
}

export function showStatus(msg) {
  const el = $('status');
  if (!el) return;
  el.textContent = t(msg);
  el.style.display = msg ? 'block' : 'none';
}

export function ensureTextAreaResultado() {
  let el = $('resultado');
  if (el) return el;

  el = document.createElement('textarea');
  el.id = 'resultado';
  el.rows = 12;
  el.style.width = '100%';
  el.style.marginTop = '16px';
  document.body.appendChild(el);
  return el;
}

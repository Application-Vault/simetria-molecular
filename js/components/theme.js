import { atualizarTemaViewer } from './viewer.js';

export function initThemeToggle() {
  const key = 'sm_theme';
  const btn = document.getElementById('themeToggle');
  if (!btn) return;

  const icon = btn.querySelector('i');

  function syncThemeIcon() {
    const isLight = document.body.getAttribute('data-theme') === 'light';
    if (!icon) return;

    if (isLight) {
      icon.classList.remove('fa-moon');
      icon.classList.add('fa-sun');
    } else {
      icon.classList.remove('fa-sun');
      icon.classList.add('fa-moon');
    }
  }

  const saved = localStorage.getItem(key);
  if (saved === 'light') {
    document.body.setAttribute('data-theme', 'light');
  }

  syncThemeIcon();
  atualizarTemaViewer();

  btn.addEventListener('click', () => {
    const isLight = document.body.getAttribute('data-theme') === 'light';

    if (isLight) {
      document.body.removeAttribute('data-theme');
      localStorage.setItem(key, 'dark');
    } else {
      document.body.setAttribute('data-theme', 'light');
      localStorage.setItem(key, 'light');
    }

    syncThemeIcon();
    atualizarTemaViewer();
  });
}

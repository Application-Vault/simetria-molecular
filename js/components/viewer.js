import { $, safeValue } from '../utils/dom.js';

let viewer3d = null;

export function getViewerBackground() {
  const isLight = document.body.getAttribute('data-theme') === 'light';
  return isLight ? '#f8f9fc' : '#0b0f16';
}

export function clearViewer3D() {
  const el = $('viewer3d');
  if (!el) return;
  el.innerHTML = '';
  viewer3d = null;
}

export function renderizarMoleculaXYZ(xyzText) {
  const el = $('viewer3d');
  if (!el || typeof $3Dmol === 'undefined') return;

  const xyz = String(xyzText || '').trim();
  if (!xyz) {
    clearViewer3D();
    return;
  }

  el.innerHTML = '';

  viewer3d = $3Dmol.createViewer(el, {
    backgroundColor: getViewerBackground()
  });

  viewer3d.addModel(xyz, 'xyz');
  viewer3d.setStyle({}, {
    sphere: { scale: 0.32, colorscheme: 'Jmol' },
    stick: { radius: 0.14, colorscheme: 'Jmol' }
  });
  viewer3d.zoomTo();
  viewer3d.render();
}

export function atualizarViewerDaMolecula() {
  renderizarMoleculaXYZ(safeValue('moleculaOutput', ''));
}

export function atualizarTemaViewer() {
  if (!viewer3d) return;
  viewer3d.setBackgroundColor(getViewerBackground());
  viewer3d.render();
}

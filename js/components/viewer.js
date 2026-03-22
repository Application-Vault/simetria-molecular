import { $, safeValue } from '../utils/dom.js';

let viewer3d = null;
let currentXYZ = '';
let atomLabels = [];

export function getViewerBackground() {
  const isLight = document.body.getAttribute('data-theme') === 'light';
  return isLight ? '#f8f9fc' : '#0b0f16';
}

function getGraphicStyle() {
  return document.querySelector('input[name="estiloGrafico"]:checked')?.value || 'ballstick';
}

function getPaletteMode() {
  return document.querySelector('input[name="paletaCores"]:checked')?.value || 'PADRAO';
}

function getGraphicOptions() {
  return {
    estilo: getGraphicStyle(),
    paleta: getPaletteMode(),
    mostrarH: $('mostrarH')?.checked ?? true,
    mostrarLabels: $('mostrarLabels')?.checked ?? false,
    ativarSpin: $('ativarSpin')?.checked ?? false,
    fundoEscuro: $('fundoEscuro')?.checked ?? false,
  };
}

function clearAtomLabels() {
  if (!viewer3d || !atomLabels.length) return;
  atomLabels.forEach(label => viewer3d.removeLabel(label));
  atomLabels = [];
}

function getPaletteColors(mode) {
  switch (mode) {
    case 'PASTEL':
      return {
        H: '#f8f8f8',
        C: '#b7b7c9',
        N: '#a8c8ff',
        O: '#ffb3ba',
        F: '#c7f0bd',
        S: '#ffe29a',
        P: '#ffd6a5',
        Cl: '#c3f7d6',
        Br: '#d9b08c',
        I: '#cdb4db',
      };

    case 'VIBRANTE':
      return {
        H: '#ffffff',
        C: '#444444',
        N: '#2f6fff',
        O: '#ff2d2d',
        F: '#31c45d',
        S: '#ffcc00',
        P: '#ff7a00',
        Cl: '#00c853',
        Br: '#8d4b32',
        I: '#7b1fa2',
      };

    case 'MONOCROMATICA':
      return {
        H: '#d9d9d9',
        C: '#8c8c8c',
        N: '#8c8c8c',
        O: '#8c8c8c',
        F: '#8c8c8c',
        S: '#8c8c8c',
        P: '#8c8c8c',
        Cl: '#8c8c8c',
        Br: '#8c8c8c',
        I: '#8c8c8c',
      };

    case 'PADRAO':
    default:
      return null;
  }
}

function buildColorFunc(mode) {
  const palette = getPaletteColors(mode);
  if (!palette) return null;

  return function colorfunc(atom) {
    return palette[atom.elem] || '#cccccc';
  };
}

function buildViewerStyle(estilo, colorfunc) {
  if (estilo === 'stick') {
    return {
      stick: colorfunc
        ? { radius: 0.18, colorfunc }
        : { radius: 0.18, colorscheme: 'Jmol' },
    };
  }

  if (estilo === 'sphere') {
    return {
      sphere: colorfunc
        ? { scale: 0.55, colorfunc }
        : { scale: 0.55, colorscheme: 'Jmol' },
    };
  }

  if (estilo === 'line') {
    return {
      line: colorfunc
        ? { linewidth: 2.0, colorfunc }
        : { linewidth: 2.0, colorscheme: 'Jmol' },
    };
  }

  // default: ball & stick
  return {
    sphere: colorfunc
      ? { scale: 0.32, colorfunc }
      : { scale: 0.32, colorscheme: 'Jmol' },
    stick: colorfunc
      ? { radius: 0.14, colorfunc }
      : { radius: 0.14, colorscheme: 'Jmol' },
  };
}

function getAtomSelector(mostrarH) {
  return mostrarH ? {} : { elem: 'H', invert: true };
}

function applyLabels(selector, fundoEscuro) {
  if (!viewer3d) return;

  clearAtomLabels();

  const atoms = viewer3d.selectedAtoms(selector);
  atoms.forEach((atom, idx) => {
    const label = viewer3d.addLabel(`${atom.elem}${idx + 1}`, {
      position: { x: atom.x, y: atom.y, z: atom.z },
      backgroundOpacity: 0.55,
      fontColor: fundoEscuro ? '#ffffff' : '#222222',
      backgroundColor: fundoEscuro ? '#222831' : '#ffffff',
      borderThickness: 0.5,
      fontSize: 12,
    });
    atomLabels.push(label);
  });
}

export function clearViewer3D() {
  const el = $('viewer3d');
  if (!el) return;
  el.innerHTML = '';
  viewer3d = null;
  currentXYZ = '';
  atomLabels = [];
}

export function applyViewer3DOptions() {
  const el = $('viewer3d');
  if (!el || typeof $3Dmol === 'undefined') return;

  const xyz = String(currentXYZ || '').trim();
  if (!xyz) {
    clearViewer3D();
    return;
  }

  const {
    estilo,
    paleta,
    mostrarH,
    mostrarLabels,
    ativarSpin,
    fundoEscuro,
  } = getGraphicOptions();

  const bg = fundoEscuro ? '#0b0f16' : getViewerBackground();
  const selector = getAtomSelector(mostrarH);
  const colorfunc = buildColorFunc(paleta);
  const style = buildViewerStyle(estilo, colorfunc);

  el.innerHTML = '';

  viewer3d = $3Dmol.createViewer(el, {
    backgroundColor: bg,
  });

  viewer3d.addModel(xyz, 'xyz');
  viewer3d.setStyle(selector, style);

  if (mostrarLabels) {
    applyLabels(selector, fundoEscuro);
  }

  viewer3d.zoomTo(selector);
  viewer3d.spin(ativarSpin);
  viewer3d.render();
}

export function renderizarMoleculaXYZ(xyzText) {
  currentXYZ = String(xyzText || '').trim();
  applyViewer3DOptions();
}

export function update3DViewerFromXYZ(xyzText) {
  renderizarMoleculaXYZ(xyzText);
}

export function atualizarViewerDaMolecula() {
  const xyz = safeValue('moleculaOutput', '');
  update3DViewerFromXYZ(xyz);
}

export function atualizarTemaViewer() {
  if (!viewer3d || !currentXYZ) return;
  applyViewer3DOptions();
}

export function bindViewerControls() {
  document.querySelectorAll('input[name="estiloGrafico"]').forEach(el => {
    el.addEventListener('change', applyViewer3DOptions);
  });

  document.querySelectorAll('input[name="paletaCores"]').forEach(el => {
    el.addEventListener('change', applyViewer3DOptions);
  });

  ['mostrarH', 'mostrarLabels', 'ativarSpin', 'fundoEscuro'].forEach(id => {
    const el = $(id);
    if (el) {
      el.addEventListener('change', applyViewer3DOptions);
    }
  });

  const resetBtn = $('resetViewerBtn');
  if (resetBtn) {
    resetBtn.addEventListener('click', () => {
      const spinCheckbox = $('ativarSpin');
      if (spinCheckbox) spinCheckbox.checked = false;

      applyViewer3DOptions();
    });
  }

  const moleculaOutput = $('moleculaOutput');
  if (moleculaOutput) {
    moleculaOutput.addEventListener('input', () => {
      if (!moleculaOutput.readOnly) {
        update3DViewerFromXYZ(moleculaOutput.value);
      }
    });
  }
}
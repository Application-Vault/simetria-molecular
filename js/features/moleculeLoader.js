import { API_CONFIG } from '../config.js';
import { $, showStatus } from '../utils/dom.js';
import { clearPdfUi, clearResultadoUi } from '../services/pdfState.js';
import { atualizarViewerDaMolecula, clearViewer3D } from '../components/viewer.js';

export function initMoleculeLoader() {
  const moleculaSelect = $('moleculaSelect');
  const moleculaOutput = $('moleculaOutput');
  if (!moleculaSelect || !moleculaOutput) return;

  moleculaSelect.addEventListener('change', async () => {
    clearResultadoUi();
    clearPdfUi();

    const moleculaSelecionada = moleculaSelect.value;

    if (moleculaSelecionada === 'outro') {
      moleculaOutput.readOnly = false;
      moleculaOutput.value = '';
      clearViewer3D();
      return;
    }

    if (!moleculaSelecionada) {
      moleculaOutput.value = '';
      moleculaOutput.readOnly = true;
      clearViewer3D();
      return;
    }

    try {
      showStatus('Carregando molécula...');
      const resp = await fetch(API_CONFIG.baseUrlMoleculas + moleculaSelecionada);
      if (!resp.ok) throw new Error('Erro ao carregar o XYZ');

      const xyz = await resp.text();
      moleculaOutput.value = xyz;
      moleculaOutput.readOnly = true;
      atualizarViewerDaMolecula();
      showStatus('');
    } catch (error) {
      moleculaOutput.value = String(error?.message ?? error);
      clearViewer3D();
      showStatus('');
    }
  });

  moleculaOutput.addEventListener('input', () => {
    atualizarViewerDaMolecula();
  });
}

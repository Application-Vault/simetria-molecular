import { API_CONFIG } from '../config.js';
import { $, showStatus } from '../utils/dom.js';
import { clearPdfUi, clearResultadoUi } from '../services/pdfState.js';
import { atualizarViewerDaMolecula, clearViewer3D } from '../components/viewer.js';
import { t } from '../i18n.js';

export function initMoleculeLoader() {
  const moleculaSelect = $('moleculaSelect');
  const moleculaOutput = $('moleculaOutput');
  if (!moleculaSelect || !moleculaOutput) return;
  let loadError = null;
  document.addEventListener('languagechange', () => {
    if (loadError) moleculaOutput.value = t(loadError);
  });

  moleculaSelect.addEventListener('change', async () => {
    loadError = null;
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
      loadError = String(error?.message ?? error);
      moleculaOutput.value = t(loadError);
      clearViewer3D();
      showStatus('');
    }
  });

  moleculaOutput.addEventListener('input', () => {
    loadError = null;
    atualizarViewerDaMolecula();
  });
}

export async function carregarListaDeMoleculas() {
  const select = $('moleculaSelect');
  if (!select) return;

  select.replaceChildren(new Option(t('Carregando moléculas...'), ''));

  try {
    const resp = await fetch(API_CONFIG.baseUrlMoleculasList);
    if (!resp.ok) throw new Error('Erro ao carregar lista de moléculas');

    const data = await resp.json();
    const moleculas = Array.isArray(data?.moleculas) ? data.moleculas : [];

    select.innerHTML = '';

    const defaultOption = document.createElement('option');
    defaultOption.value = '';
    defaultOption.textContent = t('Selecione uma molécula ...');
    select.appendChild(defaultOption);

    moleculas.forEach((mol) => {
      const option = document.createElement('option');
      option.value = mol.id;
      option.dataset.i18nIgnore = '';
      option.textContent = mol.label;
      select.appendChild(option);
    });

    const otherOption = document.createElement('option');
    otherOption.value = 'outro';
    otherOption.textContent = t('Outra (especifique)');
    select.appendChild(otherOption);

  } catch (err) {
    console.error(err);
    select.replaceChildren(
      new Option(t('Erro ao carregar moléculas'), ''),
      new Option(t('Outra (especifique)'), 'outro')
    );
  }
}
import { initThemeToggle } from './components/theme.js';
import { initRenderMode } from './components/renderMode.js';
import { initResultActions } from './components/resultActions.js';
import { initMoleculeLoader, carregarListaDeMoleculas } from './features/moleculeLoader.js';
import { initAnalysis } from './features/analysis.js';
import { bindViewerControls } from './components/viewer.js';
import { initLanguage } from './i18n.js';

async function bootstrap() {
  initLanguage();
  initThemeToggle();
  initRenderMode();
  initResultActions();
  await carregarListaDeMoleculas();
  initMoleculeLoader();
  initAnalysis();
  bindViewerControls();
}

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', bootstrap);
} else {
  bootstrap();
}
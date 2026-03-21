import { initThemeToggle } from './components/theme.js';
import { initRenderMode } from './components/renderMode.js';
import { initResultActions } from './components/resultActions.js';
import { initMoleculeLoader } from './features/moleculeLoader.js';
import { initAnalysis } from './features/analysis.js';

function bootstrap() {
  initThemeToggle();
  initRenderMode();
  initResultActions();
  initMoleculeLoader();
  initAnalysis();
}

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', bootstrap);
} else {
  bootstrap();
}

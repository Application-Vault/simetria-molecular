import { initThemeToggle } from './components/theme.js';
import { initRenderMode } from './components/renderMode.js';
import { initResultActions } from './components/resultActions.js';
import { initMoleculeLoader } from './features/moleculeLoader.js';
import { initAnalysis } from './features/analysis.js';
import { bindViewerControls } from './components/viewer.js';

function bootstrap() {
  initThemeToggle();
  initRenderMode();
  initResultActions();
  initMoleculeLoader();
  initAnalysis();
  bindViewerControls();
}

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', bootstrap);
} else {
  bootstrap();
}

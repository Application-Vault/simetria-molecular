let __viewer3d = null;

function getViewerBackground() {
  const isLight = document.body.getAttribute("data-theme") === "light";
  return isLight ? "#f8f9fc" : "#0b0f16";
}

function clearViewer3D() {
  const el = $("viewer3d");
  if (!el) return;
  el.innerHTML = "";
  __viewer3d = null;
}

function renderizarMoleculaXYZ(xyzText) {
  const el = $("viewer3d");
  if (!el) return;

  const xyz = String(xyzText || "").trim();
  if (!xyz) {
    clearViewer3D();
    return;
  }

  el.innerHTML = "";

  __viewer3d = $3Dmol.createViewer(el, {
    backgroundColor: getViewerBackground()
  });

  __viewer3d.addModel(xyz, "xyz");
  __viewer3d.setStyle({}, {
    sphere: { scale: 0.32, colorscheme: "Jmol" },
    stick: { radius: 0.14, colorscheme: "Jmol" }
  });

  __viewer3d.zoomTo();
  __viewer3d.render();
}

function atualizarViewerDaMolecula() {
  renderizarMoleculaXYZ(safeValue("moleculaOutput", ""));
}

function atualizarTemaViewer() {
  if (!__viewer3d) return;
  __viewer3d.setBackgroundColor(getViewerBackground());
  __viewer3d.render();
}
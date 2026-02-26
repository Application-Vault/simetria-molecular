# visualizer.py

import pyvista as pv
import numpy as np

class PyvistaVisualizer:
    """
    Mostra, em duas sub-janelas, uma molécula antes e depois
    de uma transformação 3D (rotação, reflexão, etc.).
    """

    def __init__(self,
                 elementos: list[str],
                 coords_orig: list[list[float]],
                 coords_transf: list[list[float]],
                 titulo: str = "Simetria aplicada"):
        """
        elementos    : lista de símbolos (“C”, “H”, …)
        coords_orig  : [[x,y,z], …] antes da operação
        coords_transf: [[x,y,z], …] depois da operação
        titulo       : título geral da janela
        """
        self.elementos    = elementos
        self.coords_orig  = np.array(coords_orig)
        self.coords_trans = np.array(coords_transf)
        self.titulo       = titulo

        # raios aproximados para cada átomo
        self.raio = {"C": .3, "H": .2}

    def render(self):
        # cria plotter 1×2
        plotter = pv.Plotter(shape=(1, 2), window_size=(1400, 600))
        plotter.add_text(self.titulo, font_size=24)

        # lado esquerdo: molécula original
        plotter.subplot(0, 0)
        plotter.add_text("Antes", font_size=18)
        self._draw(plotter, self.coords_orig)

        # lado direito: molécula transformada
        plotter.subplot(0, 1)
        plotter.add_text("Depois", font_size=18)
        self._draw(plotter, self.coords_trans)

        plotter.link_views()
        plotter.show()

    def _draw(self, plotter: pv.Plotter, coords: np.ndarray):
        """Summary
        """
        # desenha cada átomo como esfera + rótulo
        for idx, (el, c) in enumerate(zip(self.elementos, coords), start=1):
            raio = self.raio.get(el, .2)
            sphere = pv.Sphere(radius=raio, center=c)
            plotter.add_mesh(sphere, color="lightgray", smooth_shading=True)
            plotter.add_point_labels(
                [c], [str(idx)],
                font_size=14,
                text_color="black",
                point_size=0,
                shape_opacity=0.0,
                always_visible=True
            )

        # desenha ligações (arestas) se distância < 1.3 Å
        n = len(coords)
        for i in range(n):
            for j in range(i+1, n):
                if np.linalg.norm(coords[i] - coords[j]) < 1.3:
                    line = pv.Line(coords[i], coords[j], resolution=1)
                    plotter.add_mesh(line, color="gray", line_width=2)
"""=================================================================================================================================================
**                                                   Copyright © 2025 Chanah Yocheved Bat Sarah                                                   **
**                                                                                                                                                **
**                                                       Author: Chanah Yocheved Bat Sarah                                                        **
**                                                          Contact: contact@chanah.dev                                                           **
**                                                                Date: 2025-05-25                                                                **
**                                                      License: Custom Attribution License                                                       **
**                                                                                                                                                **
**    Este módulo faz parte do projeto de simetria molecular desenvolvido no contexto da disciplina de pós-graduação PGF5261 Teoria de Grupos     **
**                                                       Aplicada para Sólidos e Moléculas.                                                       **
**                                                                                                                                                **
**   Permission is granted to use, copy, modify, and distribute this file, provided that this notice is retained in full and that the origin of   **
**    the software is clearly and explicitly attributed to the original author. Such attribution must be preserved not only within the source     **
**       code, but also in any accompanying documentation, public display, distribution, or derived work, in both digital or printed form.        **
**                                                  For licensing inquiries: contact@chanah.dev                                                   **
====================================================================================================================================================
"""

# import pyvista as pv
import numpy as np

class PyvistaVisualizer:
    
    def __init__(self, original, transformada, titulo="Simetria aplicada", destaque=None, cores=None, operacao=None):
        """Summary
        """
        print(">>>>>>>>>>>>>>>>>>>>>HERE>>>>>>>>>>>>>>>>>>>>")
        self.original = original
        self.transformada = transformada
        self.titulo = titulo
        self.destaque = destaque
        self.tamanho = {"C": 0.3, "H": 0.2}
        self.cores_personalizadas = cores
        self.plotter = pv.Plotter(shape=(1, 2), window_size=(1600, 800))
        self.elementos = original.elementos
        self.coordenadas = original.coordenadas
        self.operacao = operacao



    def renderizar(self):
        """Summary
        """
        transformada = self.transformada
        plotter = pv.Plotter(shape=(1, 2), window_size=(1600, 800))
        plotter.subplot(0, 0)
        destaques = self._gerar_destaques_da_operacao(self.operacao)
        self._desenhar_molecula(list(zip(self.elementos, self.coordenadas)), plotter, "Antes da simetria", destaques)
        plotter.subplot(0, 1)
        self._desenhar_molecula(transformada, plotter, "Depois da simetria")
        plotter.link_views()
        plotter.camera.azimuth -= 25
        plotter.camera.elevation -= 20
        plotter.camera.roll += 1
        plotter.show()


    def _gerar_cores(self, n):
        if self.cores_personalizadas:
            return self.cores_personalizadas[:n]
        base = [
            (174, 198, 207), (255, 179, 71), (179, 158, 181),
            (119, 221, 119), (255, 105, 97), (253, 253, 150),
            (207, 207, 196), (244, 154, 194), (222, 165, 164),
            (176, 224, 230), (230, 230, 250), (197, 227, 132)
        ]
        return base[:n]

    def _desenhar_molecula(self, molecula, plotter, titulo, destaque=None):
        """
        Desenha a molécula na ordem exata do .xyz, rotulando cada átomo
        com seu índice 1…N conforme aparece em 'molecula'.
        """
        import pyvista as pv

        # Desenhar átomos na ordem em que chegam no .xyz
        cores = self._gerar_cores(len(molecula))
        for idx, (el, coord) in enumerate(molecula, start=1):
            cor   = cores[(idx - 1) % len(cores)]
            raio  = self.tamanho.get(el, 0.2)
            esfera = pv.Sphere(radius=raio, center=coord)
            plotter.add_mesh(esfera, color=cor, smooth_shading=True)
            plotter.add_point_labels(
                [coord],
                [str(idx)],
                font_size=70,
                text_color='white',
                point_size=0,
                shape_opacity=0,
                always_visible=True
            )

        # Desenhar ligações e destacar, se solicitado
        self._desenhar_ligacoes(molecula, plotter)
        if destaque:
            self._destacar(destaque, plotter)

    # def _desenhar_molecula(self, molecula, plotter, titulo, destaque=None):
    #     """
    #     Desenha a molécula e rotula átomos com índices 1…N alinhados
    #     à mesma ordem usada para calcular permutações.
    #     """
    #     import numpy as np
    #     import pyvista as pv

    #     # 1) Identificar os dois carbonos (menor e maior z)
    #     carbonos = [(i, coord) for i, (el, coord) in enumerate(molecula) if el == "C"]
    #     c1_idx = min(carbonos, key=lambda x: x[1][2])[0]
    #     c2_idx = max(carbonos, key=lambda x: x[1][2])[0]
    #     c1_coord = np.array(molecula[c1_idx][1])
    #     c2_coord = np.array(molecula[c2_idx][1])

    #     # 2) Agrupar hidrogênios por proximidade a cada carbono
    #     h_c1, h_c2 = [], []
    #     for i, (el, coord) in enumerate(molecula):
    #         if el != "H":
    #             continue
    #         coord = np.array(coord)
    #         if np.linalg.norm(coord - c1_coord) < np.linalg.norm(coord - c2_coord):
    #             h_c1.append((i, float(np.linalg.norm(coord - c1_coord))))
    #         else:
    #             h_c2.append((i, float(np.linalg.norm(coord - c2_coord))))

    #     # 3) Ordenar para consistência visual
    #     h_c1.sort(key=lambda x: x[1])
    #     h_c2.sort(key=lambda x: x[1])

    #     # 4) Montar a lista de índices na ordem desejada
    #     #    (C1, C2, Hs de C1, Hs de C2)
    #     ordered_indices = [c1_idx, c2_idx] + [i for i,_ in h_c1] + [i for i,_ in h_c2]

    #     # 5) Reordenar a lista original de átomos
    #     molecula_ord = [molecula[i] for i in ordered_indices]

    #     # 6) Desenhar átomos e rotular usando idx+1
    #     cores = self._gerar_cores(len(molecula_ord))
    #     for idx, (el, coord) in enumerate(molecula_ord, start=1):
    #         cor   = cores[(idx - 1) % len(cores)]
    #         raio  = self.tamanho.get(el, 0.2)
    #         esfera = pv.Sphere(radius=raio, center=coord)
    #         plotter.add_mesh(esfera, color=cor, smooth_shading=True)
    #         plotter.add_point_labels(
    #             [coord],
    #             [str(idx)],
    #             font_size=14,
    #             text_color='white',
    #             point_size=0,
    #             shape_opacity=0,
    #             always_visible=True
    #         )

    #     # 7) Desenhar ligações e destacar, se pedido
    #     self._desenhar_ligacoes(molecula_ord, plotter)
    #     if destaque:
    #         self._destacar(destaque, plotter)

    # def _desenhar_molecula(self, molecula, plotter, titulo, destaque=None):
    #     """Summary
    #     """
    #     cores = self._gerar_cores(len(molecula))

    #     # Identificar carbonos
    #     carbonos = [(i, coord) for i, (el, coord) in enumerate(molecula) if el == "C"]
    #     c1_idx = min(carbonos, key=lambda x: x[1][2])[0]  # menor z
    #     c2_idx = max(carbonos, key=lambda x: x[1][2])[0]  # maior z
    #     c1_coord = molecula[c1_idx][1]
    #     c2_coord = molecula[c2_idx][1]

    #     # Inicializar dicionário de rótulos
    #     rotulos = {c1_idx: 1, c2_idx: 2}
    #     h_proximos_c1 = []
    #     h_proximos_c2 = []

    #     for i, (el, coord) in enumerate(molecula):
    #         if i in (c1_idx, c2_idx):
    #             continue
    #         dist_c1 = np.linalg.norm(np.array(coord) - np.array(c1_coord))
    #         dist_c2 = np.linalg.norm(np.array(coord) - np.array(c2_coord))
    #         if dist_c1 < dist_c2:
    #             h_proximos_c1.append((i, dist_c1))
    #         else:
    #             h_proximos_c2.append((i, dist_c2))

    #     # Ordenar para manter consistência visual
    #     h_proximos_c1.sort(key=lambda x: x[1])
    #     h_proximos_c2.sort(key=lambda x: x[1])

    #     for offset, (i, _) in enumerate(h_proximos_c1):
    #         rotulos[i] = 3 + offset
    #     for offset, (i, _) in enumerate(h_proximos_c2):
    #         rotulos[i] = 6 + offset

    #     print(">>>>>>>>>>>>>>>>>>>>.ROTULOS")
    #     print(rotulos)
    #     # rotulos = {4: 1, 0: 2, 6: 5, 5: 4, 7: 3, 1: 6, 2: 7, 3: 8}
    #     # Desenhar átomos e rótulos
    #     for i, (el, coord) in enumerate(molecula):
    #         cor = cores[i % len(cores)]
    #         raio = self.tamanho.get(el, 0.2)
    #         esfera = pv.Sphere(radius=raio, center=coord)
    #         plotter.add_mesh(esfera, color=cor, smooth_shading=True)
    #         plotter.add_point_labels([coord], [str(rotulos[i])], font_size=14, text_color='white',
    #                                  point_size=0, shape_opacity=0, always_visible=True)

    #     self._desenhar_ligacoes(molecula, plotter)

    #     if destaque:
    #         self._destacar(destaque, plotter)

    def _destacar(self, destaque, plotter):
        """Summary
        """
        print(">>>>>>>>>>>>DESTACAR>>>")
        # print(destaque)
        destaques = destaque if isinstance(destaque, list) else [destaque]
        for d in destaques:
            tipo = d["tipo"]
            centro = np.array(d.get("origem", [0.0, 0.0, 0.0]))

            if tipo == "eixo":
                mesh = self._gerar_eixo(d, centro)
                plotter.add_mesh(mesh, color="gray", line_width=3)

            # elif tipo == "plano":
            #     mesh = self._gerar_plano(d, centro)
            #     plotter.add_mesh(mesh, color="gray", opacity=0.3, show_edges=False)

            elif tipo == "ponto":
                mesh = self._gerar_ponto(centro)
                plotter.add_mesh(mesh, color="gray", opacity=0.5)

            else:
                print(f"[AVISO] Tipo de destaque desconhecido: {tipo}")

    def _gerar_eixo(self, d, centro):
        """Summary
        """
        vetor = np.array(d["direcao"])
        vetor = vetor.astype(float)
        vetor /= np.linalg.norm(vetor)
        return pv.Line(
            pointa=centro - 3.0 * vetor,
            pointb=centro + 3.0 * vetor,
            resolution=1
        )

    def _gerar_plano(self, d, centro):
        normal = np.array(d["normal"])
        return pv.Plane(
            center=centro,
            direction=normal / np.linalg.norm(normal),
            i_size=4.0,
            j_size=4.0
        )

    def _gerar_destaques_da_operacao(self, op):
        """Summary
        """
        print(">>>>>>>>>>>>DESTAQUES>>>")
        """Summary
        """
        destaques = []

        # Eixo (rotacao ou impropria)
        if "eixo" in op and isinstance(op["eixo"], list):
            destaques.append({
                "tipo": "eixo",
                "direcao": op["eixo"],
                "origem": op.get("origem", [0.0, 0.0, 0.0])
            })
        # print("Op:")
        # print(op)
        # Plano (reflexao ou impropria)
        if "plano_normal" in op and isinstance(op["plano_normal"], list):
            destaques.append({
                "tipo": "plano",
                "normal": op["plano_normal"],
                "origem": op.get("origem", [0.0, 0.0, 0.0])
            })

        if op["tipo"] == "inversao":
            destaques.append({
                "tipo": "ponto",
                "origem": [0, 0, 0]
            })
        # # Ponto (se não houver nem eixo nem plano, mas houver origem)
        # if "origem" in op and "eixo" not in op and "plano_normal" not in op:
        #     destaques.append({
        #         "tipo": "ponto",
        #         "origem": op["origem"]
        #     })
        print("DESTAQUES>>>>>:::::::::::::::")
        # print(destaques)
        return destaques

    def _desenhar_ligacoes(self, molecula, plotter):
        coords = molecula
        for i, (_, c1) in enumerate(coords):
            for j, (_, c2) in enumerate(coords):
                if i < j:
                    dist = np.linalg.norm(np.array(c1) - np.array(c2))
                    if dist < 1.2:
                        plotter.add_mesh(pv.Line(c1, c2), color="gray", line_width=3)

        for i, (el1, c1) in enumerate(coords):
            for j, (el2, c2) in enumerate(coords):
                if i < j and el1 == 'C' and el2 == 'C':
                    dist = np.linalg.norm(np.array(c1) - np.array(c2))
                    if dist < 1.6:
                        plotter.add_mesh(pv.Line(c1, c2), color='black', line_width=4)


    def _gerar_ponto(self, centro):
        return pv.Sphere(radius=0.1, center=centro)
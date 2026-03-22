"""=================================================================================================================================================
**                                                   Copyright © 2025 Chanah Yocheved Bat Sarah                                                   **
**                                                                                                                                                **
**                                                       Author: Chanah Yocheved Bat Sarah                                                        **
**                                                          Contact: contact@chanah.dev                                                           **
**                                                                Date: 2025-05-26                                                                **
**                                                      License: Custom Attribution License                                                       **
**                                                                                                                                                **
**                                                                      ---                                                                       **
**                                                                                                                                                **
**   Permission is granted to use, copy, modify, and distribute this file, provided that this notice is retained in full and that the origin of   **
**    the software is clearly and explicitly attributed to the original author. Such attribution must be preserved not only within the source     **
**       code, but also in any accompanying documentation, public display, distribution, or derived work, in both digital or printed form.        **
**                                                  For licensing inquiries: contact@chanah.dev                                                   **
====================================================================================================================================================
"""

# symmetry_analyzer.py
import numpy as np
from time import perf_counter
from analysis.analise_tabela_multiplicacao import TabelaMultiplicacao
from analysis.analise_classe_conjugacao import ClasseConjugacao
from core.core_molecula import Molecule
from render.render_tex import LatexReportGenerator
from render.render_3D import PyvistaVisualizer
from render.render_pdf import PdfReportGenerator 
from render.render_tipo import RenderTipo
from representation.builder import RepresentationBuilder, RepresentationType
from representation.representation import Representation
from core.core_grupo import Group
from representation.builder import RepresentationBuilder, RepresentationType
from datetime import datetime
from analysis.analise_tipo import AnaliseTipo
from representation.representation_matrix3d import Matrix3DRepresentation
from representation.representation_permutation import PermutationRepresentation

class SymmetryAnalyzer:

    def __init__(self, molecule, group):
        """Summary
        """
        self.molecule = molecule
        self.group = group
        self._tipo = RepresentationType.PERMUTATION  # padrão
        self._analises = []
        self._resultado = None
        self._uuid = None
        # print(self.group.operacoes)

    @classmethod
    def de(cls, group: Group, molecule: Molecule) -> 'SymmetryAnalyzer':
        return cls(molecule, group)

    def usar(self, tipo: RepresentationType) -> 'SymmetryAnalyzer':
        # print(
        #     f"\n\033[95m>>> Usando grupo: \033[1m{self.group.nome}\033[0m "
        #     f"\033[94mcom molécula: \033[1m{getattr(self.molecule, 'nome', 'desconhecida')}\033[0m"
        # ) -> print log colorido!!! :)
        self.rep = (
            RepresentationBuilder()
            .de(self.group, self.molecule)
            .usar(tipo)
            .construir()
        )
        self._tipo = tipo
        return self

    def configurar(self, analises: list, uuid: str) -> 'SymmetryAnalyzer':
        self._analises = analises
        self._uuid = uuid
        return self

    def get_representacao(self) -> Representation:
        return (
            RepresentationBuilder()
            .de(group=self.group, molecule=self.molecule)
            .usar(self._tipo)
            .construir()
        )

    def executar(self) -> 'SymmetryAnalyzer':
        """Summary
        """
        inicio = perf_counter()
        representacao = self.get_representacao()
        resultado = {}
        if AnaliseTipo.PERMUTACOES in self._analises:
            resultado["permutacoes"] = representacao.get_permutacoes()

        if AnaliseTipo.TABELA_MULTIPLICACAO in self._analises:
            resultado["operacoes_multiplicacao"] = TabelaMultiplicacao(representacao).gerar()

        if AnaliseTipo.CLASSES_CONJUGACAO in self._analises:
            classes, conjugacao = ClasseConjugacao(representacao).gerar()

            # print("[DEBUG CLASSES GERADAS]", classes)
            # print("[DEBUG CONJUGACAO GERADA]", conjugacao)
            resultado["operacoes_conjugacao"] = conjugacao
            resultado["classes_conjugacao"] = classes


        resultado["tempo_execucao"] = f"{perf_counter() - inicio:.2f}s"
        self._resultado = resultado
        return self

    def renderizar(self, formato: RenderTipo) -> str:
        """Summary

        Raises:
            RuntimeError: Description
            ValueError: Description
        """
        if self._resultado is None:
            raise RuntimeError("Você precisa chamar `.executar()` antes de `.renderizar()`.")
        # print(formato)

        metadata = self._gerar_metadata()
        if formato == RenderTipo.TEX:
            return LatexReportGenerator(metadata, self._resultado).gerar_documento()
        elif formato == RenderTipo.PDF:
            return PdfReportGenerator(metadata, self._resultado).gerar_pdf()  # bytes
        else:
            raise ValueError(f"Formato de saída não suportado: {formato}")

    def _gerar_metadata(self) -> dict:
        """Summary
        """
        return {
            "molecula": self.molecule.nome,
            "grupo": self.group.nome,
            "ordem": len(self.group.operacoes),
            "uuid": self._uuid,
            "data": datetime.today().strftime("%Y-%m-%d %H:%M"),
            "sistema": self.group.sistema
        }

    def _buscar_operacao(self, sel_op):
        """Summary

        Raises:
            ValueError: Description
        """
        for op in self.group.operacoes:
            # print(op)
            if op.get("id") == sel_op:
                return op
        raise ValueError(f"Operação com id {sel_op}' não encontrada.")

    def _gerar_matriz_rotacao(self, eixo, angulo_graus):
        """Summary
        """
        ang = np.radians(angulo_graus)
        x, y, z = eixo / np.linalg.norm(eixo)
        c, s = np.cos(ang), np.sin(ang)
        return np.array([
            [c + x*x*(1-c),   x*y*(1-c) - z*s, x*z*(1-c) + y*s],
            [y*x*(1-c) + z*s, c + y*y*(1-c),   y*z*(1-c) - x*s],
            [z*x*(1-c) - y*s, z*y*(1-c) + x*s, c + z*z*(1-c)]
        ])

    def _transformar(self, oper):
        """Summary
        """
        tipo = oper["tipo"]
        coords = np.array(self.molecule.coordenadas)
        if tipo in ["rotacao", "impropria"]:
            eixo = np.array(oper["eixo"])
            angulo = oper["angulo"]
            R = self._gerar_matriz_rotacao(eixo, angulo)
            coords = coords @ R.T
            if tipo == "impropria":
                plano = np.array(oper["plano_normal"])
                plano = plano / np.linalg.norm(plano)
                coords = coords - 2 * np.outer(np.dot(coords, plano), plano)
        elif tipo == "reflexao":
            plano = np.array(oper["plano_normal"])
            plano = plano / np.linalg.norm(plano)
            coords = coords - 2 * np.outer(np.dot(coords, plano), plano)
        elif tipo == "inversao":
            coords = -coords
        return list(zip(self.molecule.elementos, coords.tolist()))



    def renderizar_operacao(self, selected_op):
        """Summary
        """
        op = self._buscar_operacao(selected_op)
        transformada = self._transformar(op)

        print(">>>RENDER")
        return PyvistaVisualizer(self.molecule, transformada, operacao=op).renderizar()




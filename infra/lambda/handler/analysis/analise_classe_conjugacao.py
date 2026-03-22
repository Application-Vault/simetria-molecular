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

import json
import re
from pathlib import Path
from representation.representation import Representation

class ClasseConjugacao:
    def __init__(self, representation: Representation):
        self.rep = representation

    def gerar(self):
        """
        Retorna uma tupla:
        - classes: dict com representante -> lista de nomes da classe
        - conjugacao_detalhada: dict com g -> h -> {resultado, detalhe}
        """
        nomes = self.rep.nomes()
        usados = set()
        conjugacao_detalhada = {}
        classes_formatadas = {}

        for g in nomes:
            if g in usados:
                continue

            classe = set()
            conjugacao_detalhada[g] = {}

            for h in nomes:
                perm_g = self.rep[g]
                perm_h = self.rep[h]

                # h g h^{-1}
                conj = self.rep.conjugar(perm_g, perm_h)

                nome_resultado = self._nome_da_permutacao(self.rep, conj, nomes, g)

                classe.add(nome_resultado)
                conjugacao_detalhada[g][h] = {
                    "resultado": nome_resultado,
                    "detalhe": {
                        "g": perm_g,
                        "h": perm_h,
                        "hgh⁻¹": conj
                    }
                }

            classe_ordenada = sorted(classe, key=nomes.index)
            classes_formatadas[g] = classe_ordenada
            usados.update(classe)

        return classes_formatadas, conjugacao_detalhada

    @staticmethod
    def _nome_da_permutacao(rep, perm_resultado, nomes, g):
        if rep[g] == perm_resultado:
            return g

        for nome_k in nomes:
            if nome_k != "E" and rep[nome_k] == perm_resultado:
                return nome_k

        for nome_k in nomes:
            if rep[nome_k] == perm_resultado:
                return nome_k

        return "??"
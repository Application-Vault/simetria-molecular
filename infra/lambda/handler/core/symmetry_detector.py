from dataclasses import dataclass
from typing import Any

import numpy as np


@dataclass
class DetectedOperation:
    tipo: str
    nome: str
    comentario: str
    eixo: list[float] | None = None
    angulo: float | None = None
    plano_normal: list[float] | None = None

    def to_dict(self) -> dict[str, Any]:
        d = {
            "tipo": self.tipo,
            "nome": self.nome,
            "comentario": self.comentario,
        }
        if self.eixo is not None:
            d["eixo"] = self.eixo
        if self.angulo is not None:
            d["angulo"] = self.angulo
        if self.plano_normal is not None:
            d["plano_normal"] = self.plano_normal
        return d


class SymmetryDetector:
    def __init__(self, molecule, tolerancia: float = 0.02):
        self.molecule = molecule
        self.tol = float(tolerancia)

    # ============================================================
    # UTILITÁRIOS BÁSICOS
    # ============================================================
    def detect_operations(self) -> list[dict[str, Any]]:
        """
        Começa com a identidade apenas.
        Depois vamos enriquecer isso com detecção geométrica real.
        """
        return [
            DetectedOperation(
                tipo="identidade",
                nome="\\mathrm{E}",
                comentario="Identidade",
            ).to_dict()
        ]

    def _group_payload(self, nome: str, descricao: str, ops: list[dict[str, Any]]) -> dict[str, Any]:
        return {
            "nome": nome,
            "descricao": descricao,
            "ordem": len(ops),
            "operacoes": ops,
            "tolerancia": self.tol,
        }

    # ============================================================
    # MOTOR PRINCIPAL — FLUXOGRAMA
    # ============================================================
    def infer_group(self) -> dict[str, Any]:
        ops = self.detect_operations()

        if self.e_linear():
            if self.tem_inversao():
                return self._group_payload("D∞h", "Molécula linear com inversão", ops)
            return self._group_payload("C∞v", "Molécula linear sem inversão", ops)

        if self.tem_dois_ou_mais_eixos_cn_maior_que_2():
            return self.classificar_grupo_cubico()

        if self.tem_um_eixo_cn():
            n, eixo_principal = self.obter_eixo_principal()

            if self.tem_n_eixos_c2_perpendiculares(n, eixo_principal):
                if self.tem_plano_horizontal(eixo_principal):
                    return self._group_payload(f"D{n}h", "Grupo Dnh", ops)

                if self.tem_n_planos_diagonais(n, eixo_principal):
                    return self._group_payload(f"D{n}d", "Grupo Dnd", ops)

                return self._group_payload(f"D{n}", "Grupo Dn", ops)

            if self.tem_plano_horizontal(eixo_principal):
                return self._group_payload(f"C{n}h", "Grupo Cnh", ops)

            if self.tem_n_planos_verticais(n, eixo_principal):
                return self._group_payload(f"C{n}v", "Grupo Cnv", ops)

            if self.tem_eixo_s2n(n, eixo_principal):
                return self._group_payload(f"S{2*n}", f"Grupo S{2*n}", ops)

            return self._group_payload(f"C{n}", "Grupo Cn", ops)

        if self.tem_plano_espelho():
            return self._group_payload("Cs", "Grupo Cs", ops)

        if self.tem_inversao():
            return self._group_payload("Ci", "Grupo Ci", ops)

        return self._group_payload("C1", "Grupo C1", ops)

    # ============================================================
    # LOSANGOS DO FLUXOGRAMA
    # ============================================================

    # 1) A molécula é linear?

    def e_linear(self) -> bool:
        species, coords = self._extract_species_coords(self.molecule)
        coords = np.asarray(coords, dtype=float)

        if coords.ndim != 2 or coords.shape[1] != 3:
            return False

        if len(coords) < 3:
            return True

        center = coords.mean(axis=0)
        centered = coords - center

        ref = None
        for v in centered:
            if np.linalg.norm(v) > self.tol:
                ref = v / np.linalg.norm(v)
                break

        if ref is None:
            return True

        for v in centered:
            norm = np.linalg.norm(v)
            if norm <= self.tol:
                continue

            u = v / norm
            cross = np.linalg.norm(np.cross(ref, u))

            if cross > 5 * self.tol:
                return False

        return True

    # 2) Existe inversão?
    def tem_inversao(self) -> bool:
        return False

    # 3) Ela tem dois ou mais eixos Cn com n > 2?
    def tem_dois_ou_mais_eixos_cn_maior_que_2(self) -> bool:
        return False

    # 4) Classificação cúbica: I / Ih / O / Oh / Td
    def classificar_grupo_cubico(self) -> dict[str, Any]:
        ops = self.detect_operations()
        return self._group_payload("C1", "Classificação cúbica ainda não implementada", ops)

    # 5) Ela tem um eixo Cn?
    def tem_um_eixo_cn(self) -> bool:
        return False

    # 6) Qual é o eixo principal?
    def obter_eixo_principal(self) -> tuple[int, np.ndarray | None]:
        return 1, None

    # 7) Existem n eixos C2 perpendiculares ao eixo principal?
    def tem_n_eixos_c2_perpendiculares(self, n: int, eixo_principal: np.ndarray | None) -> bool:
        return False

    # 8) Existe um plano de espelho horizontal?
    def tem_plano_horizontal(self, eixo_principal: np.ndarray | None) -> bool:
        return False

    # 9) Existem n planos de espelho diagonais?
    def tem_n_planos_diagonais(self, n: int, eixo_principal: np.ndarray | None) -> bool:
        return False

    # 10) Existem n planos de espelho verticais?
    def tem_n_planos_verticais(self, n: int, eixo_principal: np.ndarray | None) -> bool:
        return False

    # 11) Existe um eixo S2n?
    def tem_eixo_s2n(self, n: int, eixo_principal: np.ndarray | None) -> bool:
        return False

    # 12) Existe um plano de espelho?
    def tem_plano_espelho(self) -> bool:
        return False

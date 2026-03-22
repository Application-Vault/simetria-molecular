from dataclasses import dataclass
from typing import Any

import numpy as np

# ============================================================
# HELPERS
# ============================================================

def _normalize(v: np.ndarray, eps: float = 1e-12) -> np.ndarray:
    n = float(np.linalg.norm(v))
    if n < eps:
        return v.copy()
    return v / n

def _rotation_matrix(axis: np.ndarray, angle_deg: float) -> np.ndarray:
    axis = _normalize(np.asarray(axis, dtype=float))
    theta = np.deg2rad(float(angle_deg))
    x, y, z = axis

    c = np.cos(theta)
    s = np.sin(theta)
    C = 1.0 - c

    return np.array([
        [c + x*x*C,     x*y*C - z*s, x*z*C + y*s],
        [y*x*C + z*s,   c + y*y*C,   y*z*C - x*s],
        [z*x*C - y*s,   z*y*C + x*s, c + z*z*C  ],
    ], dtype=float)

# ============================================================
# SYMMETRY
# ============================================================

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

    def _reflection_matrix(self, normal: np.ndarray) -> np.ndarray:
        n = _normalize(np.asarray(normal, dtype=float))
        return np.eye(3) - 2.0 * np.outer(n, n)

    def _match_structure(self, coords_a: np.ndarray, coords_b: np.ndarray, species: list[str], tol: float) -> bool:
        from collections import defaultdict

        idx_by_species = defaultdict(list)
        for i, sp in enumerate(species):
            idx_by_species[sp].append(i)

        used = set()

        for i, sp in enumerate(species):
            pi = coords_a[i]
            candidates = idx_by_species[sp]

            best_j = None
            best_d = None

            for j in candidates:
                if j in used:
                    continue

                d = np.linalg.norm(pi - coords_b[j])
                if d <= tol and (best_d is None or d < best_d):
                    best_j = j
                    best_d = d

            if best_j is None:
                return False

            used.add(best_j)

        return True

    def _tem_rotacao(self, axis: np.ndarray, angle_deg: float) -> bool:
        species, coords = self._extract_species_coords(self.molecule)
        coords = np.asarray(coords, dtype=float)

        center = coords.mean(axis=0)
        centered = coords - center

        M = _rotation_matrix(axis, angle_deg)
        rotated = centered @ M.T

        return self._match_structure(rotated, centered, species, self.tol)

    def _candidate_axes(self) -> list[np.ndarray]:
        species, coords = self._extract_species_coords(self.molecule)
        coords = np.asarray(coords, dtype=float)

        center = coords.mean(axis=0)
        centered = coords - center

        axes = []

        # cartesianos
        axes.extend([
            np.array([1.0, 0.0, 0.0]),
            np.array([0.0, 1.0, 0.0]),
            np.array([0.0, 0.0, 1.0]),
        ])

        # autovetores geométricos
        cov = centered.T @ centered
        _, eigvecs = np.linalg.eigh(cov)
        for k in range(3):
            axes.append(_normalize(eigvecs[:, k]))

        # vetores centro -> átomo
        for v in centered:
            if np.linalg.norm(v) > self.tol:
                axes.append(_normalize(v))

        # remover duplicados até sinal
        unique = []
        for a in axes:
            keep = True
            for b in unique:
                if np.linalg.norm(a - b) < 1e-3 or np.linalg.norm(a + b) < 1e-3:
                    keep = False
                    break
            if keep:
                unique.append(a)

        return unique

    def _tem_reflexao(self, normal: np.ndarray) -> bool:
        species, coords = self._extract_species_coords(self.molecule)
        coords = np.asarray(coords, dtype=float)

        center = coords.mean(axis=0)
        centered = coords - center

        M = self._reflection_matrix(normal)
        reflected = centered @ M.T

        return self._match_structure(reflected, centered, species, self.tol)


    def _candidate_plane_normals(self) -> list[np.ndarray]:
        species, coords = self._extract_species_coords(self.molecule)
        coords = np.asarray(coords, dtype=float)

        center = coords.mean(axis=0)
        centered = coords - center

        normals = []

        # cartesianos
        normals.extend([
            np.array([1.0, 0.0, 0.0]),
            np.array([0.0, 1.0, 0.0]),
            np.array([0.0, 0.0, 1.0]),
        ])

        # autovetores geométricos
        cov = centered.T @ centered
        _, eigvecs = np.linalg.eigh(cov)
        for k in range(3):
            normals.append(_normalize(eigvecs[:, k]))

        # vetores centro -> átomo
        for v in centered:
            if np.linalg.norm(v) > self.tol:
                normals.append(_normalize(v))

        # remove duplicados até sinal
        unique = []
        for n in normals:
            keep = True
            for m in unique:
                if np.linalg.norm(n - m) < 1e-3 or np.linalg.norm(n + m) < 1e-3:
                    keep = False
                    break
            if keep:
                unique.append(n)

        return unique

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
            print("[DEBUG eixo principal]", n, eixo_principal)

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
    # EXTRAÇÃO DE DADOS
    # ============================================================
    def _extract_species_coords(self, molecule):
        if hasattr(molecule, "atoms"):
            species = []
            coords = []
            for atom in molecule.atoms:
                if isinstance(atom, dict):
                    species.append(atom.get("element") or atom.get("simbolo"))
                    coords.append(atom.get("coord") or atom.get("coords"))
                else:
                    species.append(
                        getattr(atom, "element", None)
                        or getattr(atom, "simbolo", None)
                    )
                    coords.append(
                        getattr(atom, "coord", None)
                        or getattr(atom, "coords", None)
                    )
            return species, coords

        if hasattr(molecule, "species") and hasattr(molecule, "coords"):
            return list(molecule.species), np.asarray(molecule.coords, dtype=float)

        if hasattr(molecule, "elementos") and hasattr(molecule, "coordenadas"):
            return list(molecule.elementos), np.asarray(molecule.coordenadas, dtype=float)

        raise ValueError("Não consegui extrair espécies e coordenadas de Molecule.")


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
        species, coords = self._extract_species_coords(self.molecule)
        coords = np.asarray(coords, dtype=float)

        if coords.ndim != 2 or coords.shape[1] != 3:
            return False

        center = coords.mean(axis=0)
        centered = coords - center

        usados = set()

        for i, sp in enumerate(species):
            alvo = -centered[i]

            melhor_j = None
            melhor_d = None

            for j, sp_j in enumerate(species):
                if j in usados:
                    continue
                if sp_j != sp:
                    continue

                d = np.linalg.norm(centered[j] - alvo)
                if d <= self.tol and (melhor_d is None or d < melhor_d):
                    melhor_j = j
                    melhor_d = d

            if melhor_j is None:
                return False

            usados.add(melhor_j)

        return True

    # 3) Ela tem dois ou mais eixos Cn com n > 2?
    def tem_dois_ou_mais_eixos_cn_maior_que_2(self) -> bool:
        return False

    # 4) Classificação cúbica: I / Ih / O / Oh / Td
    def classificar_grupo_cubico(self) -> dict[str, Any]:
        ops = self.detect_operations()
        return self._group_payload("C1", "Classificação cúbica ainda não implementada", ops)

    # 5) Ela tem um eixo Cn?
    def tem_um_eixo_cn(self) -> bool:
        axes = self._candidate_axes()

        for axis in axes:
            for n in [6, 5, 4, 3, 2]:
                angle = 360.0 / n
                if self._tem_rotacao(axis, angle):
                    return True

        return False

    # 6) Qual é o eixo principal?
    def obter_eixo_principal(self) -> tuple[int, np.ndarray | None]:
        axes = self._candidate_axes()

        best_n = 1
        best_axis = None

        for axis in axes:
            for n in [6, 5, 4, 3, 2]:
                angle = 360.0 / n
                if self._tem_rotacao(axis, angle):
                    if n > best_n:
                        best_n = n
                        best_axis = axis.copy()
                    break

        return best_n, best_axis

    # 7) Existem n eixos C2 perpendiculares ao eixo principal?
    def tem_n_eixos_c2_perpendiculares(self, n: int, eixo_principal: np.ndarray | None) -> bool:
        return False

    # 8) Existe um plano de espelho horizontal?
    def tem_plano_horizontal(self, eixo_principal: np.ndarray | None) -> bool:
        if eixo_principal is None:
            return False

        eixo_principal = _normalize(np.asarray(eixo_principal, dtype=float))
        normals = self._candidate_plane_normals()

        for normal in normals:
            # plano horizontal => normal paralela ao eixo principal
            paralela = (
                np.linalg.norm(normal - eixo_principal) < 1e-3
                or np.linalg.norm(normal + eixo_principal) < 1e-3
            )

            if paralela and self._tem_reflexao(normal):
                return True

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

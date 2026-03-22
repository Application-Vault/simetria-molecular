import math
from collections import defaultdict
from dataclasses import dataclass
from typing import Any

import numpy as np


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


def _reflection_matrix(normal: np.ndarray) -> np.ndarray:
    n = _normalize(np.asarray(normal, dtype=float))
    return np.eye(3) - 2.0 * np.outer(n, n)


def _improper_matrix(axis: np.ndarray, angle_deg: float) -> np.ndarray:
    # S_n = sigma_h * C_n, com sigma_h perpendicular ao eixo
    axis = _normalize(np.asarray(axis, dtype=float))
    rot = _rotation_matrix(axis, angle_deg)
    refl = _reflection_matrix(axis)
    return refl @ rot


def _inversion_matrix() -> np.ndarray:
    return -np.eye(3)


@dataclass
class DetectedOperation:
    tipo: str
    nome: str
    comentario: str
    eixo: list[float] | None = None
    angulo: float | None = None
    plano_normal: list[float] | None = None

    def _log_summary(
        self,
        ops: list[dict[str, Any]],
        rotations: list[dict[str, Any]],
        reflections: list[dict[str, Any]],
        impropers: list[dict[str, Any]],
        has_i: bool,
        n_main: int | None,
        main_axis: np.ndarray | None,
        sigma_h: bool,
        sigma_v_count: int,
        sigma_d_count: int,
        c2_perp_count: int,
    ) -> None:
        print("========== [DEBUG SYMMETRY DETECTOR] ==========")
        print("species:", self.species)
        print("center:", self.center.tolist())
        print("linear:", self.is_linear())
        print("has_inversion:", has_i)
        print("n_main:", n_main)
        print("main_axis:", None if main_axis is None else np.round(main_axis, 6).tolist())
        print("sigma_h:", sigma_h)
        print("sigma_v_count:", sigma_v_count)
        print("sigma_d_count:", sigma_d_count)
        print("c2_perp_count:", c2_perp_count)
        print("rotations:", [op["nome"] for op in rotations])
        print("reflections:", [op["nome"] for op in reflections])
        print("impropers:", [op["nome"] for op in impropers])
        print("all_ops:", [op["nome"] for op in ops])
        print("==============================================")
        
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

        self.species, self.coords = self._extract_species_coords(molecule)
        self.coords = np.asarray(self.coords, dtype=float)

        if self.coords.ndim != 2 or self.coords.shape[1] != 3:
            raise ValueError("Coordenadas inválidas para detecção de simetria.")

        self.center = self.coords.mean(axis=0)
        self.coords_centered = self.coords - self.center

        self._ops: list[DetectedOperation] = []

    # ----------------------------
    # Extração de dados
    # ----------------------------
    def _extract_species_coords(self, molecule):
        # Ajuste conservador para diferentes formatos possíveis da sua classe Molecule
        if hasattr(molecule, "atoms"):
            species = []
            coords = []
            for atom in molecule.atoms:
                if isinstance(atom, dict):
                    species.append(atom.get("element") or atom.get("simbolo"))
                    coords.append(atom.get("coord") or atom.get("coords"))
                else:
                    species.append(getattr(atom, "element", None) or getattr(atom, "simbolo", None))
                    coords.append(getattr(atom, "coord", None) or getattr(atom, "coords", None))
            return species, coords

        if hasattr(molecule, "species") and hasattr(molecule, "coords"):
            return list(molecule.species), np.asarray(molecule.coords, dtype=float)

        if hasattr(molecule, "elementos") and hasattr(molecule, "coordenadas"):
            return list(molecule.elementos), np.asarray(molecule.coordenadas, dtype=float)

        raise ValueError("Não consegui extrair espécies e coordenadas de Molecule.")

    # ----------------------------
    # Teste genérico de operação
    # ----------------------------
    def has_symmetry_matrix(self, M: np.ndarray) -> bool:
        transformed = self.coords_centered @ M.T
        return self._match_structure(transformed, self.coords_centered, self.species, self.tol)

    def _match_structure(
        self,
        coords_a: np.ndarray,
        coords_b: np.ndarray,
        species: list[str],
        tol: float,
    ) -> bool:
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

    # ----------------------------
    # Detectores básicos
    # ----------------------------
    def is_linear(self) -> bool:
        if len(self.coords_centered) < 3:
            return True

        ref = None
        for v in self.coords_centered:
            if np.linalg.norm(v) > self.tol:
                ref = _normalize(v)
                break

        if ref is None:
            return True

        for v in self.coords_centered:
            if np.linalg.norm(v) <= self.tol:
                continue
            vv = _normalize(v)
            cross = np.linalg.norm(np.cross(ref, vv))
            if cross > 5 * self.tol:
                return False
        return True

    def has_inversion(self) -> bool:
        return self.has_symmetry_matrix(_inversion_matrix())

    def has_reflection(self, normal: np.ndarray) -> bool:
        return self.has_symmetry_matrix(_reflection_matrix(normal))

    def has_rotation(self, axis: np.ndarray, angle_deg: float) -> bool:
        return self.has_symmetry_matrix(_rotation_matrix(axis, angle_deg))

    def has_improper(self, axis: np.ndarray, angle_deg: float) -> bool:
        return self.has_symmetry_matrix(_improper_matrix(axis, angle_deg))

    # ----------------------------
    # Candidatos geométricos
    # ----------------------------
    def candidate_axes(self) -> list[np.ndarray]:
        axes = []

        # Eixos cartesianos
        axes.extend([
            np.array([1.0, 0.0, 0.0]),
            np.array([0.0, 1.0, 0.0]),
            np.array([0.0, 0.0, 1.0]),
        ])

        # Eixos principais de inércia aproximados
        cov = self.coords_centered.T @ self.coords_centered
        _, eigvecs = np.linalg.eigh(cov)
        for k in range(3):
            axes.append(_normalize(eigvecs[:, k]))

        # Vetores centro -> átomo
        for v in self.coords_centered:
            if np.linalg.norm(v) > self.tol:
                axes.append(_normalize(v))

        # remove duplicados até sinal
        unique = []
        for a in axes:
            if np.linalg.norm(a) < 1e-10:
                continue
            keep = True
            for b in unique:
                if np.linalg.norm(a - b) < 1e-3 or np.linalg.norm(a + b) < 1e-3:
                    keep = False
                    break
            if keep:
                unique.append(a)

        return unique

    def candidate_plane_normals(self) -> list[np.ndarray]:
        normals = []

        # Cartesianos
        normals.extend([
            np.array([1.0, 0.0, 0.0]),
            np.array([0.0, 1.0, 0.0]),
            np.array([0.0, 0.0, 1.0]),
        ])

        # mesmos eixos candidatos servem como normais de plano
        normals.extend(self.candidate_axes())

        unique = []
        for n in normals:
            if np.linalg.norm(n) < 1e-10:
                continue
            n = _normalize(n)
            keep = True
            for m in unique:
                if np.linalg.norm(n - m) < 1e-3 or np.linalg.norm(n + m) < 1e-3:
                    keep = False
                    break
            if keep:
                unique.append(n)

        return unique

    # ----------------------------
    # Busca de operações
    # ----------------------------
    def detect_operations(self) -> list[dict[str, Any]]:
        self._ops = [
            DetectedOperation(
                tipo="identidade",
                nome="\\mathrm{E}",
                comentario="Identidade",
            )
        ]

        # inversão
        if self.has_inversion():
            self._ops.append(
                DetectedOperation(
                    tipo="inversao",
                    nome="\\mathrm{i}",
                    comentario="Inversão central pelo ponto (0,0,0)",
                )
            )

        axes = self.candidate_axes()
        normals = self.candidate_plane_normals()

        # rotações próprias
        found_rotation_axes = []
        for axis in axes:
            for n in [2, 3, 4, 5, 6]:
                angle = 360.0 / n
                if self.has_rotation(axis, angle):
                    found_rotation_axes.append((n, axis))
                    nome = self._rotation_name(n, power=1)
                    self._append_unique_op(
                        DetectedOperation(
                            tipo="rotacao",
                            nome=nome,
                            comentario=f"Rotação C{n} em torno de eixo candidato",
                            eixo=axis.round(6).tolist(),
                            angulo=angle,
                        )
                    )

                    # potências relevantes
                    for k in range(2, n):
                        angle_k = k * angle
                        if angle_k >= 360.0 - 1e-9:
                            continue
                        if self.has_rotation(axis, angle_k):
                            self._append_unique_op(
                                DetectedOperation(
                                    tipo="rotacao",
                                    nome=self._rotation_name(n, power=k),
                                    comentario=f"Rotação C{n}^{k} em torno de eixo candidato",
                                    eixo=axis.round(6).tolist(),
                                    angulo=angle_k,
                                )
                            )

        # reflexões
        sigma_count = 1
        for normal in normals:
            if self.has_reflection(normal):
                self._append_unique_op(
                    DetectedOperation(
                        tipo="reflexao",
                        nome=f"\\sigma_{{{sigma_count}}}",
                        comentario="Plano de reflexão detectado",
                        plano_normal=normal.round(6).tolist(),
                    )
                )
                sigma_count += 1

        # impróprias
        for axis in axes:
            for n in [2, 3, 4, 6]:
                angle = 360.0 / n
                if self.has_improper(axis, angle):
                    self._append_unique_op(
                        DetectedOperation(
                            tipo="impropria",
                            nome=self._improper_name(n, power=1),
                            comentario=f"Rotação imprópria S{n} detectada",
                            eixo=axis.round(6).tolist(),
                            angulo=angle,
                            plano_normal=axis.round(6).tolist(),
                        )
                    )

        return [op.to_dict() for op in self._ops]

    def _append_unique_op(self, op: DetectedOperation) -> None:
        for existing in self._ops:
            if existing.tipo != op.tipo:
                continue

            same_name = existing.nome == op.nome

            same_axis = (
                op.eixo is not None
                and existing.eixo is not None
                and (
                    np.linalg.norm(np.asarray(existing.eixo) - np.asarray(op.eixo)) < 1e-3
                    or np.linalg.norm(np.asarray(existing.eixo) + np.asarray(op.eixo)) < 1e-3
                )
            )

            same_plane = (
                op.plano_normal is not None
                and existing.plano_normal is not None
                and (
                    np.linalg.norm(np.asarray(existing.plano_normal) - np.asarray(op.plano_normal)) < 1e-3
                    or np.linalg.norm(np.asarray(existing.plano_normal) + np.asarray(op.plano_normal)) < 1e-3
                )
            )

            if same_name or same_axis or same_plane:
                return

        self._ops.append(op)

    def _count_perpendicular_c2_axes(self, rotations: list[dict], main_axis):
        if main_axis is None:
            return 0

        main_axis = _normalize(main_axis)
        axes = self._axes_from_rotations(rotations)

        perp_axes = []

        for n, axis, op in axes:
            if n != 2:
                continue

            if abs(np.dot(main_axis, axis)) < 5e-2:
                duplicated = False
                for prev in perp_axes:
                    if np.linalg.norm(axis - prev) < 1e-3 or np.linalg.norm(axis + prev) < 1e-3:
                        duplicated = True
                        break
                if not duplicated:
                    perp_axes.append(axis)

        return len(perp_axes)
        
    # ----------------------------
    # Classificação inicial
    # ----------------------------
    def infer_group(self) -> dict[str, Any]:
        ops = self.detect_operations()

        if self.is_linear():
            nome = "D∞h" if self.has_inversion() else "C∞v"
            print(f"[DEBUG DETECTOR] linear=True -> grupo={nome}")
            return self._group_payload(nome, "Molécula linear", ops)

        rotations = [op for op in ops if op["tipo"] == "rotacao"]
        reflections = [op for op in ops if op["tipo"] == "reflexao"]
        impropers = [op for op in ops if op["tipo"] == "impropria"]
        has_i = any(op["tipo"] == "inversao" for op in ops)

        n_main = self._max_rotation_order(rotations)
        main_axis = self._main_axis(rotations)

        sigma_h = self._has_plane_perpendicular_to_axis(reflections, main_axis)
        sigma_v_count = self._count_planes_containing_axis(reflections, main_axis)
        c2_perp_count = self._count_perpendicular_c2_axes(rotations, main_axis)
        sigma_d_count = self._count_dihedral_planes(reflections, main_axis)

        self._log_summary(
            ops=ops,
            rotations=rotations,
            reflections=reflections,
            impropers=impropers,
            has_i=has_i,
            n_main=n_main,
            main_axis=main_axis,
            sigma_h=sigma_h,
            sigma_v_count=sigma_v_count,
            sigma_d_count=sigma_d_count,
            c2_perp_count=c2_perp_count,
        )

        # nenhum eixo próprio principal
        if n_main is None:
            if has_i and not reflections:
                return self._group_payload("Ci", "Inversão sem eixo próprio", ops)
            if reflections and not has_i:
                return self._group_payload("Cs", "Plano de reflexão sem eixo próprio", ops)
            if reflections and has_i:
                return self._group_payload("C2h", "Caso ambíguo inicial com reflexão + inversão", ops)
            return self._group_payload("C1", "Sem eixo próprio detectado", ops)

        # -------------------------
        # Ramo D_n
        # -------------------------
        if c2_perp_count >= max(1, n_main):
            if sigma_h:
                return self._group_payload(f"D{n_main}h", "Eixo principal, C2 perpendiculares e plano horizontal", ops)

            if sigma_d_count >= max(1, n_main):
                return self._group_payload(f"D{n_main}d", "Eixo principal, C2 perpendiculares e planos diagonais", ops)

            return self._group_payload(f"D{n_main}", "Eixo principal com C2 perpendiculares", ops)

        # -------------------------
        # Ramo C_n
        # -------------------------
        if sigma_h:
            return self._group_payload(f"C{n_main}h", "Eixo principal com plano horizontal", ops)

        if sigma_v_count > 0:
            return self._group_payload(f"C{n_main}v", "Eixo principal com planos verticais", ops)

        if len(impropers) > 0:
            # Mantemos simples por enquanto
            return self._group_payload(f"S{n_main}", "Eixo impróprio detectado", ops)

        return self._group_payload(f"C{n_main}", "Apenas eixo principal detectado", ops)

    def _group_payload(self, nome: str, descricao: str, ops: list[dict[str, Any]]) -> dict[str, Any]:
        return {
            "nome": nome,
            "descricao": descricao,
            "ordem": len(ops),
            "operacoes": ops,
            "tolerancia": self.tol,
        }

    # ----------------------------
    # Helpers de classificação
    # ----------------------------
    def _rotation_name(self, n: int, power: int = 1) -> str:
        if power == 1:
            return f"\\mathrm{{C}}_{{{n}}}"
        return f"\\mathrm{{C}}_{{{n}}}^{{{power}}}"

    def _improper_name(self, n: int, power: int = 1) -> str:
        if power == 1:
            return f"\\mathrm{{S}}_{{{n}}}"
        return f"\\mathrm{{S}}_{{{n}}}^{{{power}}}"

    def _rotation_order_from_name(self, nome: str) -> int | None:
        import re
        m = re.search(r"\\mathrm\{C\}_\{(\d+)\}", nome)
        if not m:
            return None
        return int(m.group(1))

    def _max_rotation_order(self, rotations: list[dict[str, Any]]) -> int | None:
        orders = []
        for op in rotations:
            n = self._rotation_order_from_name(op["nome"])
            if n is not None:
                orders.append(n)
        return max(orders) if orders else None

    def _main_axis(self, rotations: list[dict[str, Any]]) -> np.ndarray | None:
        best_axis = None
        best_n = -1
        for op in rotations:
            n = self._rotation_order_from_name(op["nome"])
            if n is None or "eixo" not in op:
                continue
            if n > best_n:
                best_n = n
                best_axis = np.asarray(op["eixo"], dtype=float)
        return _normalize(best_axis) if best_axis is not None else None

    def _has_plane_perpendicular_to_axis(self, reflections: list[dict[str, Any]], axis: np.ndarray | None) -> bool:
        if axis is None:
            return False
        axis = _normalize(axis)
        for op in reflections:
            normal = np.asarray(op.get("plano_normal", [0, 0, 0]), dtype=float)
            normal = _normalize(normal)
            # sigma_h: normal paralela ao eixo principal
            if abs(np.dot(axis, normal)) > 1.0 - 5e-2:
                return True
        return False

    def _count_planes_containing_axis(self, reflections: list[dict[str, Any]], axis: np.ndarray | None) -> int:
        if axis is None:
            return 0
        axis = _normalize(axis)
        count = 0
        for op in reflections:
            normal = np.asarray(op.get("plano_normal", [0, 0, 0]), dtype=float)
            normal = _normalize(normal)
            # plano contém o eixo se normal ⟂ eixo
            if abs(np.dot(axis, normal)) < 5e-2:
                count += 1
        return count
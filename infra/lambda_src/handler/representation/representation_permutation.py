import numpy as np
from .representation import Representation
from .representation_matrix3d import Matrix3DRepresentation
from core.core_molecula import Molecule


def cdist_numpy(A: np.ndarray, B: np.ndarray) -> np.ndarray:
    diff = A[:, None, :] - B[None, :, :]
    return np.sqrt(np.sum(diff * diff, axis=-1))


class PermutationRepresentation(Representation):

    def __init__(self, nome_grupo: str):
        super().__init__(nome_grupo)
        self._dados = {}

    @staticmethod
    def _resolver_atribuicao_por_backtracking(dist_sub, tolerancia):
        """
        Resolve uma atribuição 1-para-1 usando backtracking, minimizando conflitos.
        dist_sub: matriz NxN de distâncias entre átomos transformados e originais
                  de um mesmo elemento químico.
        Retorna uma lista assignment tal que assignment[i] = j.
        """
        n = dist_sub.shape[0]

        # candidatos válidos por linha
        candidatos = []
        for i in range(n):
            js = [j for j in range(n) if dist_sub[i, j] <= tolerancia]
            if not js:
                return None
            # ordena por menor distância
            js.sort(key=lambda j: dist_sub[i, j])
            candidatos.append(js)

        # ordem de exploração: linhas mais restritas primeiro
        ordem = sorted(range(n), key=lambda i: (len(candidatos[i]), min(dist_sub[i, j] for j in candidatos[i])))

        usado = [False] * n
        assignment = [-1] * n

        def bt(k):
            if k == n:
                return True

            i = ordem[k]
            for j in candidatos[i]:
                if usado[j]:
                    continue
                usado[j] = True
                assignment[i] = j
                if bt(k + 1):
                    return True
                assignment[i] = -1
                usado[j] = False

            return False

        ok = bt(0)
        return assignment if ok else None

    @staticmethod
    def _calcular_permutacao(molecule, matriz, tolerancia=1e-2):
        coords_orig = np.array(molecule.coordenadas, dtype=float)

        # centraliza antes de aplicar a operação
        centro = coords_orig.mean(axis=0)
        coords_centradas = coords_orig - centro
        coords_transf = (matriz @ coords_centradas.T).T + centro

        elementos = list(molecule.elementos)
        n = len(coords_orig)
        permutacao = [-1] * n

        # resolve separadamente por elemento químico
        for elem in sorted(set(elementos)):
            idx_orig = [i for i, e in enumerate(elementos) if e == elem]
            idx_transf = [i for i, e in enumerate(elementos) if e == elem]

            A = coords_transf[idx_transf]
            B = coords_orig[idx_orig]
            dist_sub = cdist_numpy(A, B)

            assignment = PermutationRepresentation._resolver_atribuicao_por_backtracking(
                dist_sub, tolerancia
            )

            if assignment is None:
                # diagnóstico melhor
                mins = dist_sub.min(axis=1)
                detalhe = ", ".join(f"{d:.6f}" for d in mins)
                raise ValueError(
                    f"Não foi possível mapear os átomos do elemento {elem} dentro da tolerância {tolerancia}. "
                    f"Menores distâncias por átomo transformado: [{detalhe}]"
                )

            for i_local, j_local in enumerate(assignment):
                i_global = idx_transf[i_local]
                j_global = idx_orig[j_local]
                permutacao[i_global] = j_global + 1  # base-1

        if any(p == -1 for p in permutacao):
            raise ValueError("Permutação incompleta: alguns átomos não foram mapeados.")

        print(f"[DEBUG] elemento={elem}")
        print(f"[DEBUG] idx_transf={idx_transf}")
        print(f"[DEBUG] idx_orig={idx_orig}")
        print(f"[DEBUG] dist_sub=\n{dist_sub}")
        return permutacao

    @classmethod
    def from_matrix3d(cls, rep3d: Matrix3DRepresentation, molecule: Molecule):
        for nome, matriz in rep3d:
            print(f"[DEBUG] tentando operação {nome}")
            perm = cls._calcular_permutacao(molecule, matriz)
            inst.adicionar(nome, perm)
        inst = cls(rep3d.nome_grupo)
        for nome, matriz in rep3d:
            perm = cls._calcular_permutacao(molecule, matriz)
            inst.adicionar(nome, perm)
        return inst

    def get_permutacoes(self) -> dict:
        return self._dados

    def adicionar(self, nome: str, dados: list[int]):
        self._dados[nome] = dados

    def compor(self, a, b):
        return [b[a[i] - 1] for i in range(len(a))]

    def inverso(self, a):
        inv = [0] * len(a)
        for i, val in enumerate(a):
            inv[val - 1] = i + 1
        return inv

    def aplicar(self, nome, vetor):
        perm = self._dados[nome]
        return [vetor[i - 1] for i in perm]

    def conjugar(self, a, b):
        inv_b = self.inverso(b)
        return self.compor(self.compor(b, a), inv_b)

    def nomes(self):
        return list(self._dados.keys())

    def valores(self):
        return list(self._dados.values())

    def __getitem__(self, nome):
        return self._dados[nome]
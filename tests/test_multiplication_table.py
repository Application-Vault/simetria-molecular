import sys
import unittest
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "infra/lambda/handler"))

from analysis.analise_tabela_multiplicacao import TabelaMultiplicacao


class CountingRepresentation:
    def __init__(self, operations):
        self.operations = operations
        self.compositions = 0

    def nomes(self):
        return list(self.operations)

    def __getitem__(self, name):
        return self.operations[name]

    def compor(self, first, second):
        self.compositions += 1
        if isinstance(first, np.ndarray):
            return first @ second
        return [second[value - 1] for value in first]


class MultiplicationTableTests(unittest.TestCase):
    def test_permutations_are_computed_only_once(self):
        representation = CountingRepresentation({"E": [1, 2], "C2": [2, 1]})
        table = TabelaMultiplicacao(representation)
        self.assertEqual(representation.compositions, 4)
        self.assertIs(table.gerar(), table.dados)
        self.assertIs(table.gerar(), table.dados)
        self.assertEqual(representation.compositions, 4)
        self.assertEqual(table.dados["C2"]["C2"]["nome"], "E")
        self.assertEqual(table.dados["E"]["C2"]["permutacao_resultante"], [2, 1])

    def test_matrix_representation_is_preserved(self):
        identity = np.eye(2)
        rotation = -identity
        representation = CountingRepresentation({"E": identity, "C2": rotation})
        table = TabelaMultiplicacao(representation)
        self.assertEqual(table.gerar()["C2"]["C2"]["nome"], "E")
        np.testing.assert_array_equal(table.dados["C2"]["C2"]["permutacao_resultante"], identity)
        self.assertEqual(representation.compositions, 4)

    def test_nonclosed_representation_still_raises(self):
        representation = CountingRepresentation({"C2": [2, 1]})
        with self.assertRaisesRegex(ValueError, "não encontrada"):
            TabelaMultiplicacao(representation)


if __name__ == "__main__":
    unittest.main()
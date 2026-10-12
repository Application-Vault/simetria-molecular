import copy
import sys
import unittest
from pathlib import Path

from pydantic import ValidationError

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "infra/lambda/handler"))

from main_app.main_dto import AnaliseRequest
from render.render_tex import LatexReportGenerator


class ReportLanguageTests(unittest.TestCase):
    def setUp(self):
        self.metadata = {
            "sistema": "Molecular",
            "molecula": "Fe(III) tetrathiolate",
            "grupo": "S6",
            "ordem": 6,
            "uuid": "REPORT-I18N",
            "data": "2026-10-12",
        }
        self.result = {
            "permutacoes": {"E": [1, 2]},
            "operacoes_multiplicacao": {
                "E": {"E": {"nome": "E", "permutacao_op2": [1, 2], "permutacao_resultante": [1, 2]}}
            },
            "operacoes_conjugacao": {"E": {"E": {"resultado": "E", "detalhe": {"hgh⁻¹": "E"}}}},
            "classes_conjugacao": {"E": ["E"]},
            "tempo_execucao": "0.01s",
        }

    def test_default_report_is_portuguese(self):
        report = LatexReportGenerator(self.metadata, self.result).gerar_documento()
        self.assertIn(r"\section{Permutações Básicas}", report)
        self.assertIn(r"\renewcommand{\contentsname}{Sumário}", report)
        self.assertNotIn("fontset=fandol", report)

    def test_system_header_preserves_textbf_command(self):
        for language, label in (("pt", "Sistema"), ("en", "System"), ("zh", "系统")):
            with self.subTest(language=language):
                report = LatexReportGenerator(self.metadata, self.result, language).gerar_documento()
                self.assertIn(chr(92) + "textbf{" + label + " Molecular}", report)
                self.assertNotIn(chr(9) + "extbf", report)

    def test_group_subscripts_are_inside_math_mode(self):
        generator = LatexReportGenerator(self.metadata, self.result)
        self.assertEqual(generator._latex_group_name("O_h"), "$O_h$")
        self.assertEqual(generator._latex_group_name("$O_h$"), "$O_h$")
        self.assertEqual(generator._latex_group_name("C∞v"), "$C" + chr(92) + "infty{}v$")
        self.assertEqual(generator._latex_group_name(""), "")
        for language in ("pt", "en", "zh"):
            metadata = {**self.metadata, "grupo": "O_h"}
            report = LatexReportGenerator(metadata, self.result, language).gerar_documento()
            self.assertIn(chr(92) + "textbf{$O_h$}", report)

    def test_all_sections_are_translated(self):
        expected = {
            "en": ["Basic Permutations", "Multiplication Operations", "Detailed Multiplication Operations", "Conjugation Table", "Grouping into Conjugacy Classes", "Conjugations of", "Execution Time", "Contents"],
            "zh": ["基本置换", "乘法运算", "乘法运算详情", "共轭表", "共轭类分组", "共轭运算：", "执行时间", "目录"],
        }
        for language, labels in expected.items():
            with self.subTest(language=language):
                report = LatexReportGenerator(self.metadata, self.result, language).gerar_documento()
                for label in labels:
                    self.assertIn(label, report)
                self.assertNotIn("Permutações Básicas", report)
                self.assertEqual("fontset=fandol" in report, language == "zh")

    def test_scientific_data_and_tables_are_preserved(self):
        original = copy.deepcopy(self.result)
        reference = LatexReportGenerator(self.metadata, self.result)
        for language in ("pt", "en", "zh"):
            generator = LatexReportGenerator(self.metadata, self.result, language)
            report = generator.gerar_documento()
            for field in ("molecula", "grupo", "uuid", "data"):
                self.assertIn(self.metadata[field], report)
            self.assertEqual(generator._formatar_permutacoes(self.result["permutacoes"]), reference._formatar_permutacoes(self.result["permutacoes"]))
            self.assertEqual(generator._formatar_tabela_multiplicacao(self.result["operacoes_multiplicacao"]), reference._formatar_tabela_multiplicacao(self.result["operacoes_multiplicacao"]))
            self.assertEqual(generator._formatar_tabela_conjugacao(self.result["operacoes_conjugacao"]), reference._formatar_tabela_conjugacao(self.result["operacoes_conjugacao"]))
        self.assertEqual(self.result, original)

    def test_request_language_is_optional_and_validated(self):
        payload = {"render": {"tipo": "texto", "formato": "tex"}, "analises": {"grupo": True}}
        self.assertEqual(AnaliseRequest(**payload).idioma, "pt")
        for language in ("pt", "en", "zh"):
            self.assertEqual(AnaliseRequest(**payload, idioma=language).idioma, language)
        with self.assertRaises(ValidationError):
            AnaliseRequest(**payload, idioma="invalid")


if __name__ == "__main__":
    unittest.main()
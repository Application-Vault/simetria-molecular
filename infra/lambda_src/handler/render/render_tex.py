import re


class LatexReportGenerator:
    def __init__(self, metadata, resultado):
        self.metadata = metadata
        self.resultado = resultado

    def gerar_documento(self):
        blocos = []

        if "permutacoes" in self.resultado:
            blocos.append(
                r"""
\section{Permutações Básicas}
\[
%s
\]
"""
                % self._formatar_permutacoes(self.resultado["permutacoes"])
            )

        if "operacoes_multiplicacao" in self.resultado:
            blocos.append(
                r"""
\section{Operações de Multiplicação}
\subsection{Tabela de Multiplicação}
\begin{adjustbox}{max width=\linewidth, angle=90, center}
$
%s
$
\end{adjustbox}
"""
                % self._formatar_tabela_multiplicacao(self.resultado["operacoes_multiplicacao"])
            )

            blocos.append(
                r"""
\subsection{Operações de Multiplicação Detalhadas}
\begin{longtable}{r l l l}
%s
\end{longtable}
"""
                % self._formatar_operacoes_multiplicacao(self.resultado["operacoes_multiplicacao"])
            )

        if "operacoes_conjugacao" in self.resultado:
            classes = self._extrair_classes_de_operacoes(self.resultado["operacoes_conjugacao"])

            blocos.append(
                r"""
\section{Operações de Conjugação}
\subsection{Tabela de Conjugação}
\begin{adjustbox}{max width=\linewidth, angle=90, center}
$
%s
$
\end{adjustbox}
"""
                % self._formatar_tabela_conjugacao(self.resultado["operacoes_conjugacao"])
            )

            blocos.append(
                r"""
\subsection{Operações de Conjugação Detalhadas}
%s
"""
                % self._formatar_operacoes_conjugacao(self.resultado["operacoes_conjugacao"])
            )

            blocos.append(
                r"""
\subsection{Agrupamento em Classes de Conjugação}
\begin{itemize}
%s
\end{itemize}
"""
                % "\n".join(
                    rf"\item ${self._latex_math_op(classe)}$: "
                    + ", ".join(rf"${self._latex_math_op(op)}$" for op in ops)
                    for classe, ops in classes.items()
                )
            )

        sistema = self._latex_escape_text(str(self.metadata.get("sistema", "")))
        molecula = self._latex_escape_text(str(self.metadata.get("molecula", "")))
        grupo = self._latex_escape_text(str(self.metadata.get("grupo", "")))
        ordem = self._latex_escape_text(str(self.metadata.get("ordem", "")))
        data = self._latex_escape_text(str(self.metadata.get("data", "")))
        uuid = self._latex_escape_text(str(self.metadata.get("uuid", "")))
        tempo_exec = self._latex_escape_text(str(self.resultado.get("tempo_execucao", "")))

        return fr"""\documentclass[a4paper,12pt]{{article}}
\usepackage{{datetime2}}
\usepackage{{graphicx}}
\usepackage[utf8]{{inputenc}}
\usepackage{{fancyhdr}}
\usepackage{{geometry}}
\usepackage{{amsmath}}
\usepackage{{array}}
\usepackage{{longtable}}
\usepackage{{lastpage}}
\usepackage[hidelinks]{{hyperref}}
\usepackage{{adjustbox}}
\usepackage{{lscape}}

\geometry{{left=1cm, right=1cm, top=2.5cm, bottom=2.5cm}}
\pagestyle{{fancy}}
\fancyhf{{}}

\setlength{{\headheight}}{{42pt}}
\setlength{{\headsep}}{{2em}}

\fancyhead[L]{{\textbf{{Análise de Simetria}} \\
\textbf{{Sistema {sistema}}} \\
Tempo de Execução: \textbf{{{tempo_exec}}}}}

\fancyhead[C]{{Molécula: \textbf{{{molecula}}} \\
Grupo: \textbf{{{grupo}}} \\
Ordem: \textbf{{{ordem}}}}}

\fancyhead[R]{{{data} \\
Relatório: \textbf{{{uuid}}} \\
Página \thepage\ de \pageref{{LastPage}}}}

\fancyfoot[L]{{\scriptsize {{ \textcopyright}} 2026 application-vault.github.io/simetria-molecular}}

\begin{{document}}

\tableofcontents
\newpage

{''.join(blocos)}
\end{{document}}
"""

    # -------------------------
    # FORMATADORES
    # -------------------------

    def _formatar_permutacoes(self, permutacoes: dict) -> str:
        linhas = [r"\begin{array}{r@{\,:\ }l}"]
        for nome, lista in permutacoes.items():
            nome_tex = self._latex_math_op(nome)
            lista_tex = rf"\text{{{self._latex_escape_text(str(lista))}}}"
            linhas.append(rf"{nome_tex} & {lista_tex} \\")
        linhas.append(r"\end{array}")
        return "\n".join(linhas)

    def _formatar_tabela_multiplicacao(self, tabela: dict) -> str:
        chaves = list(tabela.keys())
        linhas = []

        linhas.append(r"\begin{array}{c|" + ("c" * len(chaves)) + r"}")

        header = " & " + " & ".join(self._latex_math_op(op) for op in chaves) + r" \\ \hline"
        linhas.append(header)

        for op1, linha in tabela.items():
            valores = [linha[op2]["nome"] for op2 in chaves]

            op1_tex = self._latex_math_op(op1)
            valores_tex = " & ".join(self._latex_math_op(v) for v in valores)

            linhas.append(op1_tex + " & " + valores_tex + r" \\")

        linhas.append(r"\end{array}")
        return "\n".join(linhas)

    def _formatar_operacoes_multiplicacao(self, operacoes: dict) -> str:
        linhas = []

        for op1, linha in operacoes.items():
            for op2, info in linha.items():
                perm2 = str(info.get("permutacao_op2", ""))
                perm_result = str(info.get("permutacao_resultante", ""))
                resultado = str(info.get("nome", ""))

                op1_tex = self._latex_math_op(op1)
                op2_tex = self._latex_math_op(op2)
                resultado_tex = self._latex_math_op(resultado)

                perm2_tex = self._latex_perm_to_math_text(perm2)
                perm_result_tex = self._latex_perm_to_math_text(perm_result)

                linhas.append(
                    rf"\makebox[3.3cm][r]{{$ {op1_tex} \circ {op2_tex} $}}"
                    rf" & $= {op1_tex} \circ {perm2_tex}$"
                    rf" & $= {perm_result_tex}$"
                    rf" & \makebox[2.3cm][l]{{$= {resultado_tex}$}} \\"
                )

        return "\n".join(linhas)

    def _formatar_operacoes_conjugacao(self, operacoes: dict) -> str:
        linhas = []

        for g, conjugacoes in operacoes.items():
            g_tex = self._latex_math_op(g)

            linhas.append(rf"\subsection*{{Conjugações de ${g_tex}$}}")
            linhas.append(r"\begin{longtable}{r l l l}")

            for h, info in conjugacoes.items():
                h_tex = self._latex_math_op(h)
                detalhe = info.get("detalhe", {}) or {}

                hgh_inv = detalhe.get("hgh⁻¹") or detalhe.get("hgh-1") or detalhe.get("hgh^-1") or ""
                resultado = str(info.get("resultado", ""))

                hgh_tex = self._latex_math_op(hgh_inv) if hgh_inv else r"\text{---}"
                resultado_tex = self._latex_math_op(resultado) if resultado else r"\text{---}"

                linhas.append(
                    rf"\makebox[3.5cm][r]{{$ {h_tex} \circ {g_tex} \circ {h_tex}^{{-1}} $}}"
                    rf" & $= {hgh_tex}$"
                    rf" & $= {resultado_tex}$"
                    rf" & \\"
                )

            linhas.append(r"\end{longtable}")

        return "\n".join(linhas)

    def _formatar_tabela_conjugacao(self, operacoes: dict) -> str:
        nomes = list(operacoes.keys())
        linhas = []

        linhas.append(r"\begin{array}{c|" + ("c" * len(nomes)) + r"}")
        linhas.append(
            " & " + " & ".join(self._latex_math_op(n) for n in nomes) + r" \\ \hline"
        )

        for g, resultados in operacoes.items():
            row = [self._latex_math_op(g)]
            for h in nomes:
                val = (resultados.get(h) or {}).get("resultado", "")
                row.append(self._latex_math_op(val) if val else r"\text{---}")
            linhas.append(" & ".join(row) + r" \\")

        linhas.append(r"\end{array}")
        return "\n".join(linhas)

    # -------------------------
    # HELPERS
    # -------------------------

    def _extrair_classes_de_operacoes(self, operacoes_conjugacao: dict) -> dict:
        """
        Agrupa operações em classes de conjugação.
        A chave da classe é escolhida como o primeiro elemento encontrado
        da classe, preservando a ordem do dicionário de entrada.
        """
        classes = {}
        visitados = set()

        for g, conjugacoes in operacoes_conjugacao.items():
            if g in visitados:
                continue

            classe = set([g])

            for _, info in conjugacoes.items():
                resultado = (info or {}).get("resultado")
                if resultado:
                    classe.add(str(resultado))

            classe_ordenada = [op for op in operacoes_conjugacao.keys() if op in classe]

            for op in classe_ordenada:
                visitados.add(op)

            classes[g] = classe_ordenada

        return classes

    @staticmethod
    def latex_safe(op: str) -> str:
        return re.sub(
            r"(\\mathrm\{[A-Za-z]+\})_\{([^\}]+)\}\^\{([^\}]+)\}",
            r"\1_{\2}^{\3}",
            op,
        )

    def _latex_math_op(self, op: str) -> str:
        return self.latex_safe(str(op))

    def _latex_perm_to_math_text(self, s: str) -> str:
        return rf"\text{{{self._latex_escape_text(str(s))}}}"

    def _latex_escape_text(self, s: str) -> str:
        return (
            str(s)
            .replace("\\", r"\textbackslash{}")
            .replace("&", r"\&")
            .replace("%", r"\%")
            .replace("$", r"\$")
            .replace("#", r"\#")
            .replace("_", r"\_")
            .replace("{", r"\{")
            .replace("}", r"\}")
            .replace("~", r"\textasciitilde{}")
            .replace("^", r"\textasciicircum{}")
        )
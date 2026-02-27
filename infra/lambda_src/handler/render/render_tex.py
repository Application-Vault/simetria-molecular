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

# latex_generator.py
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
\[
%s
\]
\end{adjustbox}
"""
                % self._formatar_tabela_multiplicacao(self.resultado["operacoes_multiplicacao"])
            )

            blocos.append(
                r"""
\subsection{Operações de Multiplicação Detalhadas}
\begin{longtable}{>{$}r<{$} >{$}l<{$} >{$}l<{$}}
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
\[
%s
\]
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

            # Aqui eu deixo como TEXTO (não $...$), porque os nomes podem ter "_" etc.
            # Se quiser matemático, dá pra trocar por \ensuremath{...} com escape cuidadoso.
            blocos.append(
                r"""
\subsection{Agrupamento em Classes de Conjugação}
\begin{itemize}
%s
\end{itemize}
"""
                % "\n".join(
                    rf"\item \textbf{{{self._latex_escape_text(classe)}}}: "
                    + ", ".join(rf"\texttt{{{self._latex_escape_text(op)}}}" for op in ops)
                    for classe, ops in classes.items()
                )
            )

        # metadados em texto (podem ter underscore etc.)
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
\usepackage{{longtable}}
\usepackage{{lastpage}}
\usepackage[hidelinks]{{hyperref}}
\usepackage{{adjustbox}}
\usepackage{{lscape}}

\geometry{{left=1cm, right=1cm, top=2.5cm, bottom=2.5cm}}
\pagestyle{{fancy}}
\fancyhf{{}}

% fancyhdr estava avisando headheight; já deixo o recomendado:
\setlength{{\headheight}}{{42pt}}
\setlength{{\headsep}}{{2em}}

% Cabeçalho (texto)
\fancyhead[L]{{\textbf{{Análise de Simetria}} \\
\textbf{{Sistema {sistema}}} \\
Tempo de Execução: \textbf{{{tempo_exec}}}}}

\fancyhead[C]{{Molécula: \textbf{{{molecula}}} \\
Grupo: \textbf{{{grupo}}} \\
Ordem: \textbf{{{ordem}}}}}

\fancyhead[R]{{{data} \\
Relatório: \textbf{{{uuid}}} \\
Página \thepage\ de \pageref{{LastPage}}}}

\fancyfoot[L]{{\scriptsize {{\tiny \textcopyright}} naavilam.github.io/simetria-molecular contact@chanah.dev}}

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
            nome_tex = rf"\text{{{self._latex_escape_text(str(nome))}}}"
            lista_tex = rf"\text{{{self._latex_escape_text(str(lista))}}}"
            linhas.append(rf"{nome_tex} & {lista_tex} \\")
        linhas.append(r"\end{array}")
        return "\n".join(linhas)

    def _formatar_tabela_multiplicacao(self, tabela: dict) -> str:
        chaves = list(tabela.keys())
        linhas = []

        linhas.append(r"\begin{array}{c|" + ("c" * len(chaves)) + r"}")

        header = " & " + " & ".join(rf"\text{{{self._latex_escape_text(str(op))}}}" for op in chaves) + r" \\ \hline"
        linhas.append(header)

        for op1, linha in tabela.items():
            valores = [linha[op2]["nome"] for op2 in chaves]

            op1_tex = rf"\text{{{self._latex_escape_text(str(op1))}}}"
            valores_tex = " & ".join(rf"\text{{{self._latex_escape_text(str(v))}}}" for v in valores)

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

                op1e = self._latex_escape_text(str(op1))
                op2e = self._latex_escape_text(str(op2))

                # permutações/resultados podem conter caracteres especiais, então escapamos como texto
                perm2e = self._latex_escape_text(perm2)
                permrese = self._latex_escape_text(perm_result)
                rese = self._latex_escape_text(resultado)

                linhas.append(
                    rf"\makebox[3.3cm][r]{{$\mathrm{{{op1e}}} \circ \mathrm{{{op2e}}}$}} &="
                    rf" \text{{{op1e}}} \circ \text{{{perm2e}}} &="
                    rf" \text{{{permrese}}} &="
                    rf" \makebox[2.3cm][l]{{\text{{{rese}}}}} \\"
                )
        return "\n".join(linhas)

    def _formatar_operacoes_conjugacao(self, operacoes: dict) -> str:
        linhas = []
        for g, conjugacoes in operacoes.items():
            ge = self._latex_escape_text(str(g))
            linhas.append(rf"\subsection*{{Conjugações de \texttt{{{ge}}}}}")

            for h, info in conjugacoes.items():
                he = self._latex_escape_text(str(h))
                detalhe = info.get("detalhe", {}) or {}

                # cuidado com a chave hgh⁻¹ (tem caractere unicode)
                hgh_inv = detalhe.get("hgh⁻¹") or detalhe.get("hgh-1") or detalhe.get("hgh^-1") or ""

                hgh_e = self._latex_escape_text(str(hgh_inv))
                res_e = self._latex_escape_text(str(info.get("resultado", "")))

                # Tudo como texto para não quebrar com underscores etc.
                linhas.append(
                    rf"\texttt{{{he}}} $\circ$ \texttt{{{ge}}} $\circ$ \texttt{{{he}}}^{{-1}} "
                    rf"$=$ \texttt{{{hgh_e}}} $=$ \texttt{{{res_e}}} \\"
                )
        return "\n".join(linhas)

    def _formatar_tabela_conjugacao(self, operacoes: dict) -> str:
        nomes = list(operacoes.keys())
        linhas = []

        linhas.append(r"\begin{array}{c|" + ("c" * len(nomes)) + r"}")
        linhas.append(
            " & " + " & ".join(rf"\text{{{self._latex_escape_text(str(n))}}}" for n in nomes) + r" \\ \hline"
        )

        for g, resultados in operacoes.items():
            row = [rf"\text{{{self._latex_escape_text(str(g))}}}"]
            for h in nomes:
                val = (resultados.get(h) or {}).get("resultado", "")
                row.append(rf"\text{{{self._latex_escape_text(str(val))}}}")
            linhas.append(" & ".join(row) + r" \\")
        linhas.append(r"\end{array}")
        return "\n".join(linhas)

    # -------------------------
    # HELPERS
    # -------------------------

    @staticmethod
    def latex_safe(op: str) -> str:
        """
        Corrige superscript/subscript duplos como \mathrm{C}_{2}^{(a)} para evitar erro de compilação LaTeX.
        """
        return re.sub(
            r"(\\mathrm\{[A-Za-z]+\})_\{([^\}]+)\}\^\{([^\}]+)\}",
            r"\1_{\2}^{\3}",
            op,
        )

    def _latex_escape_text(self, s: str) -> str:
        # escape bem conservador pra TEX (modo texto via \text{} / \texttt{})
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
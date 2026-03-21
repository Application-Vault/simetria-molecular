# render/render_pdf.py
import os
import subprocess
from pathlib import Path
from typing import Dict, Any

from render.render_tex import LatexReportGenerator


class PdfReportGenerator:
    def __init__(self, metadata: Dict[str, Any], resultado: Dict[str, Any], tectonic_path: str = None):
        self.metadata = metadata
        self.resultado = resultado
        self.tectonic_path = tectonic_path or "/var/task/bin/tectonic"  # dentro do zip

    def gerar_pdf(self) -> bytes:
        # 1) gera o TEX "lindo"
        tex_str = LatexReportGenerator(self.metadata, self.resultado).gerar_documento()

        # 2) escreve em /tmp e compila
        uid = self.metadata.get("uuid", "SIM")
        workdir = Path(f"/tmp/pdf_{uid}")
        workdir.mkdir(parents=True, exist_ok=True)

        tex_path = workdir / "report.tex"
        tex_path.write_text(tex_str, encoding="utf-8")

        pdf_path = workdir / "report.pdf"

        cmd = [
            self.tectonic_path,
            str(tex_path),
            "--outdir", str(workdir),
            "--print",
            "--synctex",
            "--keep-logs",
        ]

        print("[PDF] Running:", " ".join(cmd))

        # IMPORTANT: Lambda filesystem é read-only fora de /tmp
        env = os.environ.copy()
        env["HOME"] = "/tmp"
        env["XDG_CACHE_HOME"] = "/tmp"

        proc = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=env,
        )

        print("[PDF] returncode:", proc.returncode)
        if proc.stdout:
            print("[PDF] stdout:", proc.stdout.decode("utf-8", errors="replace")[:2000])
        if proc.stderr:
            print("[PDF] stderr:", proc.stderr.decode("utf-8", errors="replace")[:2000])

        if proc.returncode != 0 or not pdf_path.exists():
            raise RuntimeError("Falha ao gerar PDF via tectonic. Veja logs acima.")

        return pdf_path.read_bytes()
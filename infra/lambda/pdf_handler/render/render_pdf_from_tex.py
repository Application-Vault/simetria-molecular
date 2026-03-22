import os
import subprocess
from pathlib import Path


class PdfFromTexGenerator:
    def __init__(self, tex_str: str, tectonic_path: str = None):
        self.tex_str = tex_str
        self.tectonic_path = tectonic_path or "/var/task/bin/tectonic"

    def gerar_pdf(self) -> bytes:
        workdir = Path("/tmp/pdf_job")
        workdir.mkdir(parents=True, exist_ok=True)

        tex_path = workdir / "report.tex"
        pdf_path = workdir / "report.pdf"

        tex_path.write_text(self.tex_str, encoding="utf-8")

        print("[PDF] TEX salvo em:", tex_path)

        cmd = [
            self.tectonic_path,
            str(tex_path),
            "--outdir", str(workdir),
            "--keep-logs",
        ]

        print("[PDF] Running:", " ".join(cmd))

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
            raise RuntimeError("Falha ao gerar PDF via tectonic.")

        print("[PDF] PDF gerado com sucesso!")

        return pdf_path.read_bytes()
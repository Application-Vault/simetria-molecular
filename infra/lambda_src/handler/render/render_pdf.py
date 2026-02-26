# render/render_pdf.py
import os
import subprocess

class PdfReportGenerator:
    def __init__(self, tex_str: str, uid: str):
        self.tex_str = tex_str
        self.uid = uid

    def gerar_pdf(self) -> bytes:
        workdir = f"/tmp/latex_{self.uid}"
        os.makedirs(workdir, exist_ok=True)

        tex_path = os.path.join(workdir, f"{self.uid}.tex")
        with open(tex_path, "w", encoding="utf-8") as f:
            f.write(self.tex_str)

        # cache do tectonic no /tmp
        env = dict(os.environ)
        env["TECTONIC_CACHE_DIR"] = os.path.join(workdir, "tectonic_cache")

        # IMPORTANTE: binário tectonic junto no pacote
        # ex: /var/task/bin/tectonic
        tectonic_bin = "/var/task/bin/tectonic"

        cmd = [
            tectonic_bin,
            "-X", "compile",
            "--outdir", workdir,
            tex_path,
        ]

        res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env)

        if res.returncode != 0:
            raise RuntimeError(
                "Falha compilando PDF via tectonic.\n"
                f"STDOUT:\n{res.stdout.decode(errors='replace')}\n"
                f"STDERR:\n{res.stderr.decode(errors='replace')}\n"
            )

        pdf_path = os.path.join(workdir, f"{self.uid}.pdf")
        with open(pdf_path, "rb") as f:
            return f.read()
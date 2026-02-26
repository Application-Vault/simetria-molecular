import os, uuid, base64
from render.render_tipo import RenderTipo
from engine_analyzer.molecule_symmetry_app import MoleculeSymmetryApp
from .dto import AnaliseRequest

def processar_analise_bytes(mol_bytes: bytes, data: AnaliseRequest):
    temp_id = f"SIM{uuid.uuid4().hex[:6].upper()}"
    workdir = f"/tmp/analise_{temp_id}"
    os.makedirs(workdir, exist_ok=True)

    mol_str = mol_bytes.decode("utf-8", errors="replace")

    app = (
        MoleculeSymmetryApp(mol_str)
        .config(data.analises)
        .config(data.render)
        .config(temp_id)
    )

    output = app.run()

    # devolve no formato “API Gateway”
    if data.render.formato == RenderTipo.TEX:
        filename = f"{temp_id}.tex"
        return _resp_file_text(output, filename, "application/x-tex")

    if data.render.formato == RenderTipo.PDF:
        filename = f"{temp_id}.pdf"
        return _resp_file_bytes(output, filename, "application/pdf")

    # outros tipos por enquanto como texto
    return _resp_text(str(output), "text/plain; charset=utf-8")


def _resp_text(text: str, content_type: str):
    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": content_type,
            "Access-Control-Allow-Origin": "https://application-vault.github.io",
        },
        "body": text,
    }

def _resp_file_text(text: str, filename: str, content_type: str):
    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": content_type,
            "Content-Disposition": f'attachment; filename="{filename}"',
            "Access-Control-Allow-Origin": "https://application-vault.github.io",
        },
        "body": text,
    }

def _resp_file_bytes(blob: bytes, filename: str, content_type: str):
    return {
        "statusCode": 200,
        "isBase64Encoded": True,
        "headers": {
            "Content-Type": content_type,
            "Content-Disposition": f'attachment; filename="{filename}"',
            "Access-Control-Allow-Origin": "https://application-vault.github.io",
        },
        "body": base64.b64encode(blob).decode("ascii"),
    }
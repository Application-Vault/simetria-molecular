import json
import base64
from pathlib import Path
from email.parser import BytesParser
from email.policy import default

from main_app.main_controller import processar_analise_bytes
from main_app.main_dto import AnaliseRequest

ALLOWED_ORIGIN = "https://application-vault.github.io"
MOLECULAS_DIR = Path("static/moleculas")


def handler(event, context):
    path = event.get("rawPath", "")
    method = event.get("requestContext", {}).get("http", {}).get("method")

    # --------------------------
    # GET /api/moleculas
    # --------------------------
    if method == "GET" and path == "/api/moleculas":
        try:
            moleculas = []

            if MOLECULAS_DIR.exists():
                for arquivo in sorted(MOLECULAS_DIR.glob("*.xyz")):
                    stem = arquivo.stem
                    moleculas.append(
                        {
                            "id": stem,
                            "label": stem.replace("_", " ").replace("-", " ").title(),
                            "filename": arquivo.name,
                        }
                    )

            return _resp_json({"moleculas": moleculas}, 200)

        except Exception as e:
            return _resp_json(
                {"error": "Erro ao listar moléculas", "detail": str(e)},
                500,
            )

    # --------------------------
    # GET /api/molecula/{nome}
    # --------------------------
    if method == "GET" and path.startswith("/api/molecula/"):
        nome = path.split("/")[-1]

        try:
            arquivo = MOLECULAS_DIR / f"{nome}.xyz"
            with open(arquivo, "r", encoding="utf-8") as f:
                return _resp_text(f.read(), "text/plain; charset=utf-8")

        except FileNotFoundError:
            return _resp_json(
                {"detail": f"Molécula '{nome}' não encontrada"},
                404,
            )

    # --------------------------
    # POST /api/analise
    # --------------------------
    if method == "POST" and path == "/api/analise":
        headers = event.get("headers") or {}
        content_type = headers.get("content-type") or headers.get("Content-Type")

        if not content_type:
            return _resp_json({"error": "Missing Content-Type"}, 400)

        body = event.get("body") or ""
        if event.get("isBase64Encoded"):
            body_bytes = base64.b64decode(body)
        else:
            body_bytes = body.encode("utf-8")

        msg = BytesParser(policy=default).parsebytes(
            b"Content-Type: " + content_type.encode() + b"\n\n" + body_bytes
        )

        molecula_bytes = None
        molecula_filename = None
        payload_json = None

        for part in msg.iter_parts():
            name = part.get_param("name", header="content-disposition")

            if name == "molecula":
                molecula_bytes = part.get_payload(decode=True)
                molecula_filename = part.get_filename() or "molecula.xyz"

            elif name == "payload":
                payload_json = part.get_payload(decode=True).decode(
                    "utf-8", errors="replace"
                )

        if not molecula_bytes or not payload_json:
            return _resp_json({"error": "Payload inválido"}, 400)

        data = AnaliseRequest.parse_raw(payload_json)
        data_dict = processar_analise_bytes(molecula_bytes, molecula_filename, data)

        return _resp_json(
            data_dict,
            200,
            headers={
                "Access-Control-Expose-Headers": "Content-Disposition,Content-Type",
            },
        )

    return _resp_json({"error": "Not Found"}, 404)


def _cors_headers():
    return {
        "Access-Control-Allow-Origin": ALLOWED_ORIGIN,
    }


def _resp_text(text, content_type):
    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": content_type,
            **_cors_headers(),
        },
        "body": text,
    }


def _resp_json(data: dict, status: int = 200, headers: dict | None = None):
    h = {
        "Content-Type": "application/json; charset=utf-8",
        **_cors_headers(),
    }
    if headers:
        h.update(headers)

    return {
        "statusCode": status,
        "headers": h,
        "body": json.dumps(data, ensure_ascii=False),
    }
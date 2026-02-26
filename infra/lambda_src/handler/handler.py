import json
import base64
from email.parser import BytesParser
from email.policy import default

from app.controller.controller import processar_analise_bytes
from app.dto.dto import AnaliseRequest


def handler(event, context):

    path = event.get("rawPath", "")
    method = event.get("requestContext", {}).get("http", {}).get("method")

    # --------------------------
    # GET /api/molecula/{nome}
    # --------------------------
    if method == "GET" and path.startswith("/api/molecula/"):
        nome = path.split("/")[-1]
        try:
            with open(f"static/moleculas/{nome}.xyz", "r") as f:
                return _resp_text(f.read(), "text/plain")
        except FileNotFoundError:
            return _resp_json({"detail": f"Molécula '{nome}' não encontrada"}, 404)

    # --------------------------
    # GET /api/analises/
    # --------------------------
    if method == "GET" and path == "/api/analises/":
        return _resp_json({"status": "ok"}, 200)

    # --------------------------
    # POST /api/analise
    # --------------------------
    if method == "POST" and path == "/api/analise":

        content_type = event["headers"].get("content-type") or event["headers"].get("Content-Type")

        body = event["body"]
        if event.get("isBase64Encoded"):
            body = base64.b64decode(body)
        else:
            body = body.encode()

        # parse multipart
        msg = BytesParser(policy=default).parsebytes(
            b"Content-Type: " + content_type.encode() + b"\n\n" + body
        )

        molecula_bytes = None
        payload_json = None

        for part in msg.iter_parts():
            name = part.get_param("name", header="content-disposition")
            if name == "molecula":
                molecula_bytes = part.get_payload(decode=True)
            elif name == "payload":
                payload_json = part.get_payload(decode=True).decode()

        if not molecula_bytes or not payload_json:
            return _resp_json({"error": "Payload inválido"}, 400)

        data = AnaliseRequest.parse_raw(payload_json)

        return processar_analise_bytes(molecula_bytes, data)

    return _resp_json({"error": "Not Found"}, 404)


# --------------------------
# Helpers
# --------------------------

def _resp_text(text, content_type):
    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": content_type,
            "Access-Control-Allow-Origin": "https://application-vault.github.io",
        },
        "body": text,
    }

def _resp_json(obj, status=200):
    return {
        "statusCode": status,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "https://application-vault.github.io",
        },
        "body": json.dumps(obj),
    }
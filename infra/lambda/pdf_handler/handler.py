import json
import base64

from render.render_pdf_from_tex import PdfFromTexGenerator


def response(status, body):
    return {
        "statusCode": status,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",  # ajuste depois se quiser restringir
            "Access-Control-Allow-Headers": "content-type",
            "Access-Control-Allow-Methods": "POST,OPTIONS",
        },
        "body": json.dumps(body, ensure_ascii=False),
    }


def handler(event, context):
    try:
        method = event.get("requestContext", {}).get("http", {}).get("method", "")

        # CORS preflight
        if method == "OPTIONS":
            return response(200, {"ok": True})

        body = event.get("body") or "{}"

        if event.get("isBase64Encoded"):
            body = base64.b64decode(body).decode("utf-8")

        data = json.loads(body)

        tex = data.get("tex", "")

        if not tex.strip():
            raise ValueError("Campo 'tex' vazio.")

        print("[PDF] Recebido TEX com tamanho:", len(tex))

        pdf_bytes = PdfFromTexGenerator(tex).gerar_pdf()

        pdf_base64 = base64.b64encode(pdf_bytes).decode("utf-8")

        return response(200, {
            "ok": True,
            "pdf_base64": pdf_base64,
            "filename": "report.pdf",
        })

    except Exception as e:
        print("[PDF][ERROR]", str(e))
        return response(400, {
            "ok": False,
            "error": str(e),
        })
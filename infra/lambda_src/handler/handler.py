import json
import base64

def build_response(status, body, content_type="application/json"):
    return {
        "statusCode": status,
        "headers": {
            "Content-Type": content_type,
            "Access-Control-Allow-Origin": "*"
        },
        "body": body if isinstance(body, str) else json.dumps(body)
    }

def handler(event, context):
    print("EVENT RECEIVED:")
    print(json.dumps(event))

    path = event.get("rawPath", "")
    method = event.get("requestContext", {}).get("http", {}).get("method")

    # -------------------------
    # GET /api/molecula/{nome}
    # -------------------------
    if path.startswith("/api/molecula/") and method == "GET":
        nome = path.split("/")[-1]
        print(f"Requested molecule: {nome}")
        return build_response(200, "🙂")

    # -------------------------
    # POST /api/analise
    # -------------------------
    if path == "/api/analise" and method == "POST":
        body = event.get("body")

        if event.get("isBase64Encoded"):
            body = base64.b64decode(body).decode()

        print("Payload received:")
        print(body)

        return build_response(200, "🙂")

    # -------------------------
    # GET /api/analises/
    # -------------------------
    if path == "/api/analises/" and method == "GET":
        return build_response(200, "🙂")

    return build_response(404, {"detail": "Not found"})

    
import json
import base64
import logging
import os
import re
import time
import uuid

import boto3
from botocore.exceptions import ClientError

from render.render_pdf_from_tex import PdfFromTexGenerator

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
s3 = None
lambda_client = None
MAX_TEX_BYTES = 2 * 1024 * 1024
JOB_LIFETIME_SECONDS = 900


def response(status, body, extra_headers=None):
    headers = {
        "Content-Type": "application/json",
        "Access-Control-Allow-Origin": os.environ.get("CORS_ORIGIN", "*"),
        "Access-Control-Allow-Headers": "content-type",
        "Access-Control-Allow-Methods": "GET,POST,OPTIONS",
        "Cache-Control": "no-store",
    }
    if extra_headers:
        headers.update(extra_headers)
    return {
        "statusCode": status,
        "headers": headers,
        "body": json.dumps(body, ensure_ascii=False),
    }


def storage():
    global s3
    if s3 is None:
        s3 = boto3.client("s3")
    return s3


def job_key(job_id, filename):
    return f"jobs/{job_id}/{filename}"


def save_job(bucket, job):
    storage().put_object(
        Bucket=bucket,
        Key=job_key(job["job_id"], "state.json"),
        Body=json.dumps(job).encode("utf-8"),
        ContentType="application/json",
    )


def load_job(bucket, job_id):
    try:
        obj = storage().get_object(Bucket=bucket, Key=job_key(job_id, "state.json"))
    except ClientError as error:
        if error.response["Error"]["Code"] in ("NoSuchKey", "404"):
            return None
        raise
    return json.loads(obj["Body"].read())


def valid_job_id(job_id):
    return isinstance(job_id, str) and re.fullmatch(r"[0-9a-f]{32}", job_id) is not None


def start_job(event, context, bucket):
    global lambda_client
    body = event.get("body") or "{}"
    if event.get("isBase64Encoded"):
        body = base64.b64decode(body).decode("utf-8")
    data = json.loads(body)
    tex = data.get("tex") if isinstance(data, dict) else None
    if not isinstance(tex, str) or not tex.strip():
        return response(400, {"ok": False, "error": "Campo 'tex' vazio."})
    if len(tex.encode("utf-8")) > MAX_TEX_BYTES:
        return response(413, {"ok": False, "error": "O relatório TeX excede o limite de 2 MB."})
    job_id = uuid.uuid4().hex
    job = {"job_id": job_id, "status": "queued", "created_at": int(time.time())}
    storage().put_object(Bucket=bucket, Key=job_key(job_id, "input.tex"), Body=tex.encode("utf-8"), ContentType="text/plain; charset=utf-8")
    save_job(bucket, job)
    try:
        if lambda_client is None:
            lambda_client = boto3.client("lambda")
        result = lambda_client.invoke(
            FunctionName=context.invoked_function_arn,
            InvocationType="Event",
            Payload=json.dumps({"task": "compile_pdf", "job_id": job_id}).encode("utf-8"),
        )
        if result.get("StatusCode") != 202:
            raise RuntimeError("PDF worker invocation was not accepted")
    except Exception:
        job.update(status="failed", error="Não foi possível agendar a geração do PDF.")
        save_job(bucket, job)
        raise
    return response(202, {"ok": True, "job_id": job_id, "status": "queued"})


def run_job(job_id, context, bucket):
    if not valid_job_id(job_id):
        raise ValueError("Invalid PDF job ID")
    job = load_job(bucket, job_id)
    if not job or job["status"] in ("completed", "failed"):
        return
    try:
        storage().put_object(Bucket=bucket, Key=job_key(job_id, "lock"), Body=b"", IfNoneMatch="*")
    except ClientError as error:
        if error.response["Error"]["Code"] in ("PreconditionFailed", "412"):
            return
        raise
    job.update(status="processing")
    save_job(bucket, job)
    try:
        if time.time() - job["created_at"] > JOB_LIFETIME_SECONDS:
            raise TimeoutError("A tarefa de PDF expirou. Gere o PDF novamente.")
        obj = storage().get_object(Bucket=bucket, Key=job_key(job_id, "input.tex"))
        tex = obj["Body"].read().decode("utf-8")
        remaining = context.get_remaining_time_in_millis() / 1000 - 15
        if remaining <= 0:
            raise TimeoutError("A geração do PDF excedeu o tempo disponível.")
        pdf_bytes = PdfFromTexGenerator(tex).gerar_pdf(timeout=remaining)
        storage().put_object(Bucket=bucket, Key=job_key(job_id, "report.pdf"), Body=pdf_bytes, ContentType="application/pdf")
        job.update(status="completed", filename="report.pdf")
    except Exception:
        logger.exception("PDF job failed: %s", job_id)
        job.update(status="failed", error="Falha ao gerar PDF. Confira o TeX e tente novamente.")
    save_job(bucket, job)


def job_status(event, bucket):
    job_id = (event.get("pathParameters") or {}).get("job_id", "")
    if not valid_job_id(job_id):
        return response(400, {"ok": False, "error": "Identificador de PDF inválido."})
    job = load_job(bucket, job_id)
    if not job:
        return response(404, {"ok": False, "error": "Tarefa de PDF não encontrada ou expirada."})
    if job["status"] in ("queued", "processing") and time.time() - job["created_at"] > JOB_LIFETIME_SECONDS:
        return response(200, {"ok": False, "job_id": job_id, "status": "failed", "error": "A tarefa de PDF expirou. Gere o PDF novamente."})
    result = {"ok": job["status"] != "failed", **job}
    if job["status"] == "completed":
        url = storage().generate_presigned_url(
            "get_object",
            Params={"Bucket": bucket, "Key": job_key(job_id, "report.pdf"), "ResponseContentType": "application/pdf", "ResponseContentDisposition": 'inline; filename="report.pdf"'},
            ExpiresIn=300,
        )
        if (event.get("queryStringParameters") or {}).get("download") == "1":
            return response(302, {}, {"Location": url})
        result["download_url"] = url
    return response(200, result)


def handler(event, context):
    bucket = os.environ.get("PDF_JOB_BUCKET")
    if event.get("task") == "compile_pdf":
        if not bucket:
            raise RuntimeError("Missing PDF_JOB_BUCKET")
        run_job(event.get("job_id"), context, bucket)
        return {"ok": True}
    method = event.get("requestContext", {}).get("http", {}).get("method", "")
    if method == "OPTIONS":
        return response(204, {})
    if not bucket:
        return response(503, {"ok": False, "error": "Geração assíncrona de PDF indisponível."})
    try:
        if method == "POST":
            return start_job(event, context, bucket)
        if method == "GET":
            return job_status(event, bucket)
        return response(405, {"ok": False, "error": "Método não permitido."})
    except (ValueError, UnicodeDecodeError) as error:
        return response(400, {"ok": False, "error": str(error)})
    except Exception:
        logger.exception("PDF API failed")
        return response(500, {"ok": False, "error": "Não foi possível processar a tarefa de PDF."})
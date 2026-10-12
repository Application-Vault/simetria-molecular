import base64
import importlib.util
import io
import json
import os
import sys
import time
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, patch

from botocore.exceptions import ClientError

source = Path(__file__).resolve().parents[1] / "infra/lambda/pdf_handler"
renderer_spec = importlib.util.spec_from_file_location("pdf_job_renderer", source / "render/render_pdf_from_tex.py")
renderer = importlib.util.module_from_spec(renderer_spec)
renderer_spec.loader.exec_module(renderer)
handler_spec = importlib.util.spec_from_file_location("pdf_job_handler", source / "handler.py")
pdf_handler = importlib.util.module_from_spec(handler_spec)
with patch.dict(sys.modules, {"render.render_pdf_from_tex": renderer}):
    handler_spec.loader.exec_module(pdf_handler)


class MemoryStorage:
    def __init__(self):
        self.objects = {}

    def put_object(self, Bucket, Key, Body, **options):
        if options.get("IfNoneMatch") == "*" and Key in self.objects:
            raise ClientError({"Error": {"Code": "PreconditionFailed"}}, "PutObject")
        self.objects[Key] = Body

    def get_object(self, Bucket, Key):
        if Key not in self.objects:
            raise ClientError({"Error": {"Code": "NoSuchKey"}}, "GetObject")
        return {"Body": io.BytesIO(self.objects[Key])}

    def generate_presigned_url(self, operation, Params, ExpiresIn):
        return "https://private.example/report.pdf?expires=" + str(ExpiresIn)


class PdfJobTests(unittest.TestCase):
    def setUp(self):
        self.storage = MemoryStorage()
        self.invoker = Mock()
        self.invoker.invoke.return_value = {"StatusCode": 202}
        self.context = SimpleNamespace(invoked_function_arn="arn:aws:lambda:us-east-2:123456789012:function:test-pdf", get_remaining_time_in_millis=lambda: 300000)
        self.environment = patch.dict(os.environ, {"PDF_JOB_BUCKET": "private-jobs"})
        self.environment.start()
        self.addCleanup(self.environment.stop)
        self.clients = patch.multiple(pdf_handler, s3=self.storage, lambda_client=self.invoker)
        self.clients.start()
        self.addCleanup(self.clients.stop)

    def request(self, method, body=None, job_id=None, **extra):
        event = {"requestContext": {"http": {"method": method}}, "body": body if isinstance(body, str) else json.dumps(body or {}), "pathParameters": {"job_id": job_id}, **extra}
        return pdf_handler.handler(event, self.context)

    def start(self):
        response = self.request("POST", {"tex": "TeX source"})
        self.assertEqual(response["statusCode"], 202)
        return json.loads(response["body"])["job_id"]

    def test_post_enqueues_without_compiling(self):
        with patch.object(pdf_handler, "PdfFromTexGenerator") as generator:
            job_id = self.start()
            generator.assert_not_called()
        self.assertEqual(self.storage.objects[pdf_handler.job_key(job_id, "input.tex")], b"TeX source")
        invocation = self.invoker.invoke.call_args.kwargs
        self.assertEqual(invocation["InvocationType"], "Event")
        self.assertEqual(json.loads(invocation["Payload"]), {"task": "compile_pdf", "job_id": job_id})

    def test_worker_completes_once_and_returns_private_download(self):
        job_id = self.start()
        compiler = Mock()
        compiler.gerar_pdf.return_value = b"%PDF-test"
        with patch.object(pdf_handler, "PdfFromTexGenerator", return_value=compiler):
            pdf_handler.handler({"task": "compile_pdf", "job_id": job_id}, self.context)
            pdf_handler.handler({"task": "compile_pdf", "job_id": job_id}, self.context)
        compiler.gerar_pdf.assert_called_once_with(timeout=285)
        response = self.request("GET", job_id=job_id)
        result = json.loads(response["body"])
        self.assertEqual(result["status"], "completed")
        self.assertTrue(result["download_url"].startswith("https://private.example/"))
        self.assertNotIn("tex", result)
        self.assertNotIn("pdf_base64", result)
        download = self.request("GET", job_id=job_id, queryStringParameters={"download": "1"})
        self.assertEqual(download["statusCode"], 302)
        self.assertEqual(download["headers"]["Location"], result["download_url"])

    def test_compilation_error_is_stored_and_queryable(self):
        job_id = self.start()
        compiler = Mock()
        compiler.gerar_pdf.side_effect = RuntimeError("Missing $ inserted")
        with patch.object(pdf_handler, "PdfFromTexGenerator", return_value=compiler), self.assertLogs(pdf_handler.logger, level="ERROR"):
            pdf_handler.handler({"task": "compile_pdf", "job_id": job_id}, self.context)
        result = json.loads(self.request("GET", job_id=job_id)["body"])
        self.assertEqual(result["status"], "failed")
        self.assertIn("TeX", result["error"])

    def test_duplicate_processing_delivery_does_not_compile(self):
        job_id = self.start()
        self.storage.put_object(Bucket="private-jobs", Key=pdf_handler.job_key(job_id, "lock"), Body=b"")
        with patch.object(pdf_handler, "PdfFromTexGenerator") as compiler:
            pdf_handler.handler({"task": "compile_pdf", "job_id": job_id}, self.context)
        compiler.assert_not_called()

    def test_invalid_missing_and_expired_jobs(self):
        self.assertEqual(self.request("GET", job_id="invalid")["statusCode"], 400)
        self.assertEqual(self.request("GET", job_id="a" * 32)["statusCode"], 404)
        job_id = self.start()
        job = pdf_handler.load_job("private-jobs", job_id)
        job["created_at"] = int(time.time()) - pdf_handler.JOB_LIFETIME_SECONDS - 1
        pdf_handler.save_job("private-jobs", job)
        self.assertEqual(json.loads(self.request("GET", job_id=job_id)["body"])["status"], "failed")

    def test_input_is_validated_and_base64_body_is_supported(self):
        self.assertEqual(self.request("POST", {"tex": " "})["statusCode"], 400)
        self.assertEqual(self.request("POST", {"tex": 123})["statusCode"], 400)
        self.assertEqual(self.request("POST", {"tex": "a" * (pdf_handler.MAX_TEX_BYTES + 1)})["statusCode"], 413)
        body = base64.b64encode(json.dumps({"tex": "valid"}).encode()).decode()
        self.assertEqual(self.request("POST", isBase64Encoded=True, body=body)["statusCode"], 202)

    def test_compilation_uses_fresh_directories_and_timeout(self):
        directories = []

        def compile_pdf(command, **options):
            self.assertEqual(options["timeout"], 5)
            directory = Path(command[command.index("--outdir") + 1])
            directories.append(directory)
            (directory / "report.pdf").write_bytes(b"%PDF-test")
            return SimpleNamespace(returncode=0, stdout=b"", stderr=b"")

        with patch.object(renderer.subprocess, "run", side_effect=compile_pdf):
            for source_text in ("first", "second"):
                self.assertEqual(renderer.PdfFromTexGenerator(source_text).gerar_pdf(timeout=5), b"%PDF-test")
        self.assertNotEqual(directories[0], directories[1])
        self.assertFalse(any(directory.exists() for directory in directories))


if __name__ == "__main__":
    unittest.main()
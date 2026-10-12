resource "aws_s3_bucket" "pdf_jobs" {
  bucket = "${local.fullname}-${data.aws_caller_identity.me.account_id}-pdf-jobs"
}

resource "aws_s3_bucket_public_access_block" "pdf_jobs" {
  bucket                  = aws_s3_bucket.pdf_jobs.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_server_side_encryption_configuration" "pdf_jobs" {
  bucket = aws_s3_bucket.pdf_jobs.id
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_lifecycle_configuration" "pdf_jobs" {
  bucket = aws_s3_bucket.pdf_jobs.id
  rule {
    id     = "expire-pdf-jobs"
    status = "Enabled"
    filter {
      prefix = "jobs/"
    }
    expiration {
      days = 1
    }
  }
}

data "archive_file" "pdf_handler_zip" {
  type        = "zip"
  source_dir  = "${path.module}/lambda/pdf_handler"
  output_path = "${path.module}/build/${local.fullname}-pdf-handler.zip"
}

resource "aws_lambda_function" "pdf_handler" {
  function_name = "${local.fullname}-pdf"
  role          = aws_iam_role.pdf_handler.arn

  package_type = "Zip"
  runtime      = "python3.11"
  handler      = "handler.handler"

  filename         = data.archive_file.pdf_handler_zip.output_path
  source_code_hash = data.archive_file.pdf_handler_zip.output_base64sha256

  memory_size = 512
  timeout     = 300

  environment {
    variables = {
      HOME           = "/tmp"
      XDG_CACHE_HOME = "/tmp"
      PDF_JOB_BUCKET = aws_s3_bucket.pdf_jobs.id
      CORS_ORIGIN    = "https://quantum-materials-simulation-research.github.io"
    }
  }

  depends_on = [aws_cloudwatch_log_group.pdf_handler]

  lifecycle {
    ignore_changes = [
      filename,
      source_code_hash
    ]
  }
}

resource "aws_lambda_function_event_invoke_config" "pdf_handler" {
  function_name                = aws_lambda_function.pdf_handler.function_name
  maximum_event_age_in_seconds = 600
  maximum_retry_attempts       = 0
}
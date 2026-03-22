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
  timeout     = 60

  environment {
    variables = {
      HOME           = "/tmp"
      XDG_CACHE_HOME = "/tmp"
    }
  }

  depends_on = [aws_cloudwatch_log_group.pdf_handler]
}
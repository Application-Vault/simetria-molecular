data "archive_file" "handler_zip" {
  type        = "zip"
  source_dir  = "${path.module}/lambda_src/handler"
  output_path = "${path.module}/build/${local.fullname}.zip"
}

resource "aws_lambda_function" "handler" {
  function_name = local.fullname
  role          = aws_iam_role.lambda.arn
  runtime = "python3.11"
  handler = "handler.handler"

  # zip precisa existir no 1º apply
  filename         = data.archive_file.handler_zip.output_path
  source_code_hash = data.archive_file.handler_zip.output_base64sha256

  memory_size = 128
  timeout     = 60

  environment {
    variables = {
      # Se quiser, coloque configs aqui (ex: bucket, flags etc)
      # RESULT_BUCKET = "..."
    }
  }

  depends_on = [aws_cloudwatch_log_group.lambda]

  lifecycle {
    ignore_changes = [
      filename,
      source_code_hash
    ]
  }
}

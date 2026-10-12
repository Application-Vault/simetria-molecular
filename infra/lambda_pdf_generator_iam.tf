data "aws_iam_policy_document" "assume_pdf_handler" {
  statement {
    actions = ["sts:AssumeRole"]

    principals {
      type        = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }
  }
}

resource "aws_iam_role" "pdf_handler" {
  name               = "${local.fullname}-pdf-lambda-role"
  assume_role_policy = data.aws_iam_policy_document.assume_pdf_handler.json
}

resource "aws_iam_role_policy_attachment" "basic_exec_pdf" {
  role       = aws_iam_role.pdf_handler.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

data "aws_iam_policy_document" "pdf_jobs" {
  statement {
    actions   = ["s3:GetObject", "s3:PutObject"]
    resources = ["${aws_s3_bucket.pdf_jobs.arn}/jobs/*"]
  }

  statement {
    actions   = ["s3:ListBucket"]
    resources = [aws_s3_bucket.pdf_jobs.arn]
  }

  statement {
    actions   = ["lambda:InvokeFunction"]
    resources = [aws_lambda_function.pdf_handler.arn]
  }
}

resource "aws_iam_role_policy" "pdf_jobs" {
  name   = "${local.fullname}-pdf-jobs"
  role   = aws_iam_role.pdf_handler.id
  policy = data.aws_iam_policy_document.pdf_jobs.json
}

resource "aws_cloudwatch_log_group" "pdf_handler" {
  name              = "/aws/lambda/${local.fullname}-pdf"
  retention_in_days = 14
}
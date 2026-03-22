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

resource "aws_cloudwatch_log_group" "pdf_handler" {
  name              = "/aws/lambda/${local.fullname}-pdf"
  retention_in_days = 14
}
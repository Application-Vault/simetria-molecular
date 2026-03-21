data "aws_iam_policy_document" "assume_lambda" {
  statement {
    actions = ["sts:AssumeRole"]
    principals { 
        type = "Service"
        identifiers = ["lambda.amazonaws.com"] 
    }
  }
}

resource "aws_iam_role" "lambda" {
  name               = "${local.fullname}-lambda-role"
  assume_role_policy = data.aws_iam_policy_document.assume_lambda.json
}

# Permite logs
resource "aws_iam_role_policy_attachment" "basic_exec" {
  role       = aws_iam_role.lambda.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

# -----------------------------
# CloudWatch Logs
# -----------------------------

resource "aws_cloudwatch_log_group" "lambda" {
  name              = "/aws/lambda/${local.fullname}"
  retention_in_days = 14
}

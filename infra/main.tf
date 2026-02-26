terraform {
  cloud {
    organization = "Graduate-APPs-USP"
    workspaces {
      name = "Molecular_Symmetry"
    }
  }

  required_version = ">= 1.6.0"
  required_providers {
    aws = { source = "hashicorp/aws", version = ">= 5.0" }
  }
}

provider "aws" {
  region = var.aws_region
}

data "aws_caller_identity" "me" {}

locals {
  fullname = "${var.project_name}-${var.env}"
}

# -----------------------------
# CloudWatch Logs
# -----------------------------
resource "aws_cloudwatch_log_group" "lambda" {
  name              = "/aws/lambda/${local.fullname}"
  retention_in_days = 14
}

# -----------------------------
# IAM Role para Lambda
# -----------------------------
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
# Lambda (handler puro Python)
# -----------------------------

data "archive_file" "handler_zip" {
  type        = "zip"
  source_dir  = "${path.module}/lambda_src"
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
  timeout     = 15

  environment {
    variables = {
      # Se quiser, coloque configs aqui (ex: bucket, flags etc)
      # RESULT_BUCKET = "..."
    }
  }

  depends_on = [aws_cloudwatch_log_group.lambda]
}

# -----------------------------
# API Gateway HTTP API (v2)
# -----------------------------
resource "aws_apigatewayv2_api" "simetria-molecular" {
  name          = "${local.fullname}-api"
  protocol_type = "HTTP"

  cors_configuration {
    allow_origins = ["https://application-vault.github.io"]
    allow_methods = ["GET", "POST", "OPTIONS"]
    allow_headers = ["content-type", "authorization", "x-requested-with"]
    expose_headers = ["content-type"]
    max_age = 600
  }
}

resource "aws_apigatewayv2_integration" "handler" {
  api_id                 = aws_apigatewayv2_api.simetria-molecular.id
  integration_type       = "AWS_PROXY"
  integration_uri        = aws_lambda_function.handler.arn
  payload_format_version = "2.0"
}

# Rota curinga para preservar contrato inteiro sem mapear rota por rota
resource "aws_apigatewayv2_route" "proxy" {
  api_id    = aws_apigatewayv2_api.simetria-molecular.id
  route_key = "ANY /{proxy+}"
  target    = "integrations/${aws_apigatewayv2_integration.handler.id}"
}

resource "aws_apigatewayv2_stage" "prod" {
  api_id      = aws_apigatewayv2_api.simetria-molecular.id
  name        = "$default"
  auto_deploy = true
}

# Permite API Gateway invocar a Lambda
resource "aws_lambda_permission" "apigw" {
  statement_id  = "AllowApiGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.handler.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_apigatewayv2_api.simetria-molecular.execution_arn}/*/*"
}
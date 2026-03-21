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

resource "aws_apigatewayv2_stage" "prod" {
  api_id      = aws_apigatewayv2_api.simetria-molecular.id
  name        = "$default"
  auto_deploy = true
}


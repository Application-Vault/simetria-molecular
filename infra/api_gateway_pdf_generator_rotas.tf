resource "aws_apigatewayv2_integration" "pdf_handler" {
  api_id                 = aws_apigatewayv2_api.simetria-molecular.id
  integration_type       = "AWS_PROXY"
  integration_uri        = aws_lambda_function.pdf_handler.arn
  payload_format_version = "2.0"
}

resource "aws_apigatewayv2_route" "pdf_handler_post" {
  api_id    = aws_apigatewayv2_api.simetria-molecular.id
  route_key = "POST /api/pdf"
  target    = "integrations/${aws_apigatewayv2_integration.pdf_handler.id}"
}

resource "aws_apigatewayv2_route" "pdf_handler_options" {
  api_id    = aws_apigatewayv2_api.simetria-molecular.id
  route_key = "OPTIONS /api/pdf"
  target    = "integrations/${aws_apigatewayv2_integration.pdf_handler.id}"
}

resource "aws_lambda_permission" "allow_apigw_pdf_handler" {
  statement_id  = "AllowExecutionFromApiGatewayPdfGenerator"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.pdf_handler.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_apigatewayv2_api.simetria-molecular.execution_arn}/*/*/api/pdf"
}
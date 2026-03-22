# Permite API Gateway invocar a Lambda
resource "aws_lambda_permission" "apigw" {
  statement_id  = "AllowApiGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.handler.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_apigatewayv2_api.simetria-molecular.execution_arn}/*/*"
}

resource "aws_lambda_permission" "allow_apigw_pdf_handler" {
  statement_id  = "AllowExecutionFromApiGatewayPdfGenerator"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.pdf_handler.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_apigatewayv2_api.simetria-molecular.execution_arn}/*/*/api/pdf"
}
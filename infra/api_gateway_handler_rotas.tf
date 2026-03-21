# Rota curinga para preservar contrato inteiro sem mapear rota por rota
resource "aws_apigatewayv2_route" "proxy" {
  api_id    = aws_apigatewayv2_api.simetria-molecular.id
  route_key = "ANY /{proxy+}"
  target    = "integrations/${aws_apigatewayv2_integration.handler.id}"
}
resource "aws_apigatewayv2_route" "analise_post" {
  api_id    = aws_apigatewayv2_api.simetria-molecular.id
  route_key = "POST /api/analise"
  target    = "integrations/${aws_apigatewayv2_integration.handler.id}"
}

resource "aws_apigatewayv2_route" "analise_options" {
  api_id    = aws_apigatewayv2_api.simetria-molecular.id
  route_key = "OPTIONS /api/analise"
  target    = "integrations/${aws_apigatewayv2_integration.handler.id}"
}

resource "aws_apigatewayv2_route" "grupo_get" {
  api_id    = aws_apigatewayv2_api.simetria-molecular.id
  route_key = "GET /api/grupo/{id}"
  target    = "integrations/${aws_apigatewayv2_integration.handler.id}"
}

resource "aws_apigatewayv2_route" "grupo_options" {
  api_id    = aws_apigatewayv2_api.simetria-molecular.id
  route_key = "OPTIONS /api/grupo/{id}"
  target    = "integrations/${aws_apigatewayv2_integration.handler.id}"
}

resource "aws_apigatewayv2_route" "molecula_get" {
  api_id    = aws_apigatewayv2_api.simetria-molecular.id
  route_key = "GET /api/molecula/{id}"
  target    = "integrations/${aws_apigatewayv2_integration.handler.id}"
}

resource "aws_apigatewayv2_route" "molecula_options" {
  api_id    = aws_apigatewayv2_api.simetria-molecular.id
  route_key = "OPTIONS /api/molecula/{id}"
  target    = "integrations/${aws_apigatewayv2_integration.handler.id}"
}

resource "aws_apigatewayv2_route" "moleculas_list_get" {
  api_id    = aws_apigatewayv2_api.simetria-molecular.id
  route_key = "GET /api/moleculas"
  target    = "integrations/${aws_apigatewayv2_integration.handler.id}"
}

resource "aws_apigatewayv2_route" "moleculas_list_options" {
  api_id    = aws_apigatewayv2_api.simetria-molecular.id
  route_key = "OPTIONS /api/moleculas"
  target    = "integrations/${aws_apigatewayv2_integration.handler.id}"
}
output "api_base_url" {
  value = aws_apigatewayv2_api.simetria-molecular.api_endpoint
}

output "github_lambda_writer_arn" {
  description = "ARN da role assumida pelo GitHub Actions para deploy da Lambda"
  value       = aws_iam_role.github_lambda_writer.arn
}
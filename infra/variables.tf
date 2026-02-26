variable "aws_region" {
  description = "AWS region onde os recursos serão criados"
  type        = string
  default     = "us-east-2"
}

variable "project_name" {
  description = "Nome base do projeto (prefixo para recursos)"
  type        = string
  default     = "simetria-molecular"
}

variable "env" {
  type        = string
  default     = "prod"
}

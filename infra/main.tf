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
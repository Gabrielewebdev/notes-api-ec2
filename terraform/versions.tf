terraform {
  required_version = ">= 1.10, < 2.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.0"
    }
  }

  backend "s3" {
    bucket       = "notes-api-ec2-tfstate-726862573245"
    key          = "terraform.tfstate"
    region       = "us-east-1"
    encrypt      = true
    use_lockfile = true

  }
}

provider "aws" {
  region = "us-east-1"

  allowed_account_ids = ["726862573245"]

  default_tags {
    tags = {
      Project   = "notes-api-ec2"
      ManagedBy = "Terraform"
    }
  }
}

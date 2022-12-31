terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "4.48.0"
    }
    random = {
      source  = "hashicorp/random"
      version = "~>3.0"
    }
  }
}
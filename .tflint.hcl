plugin "terraform" {
  enabled = true
  preset  = "recommended"
}

plugin "aws" {
  enabled = true
  version = "0.28.0"
  source  = "github.com/terraform-linters/tflint-ruleset-aws"
}

# Disable unused declarations rule due to false positives
# The rule incorrectly flags locals and data sources that are actually used
rule "terraform_unused_declarations" {
  enabled = false
}

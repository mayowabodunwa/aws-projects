data "aws_caller_identity" "current" {}

# Keeps the log ARNs in iam.tf aligned with the provider's region rather than
# repeating "us-east-1" in a third place.
data "aws_region" "current" {}

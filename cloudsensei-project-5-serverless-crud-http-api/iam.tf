resource "aws_iam_role" "role" {
  name = "crud-api-exec-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = "sts:AssumeRole"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      }
    ]
  })
}

# jsonencode rather than a heredoc: Terraform validates the structure, and the
# ARNs interpolate from data sources instead of being pasted in.
resource "aws_iam_role_policy" "policy" {
  name = "crud-api-exec-role-policy"
  role = aws_iam_role.role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        # Scoped to the four calls the handlers actually make, on the one table
        # they use. Previously dynamodb:* on *, which let any handler drop any
        # table in the account.
        Action = [
          "dynamodb:PutItem",
          "dynamodb:GetItem",
          "dynamodb:DeleteItem",
          "dynamodb:Scan",
        ]
        Resource = aws_dynamodb_table.crud_table.arn
      },
      {
        Effect   = "Allow"
        Action   = "logs:CreateLogGroup"
        Resource = "arn:aws:logs:${data.aws_region.current.name}:${data.aws_caller_identity.current.account_id}:*"
      },
      {
        Effect = "Allow"
        Action = [
          "logs:CreateLogStream",
          "logs:PutLogEvents",
        ]
        Resource = "arn:aws:logs:${data.aws_region.current.name}:${data.aws_caller_identity.current.account_id}:log-group:/aws/lambda/*:*"
      },
    ]
  })
}

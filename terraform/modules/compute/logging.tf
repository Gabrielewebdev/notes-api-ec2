resource "aws_cloudwatch_log_group" "api" {
  name              = "/notes-api-ec2/api"
  retention_in_days = 14
}

resource "aws_iam_role_policy" "logs" {
  name = "${var.project_name}-logs"
  role = aws_iam_role.instance.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Action = [
        "logs:CreateLogStream",
        "logs:PutLogEvents"
      ]
      Resource = "${aws_cloudwatch_log_group.api.arn}:*"
    }]
  })
}

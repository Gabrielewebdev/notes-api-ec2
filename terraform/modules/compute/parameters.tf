resource "aws_iam_role_policy" "configuration" {
  name = "${var.project_name}-configuration"
  role = aws_iam_role.instance.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect   = "Allow"
      Action   = "ssm:GetParameter"
      Resource = "arn:aws:ssm:us-east-1:726862573245:parameter/notes-api-ec2/api-key"
    }]
  })
}

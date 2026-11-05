resource "aws_dynamodb_table" "notes" {
  name         = "${local.project_name}-notes"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "id"

  attribute {
    name = "id"
    type = "S"
  }

  server_side_encryption {
    enabled = true
  }

  tags = {
    Name = "${local.project_name}-notes"
  }
}

output "table_name" {
  value = aws_dynamodb_table.notes.name
}

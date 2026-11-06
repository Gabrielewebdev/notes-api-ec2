locals {
  project_name = "notes-api-ec2"
}

module "network" {
  source = "./modules/network"

  project_name = local.project_name
}

module "compute" {
  source = "./modules/compute"

  alert_email = var.alert_email

  project_name          = local.project_name
  vpc_id                = module.network.vpc_id
  subnet_ids            = module.network.public_subnet_ids
  alb_security_group_id = module.network.alb_security_group_id
  app_security_group_id = module.network.app_security_group_id

  certificate_arn = aws_acm_certificate_validation.api.certificate_arn
  table_name      = aws_dynamodb_table.notes.name
  table_arn       = aws_dynamodb_table.notes.arn

  image_uri      = "726862573245.dkr.ecr.us-east-1.amazonaws.com/notes-api-ec2@sha256:e9e1099a7e093d3397ff6bc6bf7a3bff8527047928a81b982c0bfe4181742550"
  repository_arn = "arn:aws:ecr:us-east-1:726862573245:repository/notes-api-ec2"

  depends_on = [module.network]
}

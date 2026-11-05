data "aws_ssm_parameter" "ami" {
  name = "/aws/service/ami-amazon-linux-latest/al2023-ami-kernel-default-x86_64"
}

resource "aws_launch_template" "api" {
  name_prefix   = "${var.project_name}-"
  image_id      = data.aws_ssm_parameter.ami.value
  instance_type = "t3.micro"

  vpc_security_group_ids = [var.app_security_group_id]

  iam_instance_profile {
    name = aws_iam_instance_profile.this.name
  }

  metadata_options {
    http_endpoint               = "enabled"
    http_tokens                 = "required"
    http_put_response_hop_limit = 2
  }

  credit_specification {
    cpu_credits = "standard"
  }

  block_device_mappings {
    device_name = "/dev/xvda"

    ebs {
      volume_size           = 8
      volume_type           = "gp3"
      encrypted             = true
      delete_on_termination = true
    }
  }

  user_data = base64encode(templatefile(
    "${path.module}/user_data.sh.tftpl",
    {
      table_name = var.table_name
      image_uri  = var.image_uri
    }
  ))

  tag_specifications {
    resource_type = "instance"

    tags = {
      Name    = "${var.project_name}-api"
      Project = var.project_name
    }
  }
}

resource "aws_autoscaling_group" "api" {
  name                = var.project_name
  min_size            = 2
  desired_capacity    = 2
  max_size            = 4
  vpc_zone_identifier = var.subnet_ids

  target_group_arns         = [aws_lb_target_group.api.arn]
  health_check_type         = "ELB"
  health_check_grace_period = 300
  default_instance_warmup   = 180

  launch_template {
    id      = aws_launch_template.api.id
    version = aws_launch_template.api.latest_version
  }

  instance_refresh {
    strategy = "Rolling"

    preferences {
      min_healthy_percentage = 100
      max_healthy_percentage = 150
      instance_warmup        = 180
    }
  }

  tag {
    key                 = "Name"
    value               = "${var.project_name}-api"
    propagate_at_launch = true
  }

  lifecycle {
    ignore_changes = [desired_capacity]
  }

  depends_on = [
    aws_lb_listener.https,
    aws_iam_role_policy.application,
    aws_iam_role_policy.configuration,
    aws_iam_role_policy.logs,
    aws_iam_role_policy_attachment.ssm
  ]
}

resource "aws_autoscaling_policy" "cpu" {
  name                   = "${var.project_name}-cpu"
  autoscaling_group_name = aws_autoscaling_group.api.name
  policy_type            = "TargetTrackingScaling"

  target_tracking_configuration {
    predefined_metric_specification {
      predefined_metric_type = "ASGAverageCPUUtilization"
    }

    target_value = 60
  }
}

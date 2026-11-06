variable "alert_email" {
  type        = string
  description = "Email address for monitoring notifications"
}

variable "image_uri" {
  type        = string
  description = "ECR image URI pinned by digest"

  default = "726862573245.dkr.ecr.us-east-1.amazonaws.com/notes-api-ec2@sha256:e9e1099a7e093d3397ff6bc6bf7a3bff8527047928a81b982c0bfe4181742550"

  validation {
    condition = can(regex(
      "^726862573245\\.dkr\\.ecr\\.us-east-1\\.amazonaws\\.com/notes-api-ec2@sha256:[0-9a-f]{64}$",
      var.image_uri
    ))
    error_message = "Usa un digest SHA256 del repository ECR notes-api-ec2."
  }
}

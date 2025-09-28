##############################
# Data sources
##############################

# Look up the current caller identity so we can construct ARNs
data "aws_caller_identity" "current" {}

# Fetch the existing ECR repository that holds the API image.  This assumes
# you have already pushed a container image to ECR using the repository
# name defined below.  If the repository does not exist, you can create
# it via the AWS Console or the CLI.  Terraform will fail if the repository
# name is wrong.
data "aws_ecr_repository" "echolove_api" {
  name = var.ecr_repository_name
}

##############################
# IAM role for App Runner
##############################

# Trust policy allowing App Runner to assume this role.  App Runner
# needs permission to pull images from ECR.
data "aws_iam_policy_document" "apprunner_assume_role" {
  statement {
    effect  = "Allow"
    actions = ["sts:AssumeRole"]
    principals {
      type        = "Service"
      identifiers = ["build.apprunner.amazonaws.com", "tasks.apprunner.amazonaws.com"]
    }
  }
}

# resource "aws_iam_role" "apprunner_service_role" {
#   name               = "${var.project_name}-apprunner-role"
#   assume_role_policy = data.aws_iam_policy_document.apprunner_assume_role.json
# }

# Attach the managed policy that grants App Runner read access to ECR.
# See AWS documentation for details on this policy.
# resource "aws_iam_role_policy_attachment" "apprunner_ecr_access" {
#   role       = aws_iam_role.apprunner_service_role.name
#   policy_arn = "arn:aws:iam::aws:policy/service-role/AWSAppRunnerServicePolicyForECRAccess"
# }

##############################
# AWS App Runner service
##############################

# The App Runner service launches your container image and exposes it via
# a public HTTPS endpoint.  You can customize CPU and memory settings
# through the instance_configuration block.  Environment variables from
# your .env file can be passed into the container via runtime_environment_variables.
# resource "aws_apprunner_service" "echolove" {
#   service_name = "${var.project_name}-api"

#   source_configuration {
#     authentication_configuration {
#       # Use the IAM role created above to allow App Runner to access ECR.
#       access_role_arn = aws_iam_role.apprunner_service_role.arn
#     }
#     # Disable auto deployments.  When set to true, App Runner will
#     # automatically deploy a new version whenever your ECR image changes.
#     auto_deployments_enabled = false

#     image_repository {
#       image_identifier      = "${data.aws_ecr_repository.echolove_api.repository_url}:${var.image_tag}"
#       image_repository_type = "ECR"
#       image_configuration {
#         # The port your application listens on.  Matches the EXPOSE instruction
#         # in your Dockerfile.
#         port = var.app_port

#         # Pass in runtime environment variables.  You can override the values
#         # from your .env file here or leave them unset to fall back to
#         # defaults in the application code.  Feel free to add/remove keys
#         # depending on your ingestion requirements.
#         runtime_environment_variables = {
#           DATABASE_URL        = var.database_url
#           MIN_GITHUB_STARS    = tostring(var.min_github_stars)
#           MAX_GITHUB_STARS    = var.max_github_stars
#           GITHUB_QUERY_ADDITIONS = var.github_query_additions
#           STACKEXCHANGE_SITES = var.stackexchange_sites
#         }
#       }
#     }
#   }

#   instance_configuration {
#     cpu    = var.apprunner_cpu
#     memory = var.apprunner_memory
#   }

#   tags = {
#     Name        = var.project_name
#     Environment = var.environment
#   }
# }

##############################
# Outputs
##############################

# output "service_url" {
#   description = "Public URL of the App Runner service"
#   value       = aws_apprunner_service.echolove.service_url
# }

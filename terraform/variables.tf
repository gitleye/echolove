variable "region" {
  description = "AWS region to deploy resources in"
  type        = string
  default     = "eu-west-2"
}

variable "project_name" {
  description = "Name prefix for resources.  Used in naming the App Runner service and IAM role."
  type        = string
  default     = "echolove"
}

variable "environment" {
  description = "Environment name, used for tagging.  Example: dev, staging, prod."
  type        = string
  default     = "dev"
}

variable "ecr_repository_name" {
  description = "Name of the ECR repository containing your API image"
  type        = string
  default     = "echolove-api"
}

variable "image_tag" {
  description = "Tag of the container image to deploy"
  type        = string
  default     = "latest"
}

variable "app_port" {
  description = "Port exposed by the Docker container"
  type        = string
  default     = "8080"
}

# Instance configuration
variable "apprunner_cpu" {
  description = "Number of CPU units for App Runner instances.  Supported values: 1024, 2048, 4096"
  type        = string
  default     = "1024"
}

variable "apprunner_memory" {
  description = "Memory size (in MiB) for App Runner instances.  Supported values: 2048, 3072, 4096"
  type        = string
  default     = "2048"
}

# Environment variables for the application
variable "database_url" {
  description = "Connection string for the database used by the API.  Defaults to a SQLite file in the container."
  type        = string
  default     = "sqlite:///./echolove.db"
}

variable "min_github_stars" {
  description = "Minimum number of GitHub stars required for a repository to be considered in ingestion"
  type        = number
  default     = 10
}

variable "max_github_stars" {
  description = "Maximum number of GitHub stars allowed when ingesting repositories.  Set to an empty string to remove the upper bound."
  type        = string
  default     = "1000"
}

variable "github_query_additions" {
  description = "Additional GitHub search qualifiers to narrow down repository topics"
  type        = string
  default     = "topic:cli OR topic:productivity OR topic:automation"
}

variable "stackexchange_sites" {
  description = "Semicolon-separated list of Stack Exchange sites to query for tool recommendations"
  type        = string
  default     = "stackoverflow;softwareengineering"
}
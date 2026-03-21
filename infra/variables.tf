variable "project_id" {
  description = "GCP project ID"
  type        = string
}

variable "region" {
  description = "GCP region for resource deployment"
  type        = string
  default     = "asia-northeast3"
}

variable "github_org" {
  description = "GitHub organization or username"
  type        = string
}

variable "github_repo" {
  description = "GitHub repository name"
  type        = string
}

variable "api_image" {
  description = "Full API container image URI including tag"
  type        = string
}

variable "api_env" {
  description = "Environment variables for API Cloud Run service"
  type        = map(string)
  default     = {}
}

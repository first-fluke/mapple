variable "project_id" {
  description = "GCP project ID where Cloud Run resources will be created"
  type        = string
}

variable "region" {
  description = "GCP region for the Cloud Run service"
  type        = string
}

variable "environment" {
  description = "Deployment environment name (e.g. dev, staging, prod)"
  type        = string
}

variable "service_name" {
  description = "Base name for the Cloud Run service"
  type        = string
}

variable "image" {
  description = "Container image URI to deploy (e.g. gcr.io/project/image:tag)"
  type        = string
}

variable "port" {
  description = "Container port the service listens on"
  type        = number
  default     = 8080
}

variable "vpc_connector_id" {
  description = "Full resource ID of the VPC Access connector for private networking"
  type        = string
}

variable "vpc_egress" {
  description = "VPC egress setting controlling which traffic is routed through the connector"
  type        = string
  default     = "PRIVATE_RANGES_ONLY"
}

variable "service_account_email" {
  description = "Email of the IAM service account the Cloud Run revision runs as"
  type        = string
}

variable "env_vars" {
  description = "Non-sensitive environment variables to inject into the container"
  type        = map(string)
  default     = {}
}

variable "secret_env_vars" {
  description = "Environment variables sourced from Secret Manager (key = env var name)"
  type = map(object({
    secret_id = string
    version   = string
  }))
  default = {}
}

variable "min_instances" {
  description = "Minimum number of instances to keep warm (0 allows scale-to-zero)"
  type        = number
  default     = 0
}

variable "max_instances" {
  description = "Maximum number of instances the service can scale to"
  type        = number
  default     = 2
}

variable "cpu" {
  description = "CPU limit per container instance (e.g. 1, 2, 4)"
  type        = string
  default     = "1"
}

variable "memory" {
  description = "Memory limit per container instance (e.g. 512Mi, 1Gi)"
  type        = string
  default     = "512Mi"
}

variable "concurrency" {
  description = "Maximum number of concurrent requests each instance handles"
  type        = number
  default     = 80
}

variable "timeout_seconds" {
  description = "Maximum duration for a single request before it is terminated"
  type        = string
  default     = "300s"
}

variable "allow_unauthenticated" {
  description = "Whether to allow unauthenticated (public) access to the service"
  type        = bool
  default     = false
}

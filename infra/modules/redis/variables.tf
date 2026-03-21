variable "project_id" {
  description = "GCP project ID where the Redis instance will be created"
  type        = string
}

variable "region" {
  description = "GCP region for the Redis instance"
  type        = string
}

variable "environment" {
  description = "Deployment environment (e.g. dev, staging, prod)"
  type        = string
}

variable "instance_name" {
  description = "Base name for the Redis instance; environment is appended automatically"
  type        = string
  default     = "globe-crm-cache"
}

variable "redis_version" {
  description = "Redis engine version to provision"
  type        = string
  default     = "REDIS_7_0"
}

variable "tier" {
  description = "Service tier: BASIC for dev, STANDARD_HA for prod"
  type        = string
  default     = "BASIC"
}

variable "memory_size_gb" {
  description = "Memory size of the Redis instance in GiB"
  type        = number
  default     = 1
}

variable "vpc_network_id" {
  description = "Self-link of the VPC network for private service access"
  type        = string
}

variable "auth_enabled" {
  description = "Whether IAM-based AUTH is enabled on the instance"
  type        = bool
  default     = true
}

variable "transit_encryption_mode" {
  description = "TLS encryption mode: DISABLED for dev, SERVER_AUTHENTICATION for prod"
  type        = string
  default     = "DISABLED"
}

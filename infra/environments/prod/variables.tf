variable "project_id" {
  description = "GCP project ID"
  type        = string
}

variable "region" {
  description = "GCP region"
  type        = string
  default     = "asia-northeast3"
}

variable "environment" {
  description = "Environment name"
  type        = string
  default     = "prod"
}

# Networking
variable "subnet_cidr" {
  description = "Primary subnet CIDR range"
  type        = string
  default     = "10.1.0.0/20"
}

variable "connector_cidr" {
  description = "Serverless VPC Access connector CIDR range"
  type        = string
  default     = "10.9.0.0/28"
}

# Cloud SQL
variable "cloud_sql_tier" {
  description = "Cloud SQL machine type"
  type        = string
  default     = "db-custom-2-8192"
}

variable "cloud_sql_availability_type" {
  description = "Cloud SQL availability type (ZONAL or REGIONAL)"
  type        = string
  default     = "REGIONAL"
}

variable "cloud_sql_deletion_protection" {
  description = "Enable deletion protection for Cloud SQL"
  type        = bool
  default     = true
}

variable "cloud_sql_backup_enabled" {
  description = "Enable automated backups for Cloud SQL"
  type        = bool
  default     = true
}

variable "cloud_sql_pitr_enabled" {
  description = "Enable point-in-time recovery for Cloud SQL"
  type        = bool
  default     = true
}

# Redis
variable "redis_tier" {
  description = "Redis tier (BASIC or STANDARD_HA)"
  type        = string
  default     = "STANDARD_HA"
}

variable "redis_memory_size_gb" {
  description = "Redis memory size in GB"
  type        = number
  default     = 4
}

# Cloud Run
variable "api_image" {
  description = "Container image URI for the API service"
  type        = string
  default     = "gcr.io/cloudrun/hello"
}

variable "web_image" {
  description = "Container image URI for the Web service"
  type        = string
  default     = "gcr.io/cloudrun/hello"
}

variable "api_min_instances" {
  description = "Minimum number of API instances"
  type        = number
  default     = 1
}

variable "api_max_instances" {
  description = "Maximum number of API instances"
  type        = number
  default     = 10
}

variable "web_min_instances" {
  description = "Minimum number of Web instances"
  type        = number
  default     = 1
}

variable "web_max_instances" {
  description = "Maximum number of Web instances"
  type        = number
  default     = 10
}

# Storage
variable "cors_origins" {
  description = "Allowed CORS origins for storage buckets"
  type        = list(string)
  default     = []
}

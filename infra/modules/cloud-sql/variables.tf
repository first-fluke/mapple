variable "project_id" {
  description = "GCP project ID where Cloud SQL resources will be created"
  type        = string
}

variable "region" {
  description = "GCP region for the Cloud SQL instance"
  type        = string
}

variable "environment" {
  description = "Deployment environment name (e.g. dev, staging, prod)"
  type        = string
}

variable "instance_name" {
  description = "Base name for the Cloud SQL instance"
  type        = string
  default     = "globe-crm-db"
}

variable "database_version" {
  description = "PostgreSQL engine version for the Cloud SQL instance"
  type        = string
  default     = "POSTGRES_16"
}

variable "tier" {
  description = "Machine tier for the Cloud SQL instance (e.g. db-f1-micro for dev, db-custom-2-8192 for prod)"
  type        = string
}

variable "disk_size_gb" {
  description = "Initial disk size in GB for the Cloud SQL instance"
  type        = number
  default     = 10
}

variable "disk_autoresize" {
  description = "Whether the disk should automatically grow when running low on space"
  type        = bool
  default     = true
}

variable "availability_type" {
  description = "Availability type for the Cloud SQL instance (ZONAL for dev, REGIONAL for prod HA)"
  type        = string
  default     = "ZONAL"
}

variable "backup_enabled" {
  description = "Whether automated backups are enabled for the Cloud SQL instance"
  type        = bool
  default     = false
}

variable "backup_start_time" {
  description = "HH:MM time window (UTC) when the daily backup should start"
  type        = string
  default     = "03:00"
}

variable "point_in_time_recovery" {
  description = "Whether point-in-time recovery (PITR) is enabled via WAL archiving"
  type        = bool
  default     = false
}

variable "database_name" {
  description = "Name of the default database to create in the Cloud SQL instance"
  type        = string
  default     = "globe_crm"
}

variable "database_user" {
  description = "Name of the default database user to create"
  type        = string
  default     = "globe"
}

variable "vpc_network_id" {
  description = "Self-link of the VPC network for private IP connectivity (from networking module)"
  type        = string
}

variable "deletion_protection" {
  description = "Whether Terraform is prevented from destroying the Cloud SQL instance"
  type        = bool
  default     = false
}

variable "maintenance_window_day" {
  description = "Day of the week (1=Mon, 7=Sun) for the preferred maintenance window"
  type        = number
  default     = 7
}

variable "maintenance_window_hour" {
  description = "Hour of the day (0-23 UTC) for the preferred maintenance window"
  type        = number
  default     = 4
}

variable "database_flags" {
  description = "Additional database flags to set on the Cloud SQL instance"
  type = list(object({
    name  = string
    value = string
  }))
  default = []
}

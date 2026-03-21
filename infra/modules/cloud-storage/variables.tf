variable "project_id" {
  description = "The GCP project ID where buckets will be created."
  type        = string
}

variable "region" {
  description = "The GCP region for bucket location."
  type        = string
}

variable "environment" {
  description = "The deployment environment (e.g. dev, staging, prod)."
  type        = string
}

variable "bucket_prefix" {
  description = "Prefix for all bucket names."
  type        = string
  default     = "globe-crm"
}

variable "bucket_names" {
  description = "List of bucket name suffixes to create."
  type        = list(string)
  default     = ["avatars"]
}

variable "storage_class" {
  description = "The storage class for the buckets (e.g. STANDARD, NEARLINE, COLDLINE, ARCHIVE)."
  type        = string
  default     = "STANDARD"
}

variable "versioning_enabled" {
  description = "Whether to enable object versioning on the buckets."
  type        = bool
  default     = false
}

variable "lifecycle_delete_days" {
  description = "Number of days after which objects are deleted. Set to 0 to disable lifecycle deletion."
  type        = number
  default     = 0
}

variable "force_destroy" {
  description = "Whether to allow Terraform to destroy buckets that still contain objects."
  type        = bool
  default     = false
}

variable "cors_origins" {
  description = "List of allowed CORS origins. Leave empty to disable CORS configuration."
  type        = list(string)
  default     = []
}

variable "project_id" {
  description = "The GCP project ID where IAM resources will be created"
  type        = string
}

variable "environment" {
  description = "The deployment environment (e.g. dev, staging, prod)"
  type        = string
}

variable "api_service_account_id" {
  description = "The base account ID for the API service account"
  type        = string
  default     = "globe-crm-api"
}

variable "web_service_account_id" {
  description = "The base account ID for the Web service account"
  type        = string
  default     = "globe-crm-web"
}

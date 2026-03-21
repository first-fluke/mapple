variable "project_id" {
  description = "GCP project ID where networking resources will be created"
  type        = string
}

variable "region" {
  description = "GCP region for regional networking resources"
  type        = string
}

variable "environment" {
  description = "Deployment environment name (e.g. dev, staging, prod)"
  type        = string
}

variable "vpc_name" {
  description = "Base name for the VPC network"
  type        = string
  default     = "globe-crm-vpc"
}

variable "subnet_cidr" {
  description = "CIDR range for the primary regional subnet"
  type        = string
  default     = "10.0.0.0/20"
}

variable "connector_cidr" {
  description = "CIDR range for the Serverless VPC Access connector"
  type        = string
  default     = "10.8.0.0/28"
}

variable "private_service_cidr" {
  description = "CIDR range for private services access (Cloud SQL, Redis)"
  type        = string
  default     = "10.16.0.0/20"
}

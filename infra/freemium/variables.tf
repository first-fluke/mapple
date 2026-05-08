variable "project_prefix" {
  type        = string
  description = "Prefix for all resource names"
  default     = "globe-crm"
}

variable "github_repo" {
  type        = string
  description = "GitHub repository (owner/repo) for Vercel git integration"
}

variable "supabase_org_id" {
  type        = string
  description = "Supabase organization slug"
}

variable "supabase_db_password" {
  type        = string
  sensitive   = true
  description = "Supabase database password"
}

variable "supabase_region" {
  type        = string
  default     = "ap-northeast-2"
  description = "Supabase project region (Seoul: ap-northeast-2, Tokyo: ap-northeast-1)"
}

variable "upstash_region" {
  type        = string
  default     = "ap-northeast-1"
  description = "Upstash Redis region (ap-northeast-1 Tokyo, ap-southeast-1 Singapore, eu-west-1, us-east-1)"
}

variable "b2_region" {
  type        = string
  default     = "us-west-004"
  description = "Backblaze B2 region used to compose the S3 endpoint (s3.<region>.backblazeb2.com)"
}

variable "api_url" {
  type        = string
  description = "Public URL of the FastAPI backend (Fly.io). Example: https://globe-crm-api.fly.dev"
}

variable "web_app_url" {
  type        = string
  description = "Public URL of the Vercel web frontend. Example: https://globe-crm.vercel.app"
}

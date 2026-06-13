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

# Cloudflare DNS
variable "cloudflare_zone_name" {
  type        = string
  description = "Registered domain managed in Cloudflare (e.g. globecrm.io). The zone must exist in Cloudflare before apply."
  # TODO(external): Set to the actual registered domain name.
  default = ""
}

variable "cloudflare_web_cname_target" {
  type        = string
  description = "Vercel CNAME target for the web app custom domain (e.g. cname.vercel-dns.com). Find in Vercel project > Domains."
  # TODO(external): Set to the cname.vercel-dns.com value shown in the Vercel project domains settings.
  default = ""
}

variable "cloudflare_api_cname_target" {
  type        = string
  description = "Fly.io app hostname for the API CNAME record (e.g. globe-crm-api.fly.dev). Find via `flyctl info`."
  # TODO(external): Set to the Fly.io app hostname.
  default = ""
}

variable "cloudflare_web_proxied" {
  type        = bool
  description = "Enable Cloudflare proxy (orange cloud) for the web record. Enables WAF + DDoS protection."
  default     = true
}

variable "cloudflare_api_proxied" {
  type        = bool
  description = "Enable Cloudflare proxy for the API record. Set false if Fly.io handles TLS termination or WebSocket pass-through is needed."
  default     = false
}

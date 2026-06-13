variable "zone_name" {
  description = "Cloudflare DNS zone name (e.g. example.com). The zone must already exist in Cloudflare; this module performs a data lookup."
  type        = string
  # TODO(external): Set to the registered domain once the domain is provisioned.
  # Example: "globecrm.io"
}

variable "environment" {
  description = "Deployment environment name (e.g. dev, staging, prod, freemium). Used to namespace record names."
  type        = string
}

# Web (Vercel) record
variable "web_subdomain" {
  description = "Subdomain for the web app (Vercel). Combined with zone_name to form the FQDN. E.g. 'app' yields app.<zone_name>."
  type        = string
  default     = "app"
}

variable "web_cname_target" {
  description = "Vercel CNAME target for the web app. Find this in the Vercel project domains settings after adding a custom domain."
  type        = string
  # TODO(external): Set to the cname.vercel-dns.com value shown in the Vercel dashboard.
  # Example: "cname.vercel-dns.com"
}

variable "web_proxied" {
  description = "Whether the Cloudflare proxy (orange cloud) is enabled for the web DNS record. Enables WAF, CDN, and DDoS protection."
  type        = bool
  default     = true
}

variable "web_ttl" {
  description = "TTL in seconds for the web CNAME record. Ignored when proxied = true (Cloudflare sets TTL to 1/auto)."
  type        = number
  default     = 1
}

# API (Fly.io) record
variable "api_subdomain" {
  description = "Subdomain for the API backend (Fly.io). Combined with zone_name to form the FQDN. E.g. 'api' yields api.<zone_name>."
  type        = string
  default     = "api"
}

variable "api_cname_target" {
  description = "Fly.io CNAME target for the API app. Find this via `flyctl info` or the Fly dashboard (typically <app-name>.fly.dev)."
  type        = string
  # TODO(external): Set to the Fly.io app hostname.
  # Example: "globe-crm-api.fly.dev"
}

variable "api_proxied" {
  description = "Whether the Cloudflare proxy is enabled for the API DNS record. Disable (false) if Fly.io handles TLS termination directly and WebSocket/gRPC pass-through is needed."
  type        = bool
  default     = false
}

variable "api_ttl" {
  description = "TTL in seconds for the API CNAME record. Ignored when proxied = true."
  type        = number
  default     = 300
}

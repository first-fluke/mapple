# Cloudflare provider v5: zone lookup by name uses the `cloudflare_zones`
# (plural) list data source with a name filter. The singular `cloudflare_zone`
# data source is read-only and requires a known zone_id, which we do not have
# until the domain is provisioned.
data "cloudflare_zones" "main" {
  name = var.zone_name
}

locals {
  zone_id = data.cloudflare_zones.main.result[0].id
}

# Web app: Vercel CNAME
resource "cloudflare_dns_record" "web" {
  zone_id = local.zone_id
  name    = "${var.web_subdomain}.${var.zone_name}"
  type    = "CNAME"
  content = var.web_cname_target
  proxied = var.web_proxied
  ttl     = var.web_proxied ? 1 : var.web_ttl

  comment = "Globe CRM web (Vercel) — managed by Terraform [${var.environment}]"
}

# API: Fly.io CNAME
resource "cloudflare_dns_record" "api" {
  zone_id = local.zone_id
  name    = "${var.api_subdomain}.${var.zone_name}"
  type    = "CNAME"
  content = var.api_cname_target
  proxied = var.api_proxied
  ttl     = var.api_proxied ? 1 : var.api_ttl

  comment = "Globe CRM API (Fly.io) — managed by Terraform [${var.environment}]"
}

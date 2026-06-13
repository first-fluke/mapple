output "zone_id" {
  description = "Cloudflare zone ID for the managed DNS zone"
  value       = local.zone_id
}

output "zone_name" {
  description = "Cloudflare zone name (domain) being managed"
  value       = var.zone_name
}

output "web_record_hostname" {
  description = "Full hostname of the web CNAME record (e.g. app.example.com)"
  value       = cloudflare_dns_record.web.name
}

output "api_record_hostname" {
  description = "Full hostname of the API CNAME record (e.g. api.example.com)"
  value       = cloudflare_dns_record.api.name
}

output "web_record_id" {
  description = "Cloudflare record ID for the web CNAME entry"
  value       = cloudflare_dns_record.web.id
}

output "api_record_id" {
  description = "Cloudflare record ID for the API CNAME entry"
  value       = cloudflare_dns_record.api.id
}

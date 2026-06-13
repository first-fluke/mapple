output "supabase_project_ref" {
  value       = local.supabase_project_ref
  description = "Supabase project reference"
}

output "supabase_url" {
  value       = local.supabase_url
  description = "Supabase project URL"
}

output "vercel_web_project_id" {
  value       = vercel_project.web.id
  description = "Vercel web project ID"
}

output "b2_bucket_name" {
  value       = b2_bucket.avatars.bucket_name
  description = "B2 avatars bucket name"
}

output "fly_secrets_command" {
  value = join(" ", concat(
    ["flyctl secrets set --app ${var.project_prefix}-api"],
    [for k, v in local.fly_secrets : "${k}='${v}'"]
  ))
  description = "One-shot flyctl command to set all api secrets"
  sensitive   = true
}

output "fly_secrets" {
  value       = local.fly_secrets
  description = "Map of secrets to set on the Fly.io api app"
  sensitive   = true
}

output "web_hostname" {
  value       = module.cloudflare_dns.web_record_hostname
  description = "Public hostname for the web app (Cloudflare DNS, e.g. app.example.com)"
}

output "api_hostname" {
  value       = module.cloudflare_dns.api_record_hostname
  description = "Public hostname for the API (Cloudflare DNS, e.g. api.example.com)"
}

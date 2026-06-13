module "cloudflare_dns" {
  source = "../modules/cloudflare-dns"

  zone_name        = var.cloudflare_zone_name
  environment      = "freemium"
  web_cname_target = var.cloudflare_web_cname_target
  api_cname_target = var.cloudflare_api_cname_target
  web_proxied      = var.cloudflare_web_proxied
  api_proxied      = var.cloudflare_api_proxied
}

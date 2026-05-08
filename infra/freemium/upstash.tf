resource "upstash_redis_database" "main" {
  database_name = "${var.project_prefix}-redis"
  region        = var.upstash_region
  tls           = true
  eviction      = false
}

resource "google_redis_instance" "this" {
  project = var.project_id

  name           = "${var.instance_name}-${var.environment}"
  tier           = var.tier
  memory_size_gb = var.memory_size_gb
  region         = var.region
  redis_version  = var.redis_version

  authorized_network      = var.vpc_network_id
  connect_mode            = "PRIVATE_SERVICE_ACCESS"
  auth_enabled            = var.auth_enabled
  transit_encryption_mode = var.transit_encryption_mode

  labels = {
    environment = var.environment
  }
}

locals {
  project_id  = var.project_id
  region      = var.region
  environment = var.environment
}

module "iam" {
  source = "../../modules/iam"

  project_id  = local.project_id
  environment = local.environment
}

module "networking" {
  source = "../../modules/networking"

  project_id     = local.project_id
  region         = local.region
  environment    = local.environment
  subnet_cidr    = var.subnet_cidr
  connector_cidr = var.connector_cidr
}

module "cloud_sql" {
  source = "../../modules/cloud-sql"

  project_id             = local.project_id
  region                 = local.region
  environment            = local.environment
  tier                   = var.cloud_sql_tier
  availability_type      = var.cloud_sql_availability_type
  vpc_network_id         = module.networking.vpc_self_link
  deletion_protection    = var.cloud_sql_deletion_protection
  backup_enabled         = var.cloud_sql_backup_enabled
  point_in_time_recovery = var.cloud_sql_pitr_enabled

  depends_on = [module.networking]
}

module "redis" {
  source = "../../modules/redis"

  project_id              = local.project_id
  region                  = local.region
  environment             = local.environment
  tier                    = var.redis_tier
  memory_size_gb          = var.redis_memory_size_gb
  vpc_network_id          = module.networking.vpc_self_link
  transit_encryption_mode = "SERVER_AUTHENTICATION"

  depends_on = [module.networking]
}

module "cloud_storage" {
  source = "../../modules/cloud-storage"

  project_id         = local.project_id
  region             = local.region
  environment        = local.environment
  bucket_names       = ["avatars"]
  versioning_enabled = true
  cors_origins       = var.cors_origins
}

module "cloud_run_api" {
  source = "../../modules/cloud-run"

  project_id            = local.project_id
  region                = local.region
  environment           = local.environment
  service_name          = "globe-crm-api"
  image                 = var.api_image
  port                  = 8000
  vpc_connector_id      = module.networking.vpc_connector_id
  service_account_email = module.iam.api_service_account_email
  min_instances         = var.api_min_instances
  max_instances         = var.api_max_instances
  cpu                   = "2"
  memory                = "1Gi"
  allow_unauthenticated = true

  env_vars = {
    ENVIRONMENT = local.environment
  }

  secret_env_vars = {
    DATABASE_URL = { secret_id = "database-url", version = "latest" }
    REDIS_URL    = { secret_id = "redis-url", version = "latest" }
  }
}

module "cloud_run_web" {
  source = "../../modules/cloud-run"

  project_id            = local.project_id
  region                = local.region
  environment           = local.environment
  service_name          = "globe-crm-web"
  image                 = var.web_image
  port                  = 3000
  vpc_connector_id      = module.networking.vpc_connector_id
  service_account_email = module.iam.web_service_account_email
  min_instances         = var.web_min_instances
  max_instances         = var.web_max_instances
  allow_unauthenticated = true

  env_vars = {
    API_BASE_URL = module.cloud_run_api.service_url
    ENVIRONMENT  = local.environment
  }
}

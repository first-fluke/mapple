locals {
  supabase_project_ref = supabase_project.main.id
  supabase_url         = "https://${local.supabase_project_ref}.supabase.co"

  # Direct connection (port 5432) — used by Alembic migrations.
  supabase_direct_host   = "db.${local.supabase_project_ref}.supabase.co"
  migration_database_url = "postgresql+asyncpg://postgres:${var.supabase_db_password}@${local.supabase_direct_host}:5432/postgres"

  # Supavisor transaction-mode pooler (port 6543) — runtime asyncpg connection.
  # Username uses the project-ref-scoped form: postgres.<project_ref>
  supabase_pooler_host = "aws-0-${var.supabase_region}.pooler.supabase.com"
  database_url         = "postgresql+asyncpg://postgres.${local.supabase_project_ref}:${var.supabase_db_password}@${local.supabase_pooler_host}:6543/postgres"

  b2_endpoint = "s3.${var.b2_region}.backblazeb2.com"

  # Fly.io secrets to set via `flyctl secrets set` after `terraform apply`.
  fly_secrets = {
    DATABASE_URL           = local.database_url
    MIGRATION_DATABASE_URL = local.migration_database_url
    REDIS_URL              = "rediss://default:${upstash_redis_database.main.password}@${upstash_redis_database.main.endpoint}:${upstash_redis_database.main.port}"
    MINIO_ENDPOINT         = local.b2_endpoint
    MINIO_ACCESS_KEY       = b2_application_key.avatars.application_key_id
    MINIO_SECRET_KEY       = b2_application_key.avatars.application_key
    MINIO_SECURE           = "true"
    WEB_APP_URL            = var.web_app_url
    CORS_ALLOW_ORIGINS     = var.web_app_url
    API_BASE_URL           = var.api_url
  }

  vercel_web_env = {
    NEXT_PUBLIC_API_URL = var.api_url
    API_URL             = var.api_url
  }
}

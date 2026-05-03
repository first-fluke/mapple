# ============================================================
# Globe CRM — prod environment variable overrides
# All variables explicitly set; no default fallback in prod.
# ============================================================

# ---- Core ----
project_id  = "globe-crm-prod"
region      = "asia-northeast3"
environment = "prod"

# ---- Networking ----
# prod CIDRs must not overlap with dev (10.0.0.0/20, 10.8.0.0/28)
subnet_cidr    = "10.1.0.0/20"
connector_cidr = "10.9.0.0/28"

# ---- Cloud SQL ----
# db-custom-2-8192: 2 vCPU / 8 GB RAM — baseline prod sizing
# Scale to db-custom-4-16384 if p95 query latency exceeds 200 ms under load.
cloud_sql_tier                = "db-custom-2-8192"
cloud_sql_availability_type   = "REGIONAL"
cloud_sql_deletion_protection = true
cloud_sql_backup_enabled      = true
cloud_sql_pitr_enabled        = true

# ---- Redis ----
# STANDARD_HA: primary + replica across zones for HA
# 2 GB covers session tokens + API-response cache for initial launch traffic;
# revisit after Sentry/monitoring shows eviction pressure.
redis_tier           = "STANDARD_HA"
redis_memory_size_gb = 2

# ---- Cloud Storage ----
# Restrict CORS to the prod web domain once Cloudflare/Vercel domains are
# finalised (Task 4). Use wildcard temporarily only during pre-launch testing.
cors_origins = ["https://app.globe-crm.com"]

locals {
  default_database_flags = [
    {
      name  = "cloudsql.enable_postgis"
      value = "on"
    },
  ]

  database_flags = concat(local.default_database_flags, var.database_flags)
}

resource "random_password" "database" {
  length  = 24
  special = true
}

resource "google_sql_database_instance" "main" {
  project             = var.project_id
  name                = "${var.instance_name}-${var.environment}"
  database_version    = var.database_version
  region              = var.region
  deletion_protection = var.deletion_protection

  settings {
    tier              = var.tier
    disk_size         = var.disk_size_gb
    disk_autoresize   = var.disk_autoresize
    availability_type = var.availability_type

    ip_configuration {
      ipv4_enabled    = false
      private_network = var.vpc_network_id
    }

    dynamic "database_flags" {
      for_each = local.database_flags
      content {
        name  = database_flags.value.name
        value = database_flags.value.value
      }
    }

    backup_configuration {
      enabled                        = var.backup_enabled
      start_time                     = var.backup_start_time
      point_in_time_recovery_enabled = var.point_in_time_recovery
      transaction_log_retention_days = 7
    }

    maintenance_window {
      day          = var.maintenance_window_day
      hour         = var.maintenance_window_hour
      update_track = "stable"
    }

    insights_config {
      query_insights_enabled  = true
      record_application_tags = true
    }
  }
}

resource "google_sql_database" "main" {
  project  = var.project_id
  name     = var.database_name
  instance = google_sql_database_instance.main.name
}

resource "google_sql_user" "main" {
  project  = var.project_id
  name     = var.database_user
  instance = google_sql_database_instance.main.name
  password = random_password.database.result
}

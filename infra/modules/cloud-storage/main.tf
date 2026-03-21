resource "google_storage_bucket" "bucket" {
  for_each = toset(var.bucket_names)

  project                     = var.project_id
  name                        = "${var.bucket_prefix}-${var.environment}-${each.value}"
  location                    = var.region
  storage_class               = var.storage_class
  uniform_bucket_level_access = true
  force_destroy               = var.force_destroy
  public_access_prevention    = "enforced"

  versioning {
    enabled = var.versioning_enabled
  }

  dynamic "lifecycle_rule" {
    for_each = var.lifecycle_delete_days > 0 ? [1] : []

    content {
      action {
        type = "Delete"
      }

      condition {
        age = var.lifecycle_delete_days
      }
    }
  }

  dynamic "cors" {
    for_each = length(var.cors_origins) > 0 ? [1] : []

    content {
      origin          = var.cors_origins
      method          = ["GET", "PUT", "POST", "DELETE"]
      response_header = ["Content-Type", "Content-Disposition"]
      max_age_seconds = 3600
    }
  }

  labels = {
    environment = var.environment
  }
}

locals {
  api_roles = [
    "roles/cloudsql.client",
    "roles/redis.editor",
    "roles/storage.objectAdmin",
    "roles/secretmanager.secretAccessor",
    "roles/logging.logWriter",
    "roles/cloudtrace.agent",
  ]

  web_roles = [
    "roles/secretmanager.secretAccessor",
    "roles/logging.logWriter",
    "roles/cloudtrace.agent",
  ]

  iam_bindings = merge(
    { for role in local.api_roles : "api-${role}" => {
      service_account = google_service_account.api
      role            = role
    } },
    { for role in local.web_roles : "web-${role}" => {
      service_account = google_service_account.web
      role            = role
    } },
  )
}

# -----------------------------------------------------------------------------
# Service Accounts
# -----------------------------------------------------------------------------

resource "google_service_account" "api" {
  project      = var.project_id
  account_id   = "${var.api_service_account_id}-${var.environment}"
  display_name = "Globe CRM API (${var.environment})"
}

resource "google_service_account" "web" {
  project      = var.project_id
  account_id   = "${var.web_service_account_id}-${var.environment}"
  display_name = "Globe CRM Web (${var.environment})"
}

# -----------------------------------------------------------------------------
# IAM Role Bindings
# -----------------------------------------------------------------------------

resource "google_project_iam_member" "bindings" {
  for_each = local.iam_bindings

  project = var.project_id
  role    = each.value.role
  member  = "serviceAccount:${each.value.service_account.email}"
}

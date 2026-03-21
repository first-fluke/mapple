# Artifact Registry for container images

resource "google_artifact_registry_repository" "globe_crm" {
  repository_id = "globe-crm"
  format        = "DOCKER"
  location      = var.region
  description   = "Docker repository for Globe CRM container images"
  labels        = local.labels
}

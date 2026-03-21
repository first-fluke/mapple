output "service_name" {
  description = "Name of the deployed Cloud Run service"
  value       = google_cloud_run_v2_service.main.name
}

output "service_url" {
  description = "HTTPS URL of the deployed Cloud Run service"
  value       = google_cloud_run_v2_service.main.uri
}

output "service_id" {
  description = "Fully qualified resource ID of the Cloud Run service"
  value       = google_cloud_run_v2_service.main.id
}

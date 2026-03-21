output "api_service_account_email" {
  description = "The email address of the API service account"
  value       = google_service_account.api.email
}

output "api_service_account_id" {
  description = "The fully-qualified ID of the API service account"
  value       = google_service_account.api.id
}

output "web_service_account_email" {
  description = "The email address of the Web service account"
  value       = google_service_account.web.email
}

output "web_service_account_id" {
  description = "The fully-qualified ID of the Web service account"
  value       = google_service_account.web.id
}

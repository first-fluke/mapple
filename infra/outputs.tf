output "workload_identity_provider" {
  description = "Full resource name of the Workload Identity Pool Provider"
  value       = google_iam_workload_identity_pool_provider.github.name
}

output "deploy_service_account_email" {
  description = "Email of the GitHub Actions deploy service account"
  value       = google_service_account.github_actions.email
}

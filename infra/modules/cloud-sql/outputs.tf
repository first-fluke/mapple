output "instance_name" {
  description = "Name of the Cloud SQL instance"
  value       = google_sql_database_instance.main.name
}

output "instance_connection_name" {
  description = "Connection name of the Cloud SQL instance (project:region:instance) for Cloud SQL Proxy"
  value       = google_sql_database_instance.main.connection_name
}

output "private_ip_address" {
  description = "Private IP address of the Cloud SQL instance within the VPC"
  value       = google_sql_database_instance.main.private_ip_address
}

output "database_name" {
  description = "Name of the default database created in the Cloud SQL instance"
  value       = google_sql_database.main.name
}

output "database_user" {
  description = "Name of the default database user"
  value       = google_sql_user.main.name
}

output "database_password" {
  description = "Password for the default database user"
  value       = random_password.database.result
  sensitive   = true
}

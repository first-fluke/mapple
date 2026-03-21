output "vpc_id" {
  description = "ID of the VPC network"
  value       = google_compute_network.main.id
}

output "vpc_name" {
  description = "Name of the VPC network"
  value       = google_compute_network.main.name
}

output "vpc_self_link" {
  description = "Self-link URI of the VPC network"
  value       = google_compute_network.main.self_link
}

output "subnet_id" {
  description = "ID of the regional subnet"
  value       = google_compute_subnetwork.main.id
}

output "subnet_name" {
  description = "Name of the regional subnet"
  value       = google_compute_subnetwork.main.name
}

output "vpc_connector_id" {
  description = "ID of the Serverless VPC Access connector"
  value       = google_vpc_access_connector.main.id
}

output "private_service_connection_id" {
  description = "ID of the private service networking connection"
  value       = google_service_networking_connection.main.id
}

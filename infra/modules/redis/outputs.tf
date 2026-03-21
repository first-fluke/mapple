output "instance_name" {
  description = "The name of the Redis instance"
  value       = google_redis_instance.this.name
}

output "host" {
  description = "The IP address of the Redis instance"
  value       = google_redis_instance.this.host
}

output "port" {
  description = "The port number of the Redis instance"
  value       = google_redis_instance.this.port
}

output "auth_string" {
  description = "The AUTH string for the Redis instance"
  value       = google_redis_instance.this.auth_string
  sensitive   = true
}

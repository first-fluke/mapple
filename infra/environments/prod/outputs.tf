output "cloud_sql_instance" {
  description = "Cloud SQL instance connection name"
  value       = module.cloud_sql.instance_connection_name
}

output "cloud_sql_private_ip" {
  description = "Cloud SQL private IP address"
  value       = module.cloud_sql.private_ip_address
}

output "redis_host" {
  description = "Redis instance host"
  value       = module.redis.host
}

output "storage_buckets" {
  description = "Storage bucket names"
  value       = module.cloud_storage.bucket_names
}

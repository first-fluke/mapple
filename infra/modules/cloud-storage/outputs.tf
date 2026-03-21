output "bucket_names" {
  description = "Map of bucket name suffix to the full bucket name."
  value = {
    for suffix, bucket in google_storage_bucket.bucket : suffix => bucket.name
  }
}

output "bucket_urls" {
  description = "Map of bucket name suffix to the gs:// URL."
  value = {
    for suffix, bucket in google_storage_bucket.bucket : suffix => bucket.url
  }
}

output "bucket_self_links" {
  description = "Map of bucket name suffix to the bucket self link."
  value = {
    for suffix, bucket in google_storage_bucket.bucket : suffix => bucket.self_link
  }
}

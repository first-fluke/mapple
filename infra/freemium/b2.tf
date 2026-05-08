resource "b2_bucket" "avatars" {
  bucket_name = "${var.project_prefix}-avatars"
  bucket_type = "allPrivate"
}

resource "b2_application_key" "avatars" {
  key_name     = "${var.project_prefix}-avatars-key"
  bucket_id    = b2_bucket.avatars.bucket_id
  capabilities = ["readFiles", "writeFiles", "listFiles", "deleteFiles"]
}

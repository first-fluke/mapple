terraform {
  backend "gcs" {
    bucket = "globe-crm-tfstate"
    prefix = "env/prod"
  }
}

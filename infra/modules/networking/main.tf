resource "google_compute_network" "main" {
  project                 = var.project_id
  name                    = "${var.vpc_name}-${var.environment}"
  auto_create_subnetworks = false
  routing_mode            = "REGIONAL"
}

resource "google_compute_subnetwork" "main" {
  project                  = var.project_id
  name                     = "${var.vpc_name}-subnet-${var.environment}"
  region                   = var.region
  network                  = google_compute_network.main.id
  ip_cidr_range            = var.subnet_cidr
  private_ip_google_access = true
}

resource "google_compute_global_address" "private_service_range" {
  project       = var.project_id
  name          = "${var.vpc_name}-private-svc-${var.environment}"
  purpose       = "VPC_PEERING"
  address_type  = "INTERNAL"
  prefix_length = tonumber(split("/", var.private_service_cidr)[1])
  address       = split("/", var.private_service_cidr)[0]
  network       = google_compute_network.main.id
}

resource "google_service_networking_connection" "main" {
  network                 = google_compute_network.main.id
  service                 = "servicenetworking.googleapis.com"
  reserved_peering_ranges = [google_compute_global_address.private_service_range.name]

  depends_on = [google_compute_global_address.private_service_range]
}

resource "google_vpc_access_connector" "main" {
  project       = var.project_id
  name          = "globe-crm-conn-${var.environment}"
  region        = var.region
  ip_cidr_range = var.connector_cidr
  network       = google_compute_network.main.name
  machine_type  = "e2-micro"
}

resource "google_compute_router" "main" {
  project = var.project_id
  name    = "${var.vpc_name}-router-${var.environment}"
  region  = var.region
  network = google_compute_network.main.id
}

resource "google_compute_router_nat" "main" {
  project                            = var.project_id
  name                               = "${var.vpc_name}-nat-${var.environment}"
  router                             = google_compute_router.main.name
  region                             = var.region
  nat_ip_allocate_option             = "AUTO_ONLY"
  source_subnetwork_ip_ranges_to_nat = "ALL_SUBNETWORKS_ALL_IP_RANGES"
}

###############################################################################
# Terraform: Public GCS bucket for OSINT challenge (+ indexable contents)
###############################################################################

terraform {
  required_version = ">= 1.5.0"
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 6.0"   # or remove to allow latest
    }
  }
}


# ---------------------- EDIT THESE ----------------------
variable "project_id" {
  description = "GCP Project ID for the CTF challenge"
  type        = string
}

variable "bucket_name" {
  description = "Globally-unique GCS bucket name (e.g., osint-ctf-holiday-2025)"
  type        = string
}

variable "bucket_location" {
  description = "Bucket location/region (e.g., US, ASIA, EU)"
  type        = string
  default     = "ASIA"
}

# Optional: the flag value you want inside the file
variable "flag_value" {
  description = "The flag content to store in flag.txt"
  type        = string
  default     = "flag{Cloud_OSINT_1337}"
}
# --------------------------------------------------------

provider "google" {
  project = var.project_id
}

# Enable the Storage API (just in case it isn't already)
resource "google_project_service" "storage_api" {
  project = var.project_id
  service = "storage.googleapis.com"

  disable_on_destroy = false
}

# Create the bucket with uniform bucket-level access
resource "google_storage_bucket" "ctf_bucket" {
  name     = var.bucket_name
  location = var.bucket_location

  # WARNING: don't set 'public_access_prevention = "enforced"' or you can't make it public
  uniform_bucket_level_access = true

  # Optional: Destroy even if not empty (useful for testing; remove in prod)
  force_destroy = true

  # Optional "static site" hints (main page acts as directory entry for crawlers)
  website {
    main_page_suffix = "index.html"
    not_found_page   = "404.html"
  }

  # Recommended: keep as inherited so public ACLs are allowed
  public_access_prevention = "inherited"
}

# Make objects in this bucket public (read/list) for everyone
# roles/storage.objectViewer includes list & get on objects at the bucket level
resource "google_storage_bucket_iam_binding" "public_read" {
  bucket = google_storage_bucket.ctf_bucket.name
  role   = "roles/storage.objectViewer"
  members = [
    "allUsers",
  ]
}

# (Optional) Some org policies require legacy role for listing via website
# Uncomment if you find listing doesn't work in your org:
# resource "google_storage_bucket_iam_binding" "public_legacy_reader" {
#   bucket = google_storage_bucket.ctf_bucket.name
#   role   = "roles/storage.legacyBucketReader"
#   members = ["allUsers"]
# }

# ---------------------- CONTENTS ------------------------

# Flag file
resource "google_storage_bucket_object" "flag_txt" {
  name         = "flag.txt"
  bucket       = google_storage_bucket.ctf_bucket.name
  content      = var.flag_value
  content_type = "text/plain"
}

# Decoy files
resource "google_storage_bucket_object" "decoy_note" {
  name         = "notes.txt"
  bucket       = google_storage_bucket.ctf_bucket.name
  content      = "todo: clean public bucket before launch\nnothing to see here"
  content_type = "text/plain"
}

resource "google_storage_bucket_object" "decoy_img" {
  name         = "promo.jpg"
  bucket       = google_storage_bucket.ctf_bucket.name
  # Replace with a local file if you want (see commented source example below)
  content      = "fake-jpeg-placeholder"
  content_type = "image/jpeg"

  # Example if you prefer uploading an actual local file:
  # source       = "${path.module}/assets/promo.jpg"
}

# robots.txt to allow indexing
resource "google_storage_bucket_object" "robots" {
  name         = "robots.txt"
  bucket       = google_storage_bucket.ctf_bucket.name
  content      = <<-EOT
    User-agent: *
    Allow: /
  EOT
  content_type = "text/plain"
}

# Optional 404 page (helps website behavior)
resource "google_storage_bucket_object" "not_found" {
  name         = "404.html"
  bucket       = google_storage_bucket.ctf_bucket.name
  content      = <<-EOT
    <!doctype html>
    <html><head><meta charset="utf-8"><title>Not Found</title></head>
    <body><h1>Not Found</h1><p>Try the home page.</p></body></html>
  EOT
  content_type = "text/html"
}

# Index page that links to content (so crawlers can discover files)
resource "google_storage_bucket_object" "index_html" {
  name         = "index.html"
  bucket       = google_storage_bucket.ctf_bucket.name
  content      = <<-EOT
    <!doctype html>
    <html>
      <head>
        <meta charset="utf-8">
        <title>Public Files</title>
      </head>
      <body>
        <h1>Public Files</h1>
        <ul>
          <li><a href="./notes.txt">notes.txt</a></li>
          <li><a href="./promo.jpg">promo.jpg</a></li>
          <!-- maybe your players will miss this one... -->
          <li><a href="./flag.txt">flag.txt</a></li>
          <li><a href="./robots.txt">robots.txt</a></li>
        </ul>
        <p>Generated for a CTF OSINT challenge.</p>
      </body>
    </html>
  EOT
  content_type = "text/html"
}

# ---------------------- OUTPUTS -------------------------

output "bucket_name" {
  value = google_storage_bucket.ctf_bucket.name
}

# Public HTTPS URL for the bucket (objects use /<objectname>)
output "object_base_url" {
  value = "https://storage.googleapis.com/${google_storage_bucket.ctf_bucket.name}"
}

output "index_page_url" {
  value = "https://storage.googleapis.com/${google_storage_bucket.ctf_bucket.name}/index.html"
}

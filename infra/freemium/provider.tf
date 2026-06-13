provider "vercel" {
  # VERCEL_API_TOKEN env var
}

provider "supabase" {
  # SUPABASE_ACCESS_TOKEN env var
}

provider "upstash" {
  # UPSTASH_EMAIL + UPSTASH_API_KEY env vars
}

provider "b2" {
  # B2_APPLICATION_KEY_ID + B2_APPLICATION_KEY env vars
}

provider "cloudflare" {
  # CLOUDFLARE_API_TOKEN env var
  # Token requires: Zone:Read + DNS:Edit scopes on the target zone.
}

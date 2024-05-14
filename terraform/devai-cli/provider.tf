terraform {
  required_providers {
    google = {
      version = ">3.5.0"
    }
  }

  provider_meta "google" {
    module_name = "cloud-solutions/genai-for-developers-v1.2"
  }
}

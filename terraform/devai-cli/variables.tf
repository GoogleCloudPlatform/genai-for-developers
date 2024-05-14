variable "project_id" {
  description = "Value of the Project Id to deploy the solution"
  type        = string
}
variable "location" {
  description = "Location of where the BigQuery data should be stored, use US or EU for multi-region storage, or use any other region id for single region storage."
  type        = string
  default = "us-central1"
}

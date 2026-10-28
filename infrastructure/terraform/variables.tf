variable "region" { default = "us-east-1" }
variable "db_password" { sensitive = true }
variable "image" { description = "Backend container image" }

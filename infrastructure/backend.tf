terraform {
  backend "s3" {
    bucket = ""
    key    = "scant/terraform.tfstate"
    region = "us-east-1"
  }
}
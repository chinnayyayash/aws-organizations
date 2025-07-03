provider "aws" {
  region = "${var.aws_region}" # Organizations API is only available in us-east-1
}

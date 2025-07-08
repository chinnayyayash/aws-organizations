variable "aws_region" {
  description = "The Home Region for Control Tower, must be us-east-1"
  type        = string
  default     = "us-east-1"

  validation {
    condition     = var.aws_region == "us-east-1"
    error_message = "Region must be home region of control tower, us-east-1"
  }

}
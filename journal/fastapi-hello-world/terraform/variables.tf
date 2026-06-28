variable "aws_profile" {
  type        = string
  description = "Local AWS CLI profile used by Terraform."
  default     = "intern-deploy"
}

variable "region" {
  type        = string
  description = "AWS region to deploy into."
  default     = "ap-southeast-2"
}

variable "project_name" {
  type        = string
  description = "Name prefix for AWS resources."
  default     = "intern-api"
}

variable "owner" {
  type        = string
  description = "Owner tag for resources."
  default     = "austin-nguyen"
}

variable "instance_type" {
  type        = string
  description = "EC2 instance type. Confirm free-tier or credit eligibility before apply."
  default     = "t3.micro"
}

variable "key_name" {
  type        = string
  description = "EC2 key pair name used for SSH."
}

variable "allowed_ssh_cidr" {
  type        = string
  description = "Your current public IPv4 CIDR, for example 42.117.192.250/32."
}

variable "image_uri" {
  type        = string
  description = "Public Docker image URI for the FastAPI app."
}

variable "jwt_secret" {
  type        = string
  description = "JWT secret for the deployed API. Use a throwaway training secret."
  sensitive   = true
}

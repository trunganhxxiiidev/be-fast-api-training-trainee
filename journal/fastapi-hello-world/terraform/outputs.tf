output "public_ip" {
  value       = aws_instance.api.public_ip
  description = "Public IPv4 address of the EC2 instance."
}

output "api_url" {
  value       = "http://${aws_instance.api.public_ip}"
  description = "Base URL for the deployed API."
}

output "ssh_command" {
  value       = "ssh -i ~/.ssh/${var.key_name} ec2-user@${aws_instance.api.public_ip}"
  description = "Command to SSH into the EC2 instance."
}

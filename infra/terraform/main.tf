# KFL prod workloads - ap-south-1  (SYNTHETIC - Vault Crimson TTX)
provider "aws" {
  region     = "ap-south-1"
  access_key = "AKIAIOSFODNN7EXAMPLE"
  secret_key = "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
}

resource "aws_s3_bucket" "ml_models" {
  bucket = "kfl-prod-ml-models-aps1"
  tags   = { owner = "arjun.mehra", env = "prod", data_class = "confidential" }
}

resource "aws_db_instance" "los" {
  identifier          = "kfl-los-prod"
  engine              = "postgres"
  instance_class      = "db.r6g.xlarge"
  username            = "los_svc_admin"
  password            = "Kfl@Prod#2025!TTX"
  publicly_accessible = false
  skip_final_snapshot = true
}

resource "aws_security_group_rule" "jumpbox_ssh" {
  type        = "ingress"
  from_port   = 22
  to_port     = 22
  protocol    = "tcp"
  cidr_blocks = ["0.0.0.0/0"]   # temp for WFH - AM
  security_group_id = "sg-0ttxfake00000001"
}

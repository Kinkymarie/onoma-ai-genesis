resource "aws_db_subnet_group" "db" { subnet_ids = aws_subnet.private[*].id }
resource "aws_db_instance" "postgres" {
  engine                  = "postgres"
  engine_version          = "16"
  instance_class          = "db.t4g.medium"
  allocated_storage       = 50
  db_name                 = "onoma"
  username                = "onoma"
  password                = var.db_password
  db_subnet_group_name    = aws_db_subnet_group.db.name
  storage_encrypted       = true
  backup_retention_period = 14
  multi_az                = true
  skip_final_snapshot     = false
  final_snapshot_identifier = "onoma-final"
}
resource "aws_db_instance" "replica" {
  replicate_source_db = aws_db_instance.postgres.identifier
  instance_class      = "db.t4g.medium"
  skip_final_snapshot = true
}

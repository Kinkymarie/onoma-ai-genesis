resource "aws_elasticache_subnet_group" "redis" { name = "onoma-redis" subnet_ids = aws_subnet.private[*].id }
resource "aws_elasticache_cluster" "redis" {
  cluster_id           = "onoma"
  engine               = "redis"
  node_type            = "cache.t4g.small"
  num_cache_nodes      = 1
  subnet_group_name    = aws_elasticache_subnet_group.redis.name
}

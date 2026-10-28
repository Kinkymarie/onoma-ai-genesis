resource "aws_ecs_cluster" "main" { name = "onoma" }
resource "aws_ecs_task_definition" "backend" {
  family                   = "onoma-backend"
  requires_compatibilities = ["FARGATE"]
  network_mode             = "awsvpc"
  cpu                      = 512
  memory                   = 1024
  execution_role_arn       = aws_iam_role.task_exec.arn
  container_definitions = jsonencode([{
    name = "backend", image = var.image, essential = true
    portMappings = [{ containerPort = 8000 }]
    environment = [
      { name = "APP_ENV", value = "production" },
      { name = "REDIS_URL", value = "redis://${aws_elasticache_cluster.redis.cache_nodes[0].address}:6379/0" }
    ]
  }])
}
resource "aws_ecs_service" "backend" {
  name            = "backend"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.backend.arn
  desired_count   = 2
  launch_type     = "FARGATE"
  network_configuration { subnets = aws_subnet.private[*].id }
  load_balancer {
    target_group_arn = aws_lb_target_group.backend.arn
    container_name   = "backend"
    container_port   = 8000
  }
}

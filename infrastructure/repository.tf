resource "aws_ecr_repository" "scanner" {
  name                 = "scant/scanner"
  image_tag_mutability = "MUTABLE"
}

resource "aws_ecr_lifecycle_policy" "scanner" {
  repository = aws_ecr_repository.scanner.name

  policy = jsonencode({
    rules = [
      {
        rulePriority = 1,
        description  = "Keep only 1 untagged image",
        selection = {
          tagStatus   = "untagged",
          countType   = "imageCountMoreThan",
          countNumber = 1
        },
        action = {
          type = "expire"
        }
      }
    ]
  })
}

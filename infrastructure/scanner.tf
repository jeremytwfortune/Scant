resource "aws_cloudwatch_log_group" "scanner" {
  name              = "/aws/lambda/scant-scanner"
  retention_in_days = 7
}

resource "aws_lambda_function" "scanner" {
  function_name = "scant-scanner"
  timeout       = 120
  memory_size   = 2048
  role          = aws_iam_role.scanner.arn
  image_uri     = "${aws_ecr_repository.scanner.repository_url}:latest"
  package_type  = "Image"
  image_config {
    command = ["scant.lambda_function.lambda_handler"]
  }
  environment {
    variables = {
      SCANT_WATERMARK_NAME      = aws_ssm_parameter.watermark.name
      SCANT_AUTHENTICATION_NAME = aws_secretsmanager_secret.authentication.name
    }
  }
}

resource "aws_lambda_function_event_invoke_config" "scanner" {
  function_name          = aws_lambda_function.scanner.function_name
  maximum_retry_attempts = 0
}

resource "aws_scheduler_schedule" "scanner" {
  name                = "scant-scanner"
  schedule_expression = "rate(3 minutes)"

  target {
    arn      = aws_lambda_function.scanner.arn
    role_arn = aws_iam_role.scheduler.arn

    retry_policy {
      maximum_event_age_in_seconds = 60
      maximum_retry_attempts       = 1
    }
  }

  flexible_time_window {
    mode                      = "FLEXIBLE"
    maximum_window_in_minutes = 2
  }
}

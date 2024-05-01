resource "aws_cloudwatch_log_group" "scanner" {
  name              = "/aws/lambda/scanner"
  retention_in_days = 7
}

resource "aws_lambda_function" "scanner" {
  function_name    = "scanner"
  handler          = "scant.lambda_function.lambda_handler"
  runtime          = "python3.12"
  timeout          = 30
  memory_size      = 1024
  role             = aws_iam_role.scanner.arn
  filename         = var.lambda_zip_file
  source_code_hash = filebase64sha256(var.lambda_zip_file)

  environment {
    variables = {
      SCANT_WATERMARK_NAME      = aws_ssm_parameter.watermark.name
      SCANT_AUTHENTICATION_NAME = aws_secretsmanager_secret.authentication.name
    }
  }
}
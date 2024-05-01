data "aws_iam_policy_document" "lambda_assume" {
  statement {
    actions = ["sts:AssumeRole"]
    principals {
      type        = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }
  }
}

resource "aws_iam_role" "scanner" {
  name               = "scant-scanner"
  assume_role_policy = data.aws_iam_policy_document.lambda_assume.json
}

data "aws_iam_policy_document" "scanner" {
  statement {
    actions = [
      "logs:CreateLogGroup",
      "logs:CreateLogStream",
      "logs:PutLogEvents",
    ]
    resources = [
      aws_cloudwatch_log_group.scanner.arn,
      "${aws_cloudwatch_log_group.scanner.arn}:*",
    ]
  }

  statement {
    actions = [
      "ssm:GetParameter",
      "ssm:GetParameters",
      "ssm:GetParametersByPath",
      "ssm:PutParameter",
    ]
    resources = [
      aws_ssm_parameter.watermark.arn
    ]
  }

  statement {
    actions = [
      "secretsmanager:GetSecretValue",
      "secretsmanager:DescribeSecret",
    ]
    resources = [replace(aws_secretsmanager_secret.authentication.arn, "/-.{6}$/", "-*")]
  }
}

resource "aws_iam_role_policy" "scanner" {
  name   = "scanner"
  role   = aws_iam_role.scanner.id
  policy = data.aws_iam_policy_document.scanner.json
}

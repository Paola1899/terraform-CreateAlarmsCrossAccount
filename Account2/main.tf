provider "aws" {
    region = "us-east-1"
    
    default_tags {
        tags = {
          CreatedBy = "Terraform"
        }
    }
}

variable "sqs_event" {}

resource "aws_lambda_function" "create_alarm" {
    function_name = "CreateAlarmsEC2Instances"
    description = "Lambda Function encargada de generar alarmas"
    
    role = aws_iam_role.iam_for_lambda.arn
    handler = "cloudwatch_alarms.lambda_handler"
    runtime = "python3.9"
    memory_size = 1024
    timeout = 870
    
    filename = "${path.module}/lambda.zip"
    source_code_hash = "${base64sha256("lambda.zip")}"
}

resource "aws_lambda_event_source_mapping" "example" {
  event_source_arn = var.sqs_event
  function_name    = aws_lambda_function.create_alarm.arn
}

resource "aws_iam_role" "iam_for_lambda" {
  name = "AWSLambdaRoleforCloudWatchAutomationAlarms"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
            Service = [
                "lambda.amazonaws.com",
                "sqs.amazonaws.com"
            ]
        }
      }
    ]
  })
}

resource "aws_iam_policy" "cloudwatch" {
    name = "CloudwatchLambdaPolicy"
    
    policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = [
          "sns:*",
          "cloudwatch:*",
          "logs:*"
        ]
        Effect = "Allow"
        Resource = "*"
      }
    ]
  })
}


resource "aws_iam_role_policy_attachment" "attach_policy1" {
  role       = aws_iam_role.iam_for_lambda.name
  policy_arn = aws_iam_policy.cloudwatch.arn
}

resource "aws_iam_role_policy_attachment" "attach_policy2" {
  role       = aws_iam_role.iam_for_lambda.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}
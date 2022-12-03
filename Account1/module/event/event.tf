variable "lambda_arn" {}
variable "sqs_name" {}

data "aws_caller_identity" "current" {}

locals {
    account_id = data.aws_caller_identity.current.account_id
}

resource "aws_cloudwatch_event_rule" "console" {
    name = "CreateAlarmsEventSchedule"
    description = "Evento recurrente para la revisión de nuevas instancias generadas"
    
    schedule_expression = "cron(0 8 ? * MON-FRI *)"
}

resource "aws_cloudwatch_event_target" "example" {
  rule = aws_cloudwatch_event_rule.console.name
  arn  = var.lambda_arn
  role_arn = var.event_role_arn
  input = <<DOC
{ 
    "queue_name": "${var.sqs_name}" 
}
  DOC
}

resource "aws_iam_role" "event_role" {
    name = "EventBridgeSchedulerLambdaRole"
    path = "/"
    assume_role_policy = <<EOF
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Principal": {
                "Service": "scheduler.amazonaws.com"
            },
            "Action": "sts:AssumeRole",
            "Condition": {
                "StringEquals": {
                    "aws:SourceAccount": "${local.account_id}",
                    "aws:SourceArn": "${aws_cloudwatch_event_rule.console.arn}"
                }
            }
        }
    ]
}
    EOF
}

resource "aws_iam_policy" "event_policy" {
    name = "EventBridgeSchedulerLambdaPolicy"
    
    policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = [
          "lambda:InvokeFunction"
        ]
        Effect = "Allow"
        Resource = [
            "${var.lambda_arn}*",
            "${var.lambda_arn}"
        ]
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "attach_policy_event" {
  role       = aws_iam_role.event_role.name
  policy_arn = aws_iam_policy.event_policy.arn
}

output "event_scheduler_arn" {
    value = aws_cloudwatch_event_rule.console.arn
}
variable "event_scheduler" {}

resource "aws_lambda_function" "create_alarm" {
    function_name = "ConfigAgentsEC2Instances"
    description = "Lambda funtion usada para configurar agente ssm y cloudwatch dentro de la instancia"
    
    role = aws_iam_role.lambda_role.arn
    handler = "ssm_function.lambda_handler"
    runtime = "python3.9"
    memory_size = 1024
    timeout = 870
    
    filename = "${path.module}/lambda.zip"
    source_code_hash = "${base64sha256("lambda.zip")}"
}

resource "aws_lambda_permission" "create_alarm" {
    statement_id  = "CreateCloudWatchAlarmForInstances"
    action        = "lambda:InvokeFunction"
    function_name = aws_lambda_function.create_alarm.function_name
    principal     = "events.amazonaws.com"
    source_arn    = var.event_scheduler
}

resource "aws_iam_role" "lambda_role" {
    name = "AWSLambdaRoleforSSM"
    path = "/"
    assume_role_policy = <<EOF
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect":"Allow",
            "Principal": {
                "Service": [
                    "lambda.amazonaws.com",
                    "sqs.amazonaws.com",
                ]
            },
            "Action":[
                "sts:AssumeRole"
            ]
        }
    ]
}
    EOF
}

resource "aws_iam_policy" "cloudwatch" {
    name = "CloudwatchLambdaPolicy"
    
    policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = [
          "ec2:*",
          "iam:ListAccountAliases",
          "organizations:DescribeAccount"
        ]
        Effect = "Allow"
        Resource = "*"
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "attach_policy1" {
  role       = aws_iam_role.lambda_role.name
  policy_arn = aws_iam_policy.cloudwatch.arn
}

resource "aws_iam_role_policy_attachment" "attach_policy2" {
  role       = aws_iam_role.lambda_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_iam_role_policy_attachment" "attach_policy3" {
  role       = aws_iam_role.lambda_role.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonSSMFullAccess"
}

resource "aws_iam_role_policy_attachment" "attach_policy4" {
  role       = aws_iam_role.lambda_role.name
  policy_arn = "arn:aws:iam::aws:policy/AWSLambdaSQSQueueExecutionRole"
}

output "create_alarm_arn" {
    value = aws_lambda_function.create_alarm.arn
}
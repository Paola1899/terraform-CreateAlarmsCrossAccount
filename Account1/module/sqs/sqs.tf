variable "OperationsLambdaRoleARN" {}

resource "aws_sqs_queue" "terraform_queue" {
    name = "InvokeLambdaCrossAccountAlarms"
}

/*resource "aws_sqs_queue_policy" "test" {
  queue_url = aws_sqs_queue.terraform_queue.id

  policy = <<EOF
{
  "Version": "2012-10-17",
  "Id": "sqspolicy",
  "Statement": [
    {
      "Sid": "LAMBDACROSSACCOUNT",
      "Effect": "Allow",
      "Principal": {
        "AWS": [
          "${var.OperationsLambdaRoleARN}"
        ]
      },
      "Action": "sqs:*",
      "Resource": "${aws_sqs_queue.terraform_queue.arn}"
    }
  ]
}
EOF
}*/

output "sqs_name" {
  value = aws_sqs_queue.terraform_queue.name
}

output "sqs_arn" {
  value = aws_sqs_queue.terraform_queue.arn
}
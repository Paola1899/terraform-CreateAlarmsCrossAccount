provider "aws" {
    region = "us-east-1"
    
    default_tags {
        tags = {
          CreatedBy = "Terraform"
        }
    }
}

module "event" {
    source = "./module/event"
    
    lambda_arn = module.lambda.create_alarm_arn
    sqs_name = module.sqs.sqs_name
}

module "sqs" {
    source = "./module/sqs"
    
    //OperationsLambdaRoleARN = ""
}

module "lambda" {
    source = "./module/lambda"
    
    event_scheduler = module.event.event_scheduler_arn
}

module "ssm" {
    source = "./module/ssm"
}

output "sqs_event_arn" {
    value = module.sqs.sqs_arn
}
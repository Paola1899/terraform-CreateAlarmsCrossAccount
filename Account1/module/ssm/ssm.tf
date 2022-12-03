resource "aws_ssm_parameter" "linux" {
  name  = "AmazonCloudWatch-Linux"
  type  = "String"
  tier = "Advanced"
  description = "Default cloudwatch setup configuration file for linux."
  value = "${path.module}/file/linux.json"
}

resource "aws_ssm_parameter" "windows" {
  name  = "AmazonCloudWatch-Windows"
  type  = "String"
  tier = "Advanced"
  description = "Default cloudwatch setup configuration file for windows."
  
  value = "${path.module}/file/windows.json"
}

resource "aws_iam_instance_profile" "prueba" {
    name = aws_iam_role.AWSEC2DefaultRole.name
    role = aws_iam_role.AWSEC2DefaultRole.name
}

resource "aws_iam_role" "AWSEC2DefaultRole" {
    name = "AWSEC2SSMRole"
    path = "/"
    assume_role_policy = jsonencode({
        Version = "2012-10-17"
        Statement = [
          {
            Action = "sts:AssumeRole"
            Effect = "Allow"
            Principal = {
              Service= [
                "ec2.amazonaws.com"
              ]
            }
          },
        ]
    })
}

resource "aws_iam_role_policy_attachment" "role_ec2_cw" {
    role = aws_iam_role.AWSEC2DefaultRole.name
    policy_arn = "arn:aws:iam::aws:policy/CloudWatchAgentServerPolicy"
}

resource "aws_iam_role_policy_attachment" "role_ec2_ssm" {
    role = aws_iam_role.AWSEC2DefaultRole.name
    policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonEC2RoleforSSM"
}

resource "aws_iam_role_policy_attachment" "role_ec2_ssm-2" {
    role = aws_iam_role.AWSEC2DefaultRole.name
    policy_arn = "arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore"
}
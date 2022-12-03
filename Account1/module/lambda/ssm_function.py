import boto3
import json
import datetime
import os
import time
from botocore.exceptions import ClientError
# Create CloudWatch client
cloudwatch = boto3.client('cloudwatch')
ec2 = boto3.resource('ec2')
ssm = boto3.client('ssm')
sns = boto3.client('sns')
client = boto3.client('ec2')
accountid = boto3.client('sts').get_caller_identity().get('Account')
alias = boto3.client('organizations').describe_account(AccountId=accountid).get('Account').get('Name')
lambda_client = boto3.client('lambda')
sqs = boto3.client('sqs')

def lambda_handler(event, context):
    print('Filters instances')
    instances = ec2.instances.filter(
        Filters=[{'Name': 'instance-state-name', 'Values': ['running']}]
    )
    for instance in instances:
        if instance.iam_instance_profile is not None:
            if 'Alarms' not in [tag['Key'] for tag in instance.tags]:
                print('Iam Instance Profile detectado con arn: ' + instance.iam_instance_profile['Arn'])
                print('Alarmas no configuradas para la instancia:' + get_instance_name(ec2.Instance(instance.id)))
                print("installing and configuring Cloudwatch agents on the instance : " + get_instance_name(ec2.Instance(instance.id)))
                install_and_configure_cwagent(instance.id)
                image = get_image_id(instance.id)
                ins_type = get_instance_type(instance.id)
                name = get_instance_name(instance)
                queue = sqs.get_queue_url(QueueName = event['queue_name'])
                body = {
                    "instance": instance.id, 
                    "accountid": accountid,
                    "instance_type": ins_type,
                    "instance_image": image,
                    "instance_name": name,
                    "account_name": alias
                }
                print('SQS Invoke LambdaCreateAlarmsEC2Instance')
                print(json.dumps(body))
                response = sqs.send_message(
                    QueueUrl = queue,
                    MessageBody = (json.dumps(body)),
                    DelaySeconds = 10,
                )
                print('Atachando Tag de Alarmas creadas')
                ec2.create_tags(Resources=[instance.id], Tags=[{'Key':'Alarms', 'Value':'True'}])
                print('Los Agentes han sido configurados exitosamente en la instancia, validar la creación de alarmas en la cuenta de Monitoreo')
            else:
                print('Las alarmas ya han sido configuradas previamente en la instancia: ' + get_instance_name(ec2.Instance(instance.id)))
                print('Si las alarmas no se encuentran en la cuenta de monitoreo, favor eliminar tag de alarmas creadas en la instancia y esperar la proxima ejecución.')
        else:
            print('Instance Profile no configurado para '+ get_instance_name(ec2.Instance(instance.id)) + ' validar la configuración de la instancia')
            
    return {
        'statusCode': 200,
        'body': json.dumps('Ejecucion Exitosa!')
    }

def get_instance_name(instance):
  instanceName = ''
  for tag in instance.tags:
      if (tag['Key']=="Name"):
        instanceName = tag['Value']
        return instanceName
 
def install_and_configure_cwagent(instanceId):
    print('========== Instances to install Cloudwatch Agents:')
    print(instanceId)
  # install cloudwatch agents using SSM automation
    ssm.send_command(
            InstanceIds=[instanceId],
            DocumentName='AWS-ConfigureAWSPackage',
            Parameters={
                "action": ["Install"],
                "installationType":["Uninstall and reinstall"],
                "name":["AmazonCloudWatchAgent"]
            }
        )
    # configure cloudwatch agents on windows servers using powershell
    commands = [
            "cd “C:\Program Files\Amazon\AmazonCloudWatchAgent\”", ".\\amazon-cloudwatch-agent-ctl.ps1 -a fetch-config -m ec2 -c ssm:AmazonCloudWatch-windows", ""
            ]
    send_run_command(instanceId,commands)
   
    
def send_run_command(instance_ids, commands):
    """
    Tries to queue a RunCommand job.  If a ThrottlingException is encountered
    recursively calls itself until success.
    """
    try:
        ssm.send_command(
            InstanceIds=[instance_ids],
            DocumentName='AWS-RunPowerShellScript',
            Parameters={
                'commands': commands,
                'executionTimeout': ['600'] # Seconds all commands have to complete in
            }
        )
        print('============RunCommand sent successfully')
        return True
    except ClientError as err:
        if 'ThrottlingException' in str(err):
            print("RunCommand throttled, automatically retrying...")
            send_run_command(instance_ids, commands)
        else:
            print("Run Command Failed!\n%s", str(err))
            return False

def get_instance_type(instanceId):
  instance_type = ''
  response = client.describe_instances(InstanceIds=[instanceId,])
  instance_type = response['Reservations'][0]['Instances'][0]['InstanceType']
  return instance_type
 
def get_image_id(instanceId):
  image_id = ''
  response = client.describe_instances(InstanceIds=[instanceId,])
  image_id = response['Reservations'][0]['Instances'][0]['ImageId']
  return image_id
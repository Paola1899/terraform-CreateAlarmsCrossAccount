import boto3 
import json
import datetime
import os
import time
from botocore.exceptions import ClientError
# Create CloudWatch client
cloudwatch = boto3.client('cloudwatch')
def lambda_handler(event, context):
    for record in event['Records']:
      print(record['body'])
      body = json.loads(record['body'])
      print(body)
      instanceID = body['instance']
      accountID = body['accountid']
      account_NAME = body['account_name']
      instanceTYPE = body['instance_type']
      instanceIMAGE = body['instance_image']
      instanceNAME = body['instance_name']
      print('Successfully processed %s records.' % str(len(event['Records'])))
      #sns_topic_arn = ''
      create_alarms(instanceID, accountID, account_NAME, instanceTYPE, instanceNAME, instanceIMAGE)
      print('Alarmas creadas con exito!')
    return {
      'statusCode': 200,
      'body': json.dumps('Alarmas creadas con exito!')
    }

def create_alarms(instanceID, accountID, account_NAME, instanceTYPE, instanceNAME, instanceIMAGE):
    print("Creating Alarms for instance :" + instanceID)
    create_alarms_for_instance(instanceID, accountID, account_NAME, instanceTYPE, instanceNAME, instanceIMAGE)
 
def create_alarms_for_instance(instanceID, accountID, account_NAME, instanceTYPE, instanceNAME, instanceIMAGE):
    instance_type = instanceTYPE
    image_id = instanceIMAGE
    cloudwatch.put_metric_alarm(
                      AlarmName= instanceNAME + account_NAME + '- C:/ Disk utilization > 90%' ,
                      ComparisonOperator='LessThanThreshold',
                      EvaluationPeriods=1,
                      Threshold=10.0,
                      ActionsEnabled=False,
                      AlarmDescription='Alarm triggers when disk space of C:/ Drive on this instance exceeds 90% utilization',
                      TreatMissingData="missing",
                      #AlarmActions=[ sns_topic_arn ],
                      Metrics = [
                        {
                          'Id': 'cloudwatch_disk',
                          'MetricStat': {
                            'Metric': {
                                'Namespace': 'CWAgent',
                                'MetricName': 'LogicalDisk % Free Space',
                                'Dimensions': [
                                    {
                                      'Name': 'InstanceId',
                                      'Value': instanceID
                                    },
                                    {
                                      'Name':'instance',
                                      'Value': 'C:'
                                    },
                                    {
                                      'Name':'objectname',
                                      'Value': 'LogicalDisk'
                                    },
                                    {
                                      'Name': 'ImageId',
                                      'Value': image_id
                                    },
                                    {
                                      'Name': 'InstanceType',
                                      'Value': instance_type
                                    }
                                ]
                            },
                            'Stat':'Average',
                            'Period': 60
                          },
                          'AccountId': accountID,
                        }
                      ]
                  )
    cloudwatch.put_metric_alarm(
                      AlarmName= instanceNAME + account_NAME +  '- CPU Utilization > 85%' ,
                      ComparisonOperator='GreaterThanThreshold',
                      EvaluationPeriods=1,
                      Threshold=85.0,
                      ActionsEnabled=False,
                      AlarmDescription='Alarm triggers when CPU Utilization  on this instance exceeds 90% utilization',
                      TreatMissingData="missing",
                      #AlarmActions=[ sns_topic_arn],
                      Metrics = [
                        {
                          'Id': 'cloudwatch_cpu',
                          'MetricStat': {
                            'Metric': {
                                'Namespace': 'AWS/EC2',
                                'MetricName': 'CPUUtilization',
                                'Dimensions': [
                                    {
                                      'Name': 'InstanceId',
                                      'Value': instanceID
                                    }
                                ]
                            },
                            'Period': 60,
                            'Stat':'Average'
                          },
                          'AccountId': accountID,
                        }
                      ],
                  )
    cloudwatch.put_metric_alarm(
                      AlarmName= instanceNAME + account_NAME + '- Processor Utilization time > 90%' ,
                      ComparisonOperator='GreaterThanThreshold',
                      EvaluationPeriods=1,
                      Threshold=90.0,
                      ActionsEnabled=False,
                      AlarmDescription='Alarm triggers when Processor time on this instance exceeds 90% utilization',
                      TreatMissingData="notBreaching",
                      #AlarmActions=[ sns_topic_arn],
                      Metrics = [
                        {
                          'Id': 'cloudwatch_utime',
                          'MetricStat': {
                            'Metric': {
                                'Namespace': 'CWAgent',
                                'MetricName': 'Processor % User Time',
                                'Dimensions': [
                                    {
                                      'Name': 'InstanceId',
                                      'Value': instanceID
                                    },
                                    {
                                      'Name':'objectname',
                                      'Value': 'Processor'
                                    },
                                    {
                                      'Name': 'ImageId',
                                      'Value': image_id
                                    },
                                   {
                                      'Name': 'InstanceType',
                                      'Value': instance_type
                                    }
                                ]
                            },
                            'Period': 60,
                            'Stat':'Average'
                          },
                          'AccountId': accountID,
                        }
                      ]
                  )
    cloudwatch.put_metric_alarm(
                      AlarmName= instanceNAME + account_NAME + '- Memory Utilization > 90%' ,
                      ComparisonOperator='GreaterThanThreshold',
                      EvaluationPeriods=1,
                      Threshold=90.0,
                      ActionsEnabled=False,
                      AlarmDescription='Alarm triggers when memory utilization on this instance exceeds 90% utilization',
                      TreatMissingData="missing",
                      #AlarmActions=[sns_topic_arn],
                      Metrics = [
                        {
                          'Id': 'cloudwatch_ram',
                          'MetricStat': {
                            'Metric': {
                                'Namespace': 'CWAgent',
                                'MetricName': 'Memory % Committed Bytes In Use',
                                'Dimensions': [
                                    {
                                      'Name': 'InstanceId',
                                      'Value': instanceID
                                    },
                                    {
                                      'Name':'objectname',
                                      'Value': 'Memory'
                                    },
                                    {
                                      'Name': 'ImageId',
                                      'Value': image_id
                                    },
                                    {
                                      'Name': 'InstanceType',
                                      'Value': instance_type
                                    }
                                ]
                            },
                            'Period': 60,
                            'Stat':'Average'
                          },
                          'AccountId': accountID,
                        }
                      ]
                  )
                 
    cloudwatch.put_metric_alarm(
                      AlarmName= instanceNAME + account_NAME + '- Status check FAILED' ,
                      ComparisonOperator='GreaterThanThreshold',
                      EvaluationPeriods=1,
                      Threshold=1,
                      ActionsEnabled=False,
                      AlarmDescription='Alarm triggers when instance status check fails or when instance is not reachable',
                      TreatMissingData="missing",
                      #AlarmActions=[sns_topic_arn],
                      Metrics = [
                        {
                          'Id': 'cloudwatch_check',
                          'MetricStat': {
                            'Metric': {
                                'Namespace': 'AWS/EC2',
                                'MetricName': 'StatusCheckFailed_Instance',
                                'Dimensions': [
                                    {
                                      'Name': 'InstanceId',
                                      'Value': instanceID
                                    }
                                ]
                            },
                            'Period': 60,
                            'Stat':'Average'
                          },
                          'AccountId': accountID,
                        }
                      ]
                  )
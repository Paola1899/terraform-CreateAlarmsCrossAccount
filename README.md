# terraform-CreateAlarmsCrossAccount
ACCOUNT 1
    -Amazon EventBridge
    -AWS Lambda
    -AWS SQS
    -AWS SSM
    -IAM
    
En esta cuenta se configura la automatización para la instalación de los agentes de system manager y cloudwatch, a traves de la función lambda. Esta función, es invocada por un evento programado todos los dias a las 20 horas.

Una vez configurados los agentes, la función lambda envia invoca un evento sqs que posteriormente invoca la función lambda ubicada en ACCOUNT 2.
ACCOUNT 2
    -AWS Lambda
    -IAM
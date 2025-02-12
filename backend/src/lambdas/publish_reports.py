# Python imports
# import asyncio
# Python imports
import json
import os
import time

# Pip imports
import boto3


sqs = boto3.client('sqs')

STAGE = os.environ.get("STAGE", "dev")


def lambda_handler(event):
    # Extract query parameters from API Gateway event
    params = event.get('queryStringParameters', {})

    # Construct JSON object with query parameters
    query_params_json = {
        "query": params.get('query'),
        "run_by": params.get('run_by'),
        "begin_date": params.get('begin_date'),
        "end_date": params.get('end_date'),
        "conditions": params.get('conditions'),
        "productTypes": params.get('productTypes'),
        "account_id": params.get('account_id'),
        "statuses": params.get('statuses'),
        "states": params.get('states'),
        "role_id": params.get('role_id'),
        "purchase_type": params.get("purchase_type"),
        "vendors": params.get("vendors"),
        "order_ids": params.get("order_ids"),
        "manager": params.get("manager"),
        "can_read_all": params.get("can_read_all"),
        "user_id": params.get("user_id"),
        "purchase_types": params.get("purchase_types")
    }

    # Publish JSON object to SQS queue
    queue_url = f'https://sqs.us-west-2.amazonaws.com/721398480587/reports-{STAGE}'
    sqs.send_message(QueueUrl=queue_url, MessageBody=json.dumps(query_params_json))
    time.sleep(1.2)
    sqs.send_message(QueueUrl=queue_url, MessageBody=json.dumps(query_params_json))

    return {'statusCode': 200, 'body': json.dumps('Query parameters published to SQS successfully')}


def handler(event, context):
    result = lambda_handler(event)

    # Return the result of lambda_handler as the body of the HTTP response
    return {'statusCode': result['statusCode'], 'body': result['body']}

import json
import urllib.parse
import boto3
from . import utils

secret_name = "event_trigger_tutorial_lambda_example_secret"
region_name = "ap-southeast-1"

s3_client = boto3.client('s3')
    # Create a Secrets Manager client
session = boto3.session.Session()
secret_client = session.client(
    service_name='secretsmanager',
    region_name=region_name
)


def lambda_handler(event, context):

    # Get the secret from Secrets Manager
    secret = utils.get_secret(secret_client,secret_name)

    bucket = event['Records'][0]['s3']['bucket']['name']
    s3_key = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'], encoding='utf-8')

    try:
        json_path = utils.download_file_from_s3(s3_client,bucket, s3_key)
        data = utils.open_json_file(json_path)
        json_string = json.dump(data, data,indent=4)
        print(json_string)

    except Exception as e:
        print(e)
        print('Error getting object {} from bucket {}.'.format(s3_key, bucket))
        raise e
    



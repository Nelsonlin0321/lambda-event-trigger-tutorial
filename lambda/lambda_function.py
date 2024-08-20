import os
import json
import urllib.parse
import boto3
from pymongo import MongoClient
from botocore.exceptions import ClientError


env = os.getenv('env')

mongodb_url_secret = f"{env}/mongodb_url"
region_name = "ap-southeast-1"

s3_client = boto3.client('s3')
    # Create a Secrets Manager client
session = boto3.session.Session()
secret_client = session.client(
    service_name='secretsmanager',
    region_name=region_name
)


def handler(event, context):

    # Get the secret from Secrets Manager
    mongodb_url = get_secret(secret_client,mongodb_url_secret)
    mongodb_client = MongoClient(mongodb_url)
    mongodb_db = mongodb_client.client["search"]
    print("Get mongodb_url secret from Secrets Manager successfully")

    bucket = event['Records'][0]['s3']['bucket']['name']
    s3_key = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'], encoding='utf-8')

    try:
        json_path = download_file_from_s3(s3_client,bucket, s3_key)
        data = open_json_file(json_path)

        collection = mongodb_db['lambda_tutorial']
        results = collection.insert_many(data)
        print(f'Inserted {results.inserted_ids} documents into the database.')

        json_string = json.dump(data, data,indent=4)
        print("Inserted Data:",json_string)

    except Exception as e:
        print(e)
        print('Error getting object {} from bucket {}.'.format(s3_key, bucket))
        raise e
    
    return {
       "statusCode": 200,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps({"message":'data inserted successfully into MongoDB'}), 
    }
    


def get_secret(secret_client,secret_name):
    try:
        get_secret_value_response = secret_client.get_secret_value(
            SecretId=secret_name
        )
    except ClientError as e:
        raise e
    secret = get_secret_value_response['SecretString']
    return secret 

def download_file_from_s3(s3_client,bucket, s3_key):

    file_name = os.path.basename(s3_key)
    file_path  =  f'/tmp/{file_name}'
    try:
        s3_client.download_file(bucket, s3_key,file_path)
        print('Successfully downloaded file from S3.')
    except ClientError as e:
        if e.response['Error']['Code'] == '404':
            print("The object does not exist.")
        else:
            raise
    
    return file_path



def open_json_file(json_file):
    with open(json_file, 'r') as f:
        data = json.load(f)
    return data
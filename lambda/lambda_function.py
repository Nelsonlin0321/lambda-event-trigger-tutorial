import os
import json
import urllib.parse
import boto3
from pymongo import MongoClient
from . import utils


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

mongodb_url = utils.get_secret(secret_client,mongodb_url_secret)

mongodb_client = MongoClient(mongodb_url)
mongodb_db = mongodb_client.client["search"]


def handler(event, context):

    # Get the secret from Secrets Manager
    mongodb_url = utils.get_secret(secret_client,mongodb_url_secret)
    print("Get mongodb_url secret from Secrets Manager successfully")

    bucket = event['Records'][0]['s3']['bucket']['name']
    s3_key = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'], encoding='utf-8')

    try:
        json_path = utils.download_file_from_s3(s3_client,bucket, s3_key)
        data = utils.open_json_file(json_path)

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
    
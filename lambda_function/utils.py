import os
import json
from botocore.exceptions import ClientError


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
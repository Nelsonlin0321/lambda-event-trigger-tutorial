import sys
def handler(event, context):
    message = 'Hello from AWS Lambda using Python' + sys.version + '!' 
    return message
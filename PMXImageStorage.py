import json
import boto3
import base64
from requests_toolbelt.multipart import decoder
 

def lambda_handler(event, context):
    
    print('event', event)
    forward_slash = "/"
    bucket_name = "pmximagestore"
    output = {}
    
    s3 = boto3.client('s3')

    if event['resource'] == '/images/uploadimage':
        subject_id = event['queryStringParameters']['subjectID']
        image_id = event['queryStringParameters']['imageID']
        file_path = subject_id + forward_slash + image_id
        print(file_path)

        body = event["body"]
        content_type = event["headers"]["Content-Type"]
        body_dec = base64.b64decode(body)
        multipart_data = decoder.MultipartDecoder(body_dec, content_type)
    
        binary_content = []
    
        for part in multipart_data.parts:
            binary_content.append(part.content)
        try:
            s3_response = s3.put_object(Bucket=bucket_name, Key=file_path, Body=binary_content[0])
        except Exception as e:
            raise IOError(e)

        
    elif event['resource'] == '/images/downloadimage':
        subject_id = event['queryStringParameters']['subjectID']
        image_id = event['queryStringParameters']['imageID']
        file_path = subject_id + forward_slash + image_id
        try:
            s3_response = s3.get_object(Bucket=bucket_name, Key=file_path)
            data = s3_response['Body'].read()
            resp = base64.b64encode(data).decode('utf-8')
            output['data'] = resp
        except Exception as e:
            print(e)
            output[data] = e
            raise IOError(e)

    elif event['resource'] == '/images/list':
        subject_id = event['queryStringParameters']['subjectID']
        file_path = forward_slash + subject_id + forward_slash
        try:
            s3_response = s3.list_objects(Bucket=bucket_name, Delimiter=file_path)
            list = []
            for object in s3_response['Contents']:
                list.append(object['Key'])
            print(s3_response)
            output['keys'] = list
        except Exception as e:
            print(e)
            output['keys'] = e
            raise IOError(e)

    return {
        "isBase64Encoded": False,
        "statusCode": 200,
        "headers": { 'Content-Type': 'application/json' },
        "body": json.dumps(output)
    }
    
from datetime import datetime
import boto3
from io import BytesIO
from PIL import Image, ImageOps
import os
import uuid
import json


s3 = boto3.client('s3') #Handle to s3 service
size = int(os.environ['THUMBNAIL_SIZE']) #refersto env var from serverless.yml


def s3_thumbnail_generator(event, context):
    #parse event
    print("EVENT:::", event)
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = event['Records'][0]['s3']['object']['key']
    img_size = event['Records'][0]['s3']['object']['size']

    if not key.endswith("_thumbnail.png"):
        image = get_s3_image(bucket, key)

        thumbnail = image_to_thumbnail(image)

        thumbnail_key = new_filename(key)

        url = upload_to_s3(bucket, thumbnail_key, thumbnail, img_size)
        
        return url
    
    body = {
        "message": "Go Serverless v3.0! Your function executed successfully!",
        "input": event,
    }

    return {"statusCode": 200, "body": json.dumps(body)}
    
####################
##HELPER FUNCTIONS##
####################
def get_s3_image(bucket, key):
    response = s3.get_object(Bucket=bucket, Key=key)
    imagecontent = response['Body'].read()
        
    file = BytesIO(imagecontent)
    img = Image.open(file)
    return img
    

def image_to_thumbnail(image):
    return ImageOps.fit(image, (size,size), Image.ANTIALIAS)

def new_filename(key):
    key_split = key.rsplit('.',1)
    return key_split[0] + "_thumbnail.png"
       

def upload_to_s3(bucket, key, image, img_size):
    out_thumbnail = BytesIO()
    
    image.save(out_thumbnail, 'PNG')
    out_thumbnail.seek(0)

    response = s3.put_object(
        Body = out_thumbnail,
        Bucket = bucket,
        ContentType = 'image/png',
        Key=key
    )
    print(response)

    url = '{}/{}/{}'.format(s3.meta.endpoint_url, bucket, key)

    return url

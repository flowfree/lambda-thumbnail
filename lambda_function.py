#!/usr/bin/env python

import mimetypes
import os
import sys
import uuid
from urllib.parse import unquote_plus

import boto3
from PIL import Image
import PIL.Image


bucket_src = 'tmp-2021-06-22-src'
bucket_dst = 'tmp-2021-06-22-dst'

s3_client = boto3.client('s3')


def resize_image(image_path, resized_path):
    with Image.open(image_path) as image:
        image.thumbnail(tuple(x / 2 for x in image.size))
        image.save(resized_path)


def lambda_handler(event, context):
    for record in event['Records']:
        if record['s3']['bucket']['name'] != bucket_src:
            continue
        key = unquote_plus(record['s3']['object']['key'])
        tmpkey = key.replace('/', '')
        download_path = '/tmp/{}{}'.format(uuid.uuid4(), tmpkey)
        upload_path = '/tmp/resized-{}'.format(tmpkey)
        
        s3_client.download_file(bucket_src, key, download_path)
        resize_image(download_path, upload_path)
        
        mimetype, _ = mimetypes.guess_type(key)
        args = {
            'ContentType': mimetype,
            'ACL': 'public-read'
        }
        s3_client.upload_file(upload_path, bucket_dst, key, ExtraArgs=args)
        
    print('done.')
            

if __name__ == "__main__":
    resize_image('sample.jpg', 'sample-resized.jpg')
    print('done.')


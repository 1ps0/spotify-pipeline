import os
import json
from pathlib import Path

from datetime import datetime

def datetime_now():
    return datetime.utcnow()

def timestamp_now():
    return int(datetime_now().timestamp())

def folder_path_now(ext="jsonl"):
    dtn = datetime_now()
    dtn_ymd = f"{dtn.year}{dtn.month:02}{dtn.day:02}"
    return f"{dtn_ymd}/{int(dtn.timestamp())}.{ext}"


def local_files(path:str, ext:str='.json', recursive=True):
    p = Path(path)
    for filename in p.glob(f"{'**/' if recursive else ''}*{ext}"):
        yield filename

def downrender_tracks():
    files = local_files('data/tracks/')
    print(f"downrendering files")
    for file in files:
        print(f"-> {file}")
        data = local_load_data(file)
        local_save_data(file, data)

def delete_file(file:str):
    return os.remove(file)

def delete_errors():
    files = local_files('data/tracks/')
    for file in files:
        file_data = local_load_data(file)
        if 'error' in file_data:
            print(f"Deleting {file}")
            delete_file(file)

def local_save_csv(path, data):
    pass

def local_save_data(path:str, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w') as f:
        return f.write(data)
    return None

def local_load_data(path:str):
    try:
        posix = Path(path)
        if posix.is_symlink():
            path = os.readlink(path)

        with open(path, 'r') as f:
            return json.loads(f.readlines()[0])
    except FileNotFoundError as err:
        print(err)
        return None
    return None

# def s3_save_data(s3_key:str, data):
#     try:
#         s3.put_object(Bucket=bucket, Key=s3_key, Body=data)
#     except Exception as e:
#         print(e)
#         print('Error getting object {} from bucket {}. Make sure they exist and your bucket is in the same region as this function.'.format(key, bucket))
#         raise e

# sqs = boto3.client('sqs', 'us-west-2')
# def sqs_enqueue(message):
    # return sqs.send_message(QueueUrl='scraper-spotify-queue', MessageBody=message)


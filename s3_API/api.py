import os
from dotenv import load_dotenv
import boto3
load_dotenv()

def upload_to_r2(file_path, object_key):
    access_key = os.environ.get("R2_ACCESS_KEY")
    secret_key = os.environ.get("R2_SECRET_KEY")
    account_id = os.environ.get("R2_ACCOUNT_ID")
    bucket_name = os.environ.get("R2_BUCKET_NAME")

    assert access_key and secret_key and account_id and bucket_name, "Missing R2 environment variables"

    endpoint_url = f"https://{account_id}.r2.cloudflarestorage.com"

    s3 = boto3.client(
        's3',
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
        endpoint_url=endpoint_url,
        region_name='auto',  # R2 không cần khu vực cụ thể
    )

    try:
        s3.upload_file(file_path, bucket_name, object_key)
        print(f"☁️ Uploaded to R2: {bucket_name}/{object_key}")
    except Exception as e:
        print(f"❌ Upload to R2 failed: {e}")

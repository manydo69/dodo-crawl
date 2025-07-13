import os
from dotenv import load_dotenv
import boto3
load_dotenv()

def upload_to_r2(file_path, object_key):
    """
    Upload a single file to R2 storage.

    Args:
        file_path (str): Path to the file to upload
        object_key (str): Key (path) where the file will be stored in the bucket
    """
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
        region_name='auto',
    )

    try:
        s3.upload_file(file_path, bucket_name, object_key)
        print(f"☁️ Uploaded to R2: {bucket_name}/{object_key}")
        return True
    except Exception as e:
        print(f"❌ Upload to R2 failed: {e}")
        return False

def upload_folder_to_r2(folder_path, prefix=""):
    """
    Upload an entire folder to R2 storage, preserving the directory structure.

    Args:
        folder_path (str): Path to the folder to upload
        prefix (str, optional): Prefix to add to the object keys in the bucket
                               (useful for organizing files in the bucket)

    Returns:
        tuple: (success_count, error_count) - Number of files successfully uploaded and failed
    """
    if not os.path.isdir(folder_path):
        print(f"❌ Error: {folder_path} is not a directory")
        return 0, 0

    success_count = 0
    error_count = 0

    # Walk through the directory
    for root, _, files in os.walk(folder_path):
        for file in files:
            # Get the full path of the file
            file_path = os.path.join(root, file)

            # Calculate the object key (path in the bucket)
            # This preserves the directory structure relative to the folder_path
            rel_path = os.path.relpath(file_path, folder_path)
            object_key = os.path.join(prefix, rel_path).replace("\\", "/")

            # Upload the file
            if upload_to_r2(file_path, object_key):
                success_count += 1
            else:
                error_count += 1

    print(f"📁 Folder upload complete: {success_count} files uploaded, {error_count} files failed")
    return success_count, error_count

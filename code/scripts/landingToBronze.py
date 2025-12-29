import re
import os
import argparse
from dotenv import load_dotenv
import boto3

load_dotenv()
user_rw = os.getenv("MINIO_RW_USER")
password_rw = os.getenv("MINIO_RW_PASSWORD")

def get_parameters():
    try:
        parser = argparse.ArgumentParser()
        parser.add_argument("--file_name", type=str, required=True, 
                            help="Name of the file to process from landing")
        args = parser.parse_args()
        return args.file_name
    except Exception as e:
        print("Error parsing parameters:", e)
        raise e
  
def create_s3_client():
    try:
        return boto3.client( 's3' , 
                  endpoint_url = 'http://minio:9000',
                  aws_access_key_id = user_rw,
                  aws_secret_access_key = password_rw,
                  region_name = 'us-east-1',
                  config = boto3.session.Config(signature_version='s3v4')
                )
    except Exception as e:
        print("Error creating S3 client:", e)
        raise e
    
def check_file_exists(s3_client, file_name):
    try:
        objects = s3_client.list_objects_v2(Bucket='landing')
        objects_names = [o.get('Key') for o in objects.get('Contents', [])]
        return file_name in objects_names
    except Exception as e:
        print("Error checking file existence:", e)
        raise e
    
def process_atus_file(s3, file_name):
    source = {'Bucket': 'landing', 'Key': file_name}
    s3.copy(source, 'bronze', Key='atus_data/' + file_name)
    print(f'> File {file_name} copied to bronze/atus_data/')

def process_catalog_file(s3, file_name):
    source = {'Bucket': 'landing', 'Key': file_name}
    s3.copy(source, 'bronze', Key='catalog/' + file_name)
    print(f'> File {file_name} copied to bronze/catalog/')

def process_other_file(s3, file_name):
    source = {'Bucket': 'landing', 'Key': file_name}
    s3.copy(source, 'bronze', Key='other_files/' + file_name)
    print(f'> File {file_name} copied to bronze/other_files/')

def process_file(file_name):
    try:
        if re.match(r"atus_anual_\d{4}\.csv", file_name):
            process_atus_file(s3, file_name)
        elif re.match(r"tc_.*\.csv", file_name):
            process_catalog_file(s3, file_name)
        else:
            process_other_file(s3, file_name)
    except Exception as e:
        print("> Error processing file:", e)
        raise e
   
def delete_file_from_landing(s3_client, file_name):
    try:
        s3_client.delete_object(Bucket='landing', Key=file_name)
        print(f'> File {file_name} deleted from landing bucket.')
    except Exception as e:
        print("Error deleting file from landing:", e)
        raise e
    
if __name__ == "__main__":
    file_name = get_parameters()
    s3 = create_s3_client()
    print("-"*50)
    print("Starting Landing to Bronze Process")
    print("-"*50)

    if not check_file_exists(s3, file_name):
        print(f"> File {file_name} does not exist in the landing bucket.")
        exit(1)
    process_file(file_name)
    #delete_file_from_landing(s3, file_name)
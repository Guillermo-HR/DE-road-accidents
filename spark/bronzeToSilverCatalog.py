import re
import os
import argparse
from dotenv import load_dotenv
import boto3
from pyspark.sql import SparkSession
from pyspark.sql.functions import input_file_name, current_timestamp, monotonically_increasing_id
from pyspark.sql.types import StructType, StructField, StringType, IntegerType

load_dotenv()
user_rw = os.getenv("MINIO_RW_USER")
password_rw = os.getenv("MINIO_RW_PASSWORD")
aws_endpoint = os.getenv("AWS_ENDPOINT_URL")

def get_parameters():
    try:
        parser = argparse.ArgumentParser()
        parser.add_argument("--file_key", type=str, required=True, 
                            help="Key of the file to process from bronze")
        args = parser.parse_args()
        return args.file_key
    except Exception as e:
        print("Error parsing parameters:", e)
        raise e

def create_spark_session():
    try:
        packages = "org.apache.hadoop:hadoop-aws:3.3.4,com.amazonaws:aws-java-sdk-bundle:1.12.262,io.delta:delta-core_2.12:2.4.0"
        return SparkSession.builder \
            .appName("BronzeToSilverCatalog") \
            .config("spark.jars.packages", packages) \
            .config("spark.hadoop.fs.s3a.endpoint", aws_endpoint) \
            .config("spark.hadoop.fs.s3a.access.key", user_rw) \
            .config("spark.hadoop.fs.s3a.secret.key", password_rw) \
            .config("spark.hadoop.fs.s3a.path.style.access", "true") \
            .config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem") \
            .config("spark.hadoop.fs.s3a.connection.ssl.enabled", "false") \
            .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension") \
            .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog") \
            .config("spark.ui.port", "8080") \
            .getOrCreate()
    except Exception as e:
        print("Error creating Spark session:", e)
        raise e
    
def create_s3_client():
    try:
        return boto3.client( 's3' , 
                  endpoint_url = aws_endpoint,
                  aws_access_key_id = user_rw,
                  aws_secret_access_key = password_rw,
                  region_name = 'us-east-1',
                  config = boto3.session.Config(signature_version='s3v4')
                )
    except Exception as e:
        print("Error creating S3 client:", e)
        raise e

def check_file_exists(s3_client, file_key):
    try:
        objects = s3_client.list_objects_v2(Bucket='bronze')
        objects_names = [o.get('Key') for o in objects.get('Contents', [])]
        return file_key in objects_names
    except Exception as e:
        print("Error checking file existence:", e)
        raise e
    
def validate_structure(spark, file_path):
    file_name = os.path.basename(file_path)

    df_columns = spark.read \
        .option("header", "true") \
        .option("inferSchema", "true") \
        .csv(file_path) \
        .limit(1).columns
    
    if file_name == "tc_entidad.csv":
        required_columns = {"ID_ENTIDAD", "NOM_ENTIDAD"}
    elif file_name == "tc_municipio.csv":
        required_columns = {"ID_ENTIDAD", "ID_MUNICIPIO", "NOM_MUNICIPIO"}
    else:
        raise ValueError(f"Unsupported catalog file: {file_name}")
    return required_columns.issubset(set(df_columns))

def read_file(spark, file_path):
    file_name = os.path.basename(file_path)
    
    if file_name == "tc_entidad.csv":
        schema = StructType([
            StructField("ID_ENTIDAD", IntegerType(), False),
            StructField("NOM_ENTIDAD", StringType(), False)
        ])
    elif file_name == "tc_municipio.csv":
        schema = StructType([
            StructField("ID_ENTIDAD", IntegerType(), False),
            StructField("ID_MUNICIPIO", IntegerType(), False),
            StructField("NOM_MUNICIPIO", StringType(), False)
        ])

    try:
        return spark.read \
            .option("header", "true") \
            .schema(schema) \
            .csv(file_path) \
            .withColumn("input_file_name", input_file_name()) \
            .withColumn("ingestion_date", current_timestamp())
    except Exception as e:
        print("Error reading catalog file into DataFrame:", e)
        raise e

def transform_df(df, file_path):
    file_name = os.path.basename(file_path)
    
    if file_name == "tc_entidad.csv":
        return df.withColumnsRenamed(
            {"ID_ENTIDAD": "ID", "NOM_ENTIDAD": "ENTIDAD"}
        )
    elif file_name == "tc_municipio.csv":
        # add id column consecutive
        return df.withColumn(
            "ID", monotonically_increasing_id()
        ).withColumnsRenamed(
            {"ID_ENTIDAD": "ENTIDAD_ID", "NOM_MUNICIPIO": "MUNICIPIO"}
        ).drop(
            "ID_MUNICIPIO"
        )
            


def process_file(spark, s3, file_key):
    try:
        if re.match(r'catalog/tc_.*\.csv', file_key):
            BRONZE_PATH = "s3a://bronze/"
            FILE_PATH = BRONZE_PATH + file_key
            
            if not validate_structure(spark, FILE_PATH):
                source = {'Bucket': 'bronze', 'Key': file_key}
                s3.copy(source, 'bronze', Key='catalog_rejected/' + file_key)
                s3.delete_object(Bucket='bronze', Key=file_key)
                raise ValueError("The file structure is invalid or missing required columns. " \
                "File moved to catalog_rejected.")
            
            df = read_file(spark, FILE_PATH)
            df_cleaned = transform_df(df)

            print("Current step")
        else:
            print(f"> Unsupported file type for {file_key}. No processing applied.")
    except Exception as e:
        print("> Error processing file:", e)
        raise e
            
if __name__ == "__main__":
    file_name = get_parameters()
    spark = create_spark_session()
    s3 = create_s3_client()
    print("-"*50)
    print("Starting Bronze to Silver Process (Catalog Files)")
    print("-"*50)
    if not check_file_exists(s3, file_name):
        print(f"> File {file_name} does not exist in the bronze bucket.")
        exit(1)
    process_file(spark, s3, file_name)
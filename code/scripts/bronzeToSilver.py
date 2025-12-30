import re
import os
import argparse
from dotenv import load_dotenv
import boto3
import pyspark
from pyspark.sql import SparkSession
from pyspark.sql.functions import input_file_name, current_timestamp, when, col, concat, lpad, lit
from pyspark.sql.types import StructType, StructField, StringType, IntegerType

load_dotenv()
user_rw = os.getenv("MINIO_RW_USER")
password_rw = os.getenv("MINIO_RW_PASSWORD")

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
            .appName("BronzeToSilver") \
            .config("spark.jars.packages", packages) \
            .config("spark.hadoop.fs.s3a.endpoint", "http://minio:9000") \
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
                  endpoint_url = 'http://minio:9000',
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
    columns = set(['COBERTURA', 'ID_ENTIDAD', 'ID_MUNICIPIO', 'ANIO', 'MES', 'ID_HORA',
                   'ID_MINUTO', 'ID_DIA', 'DIASEMANA', 'URBANA', 'SUBURBANA', 'TIPACCID',
                   'AUTOMOVIL', 'CAMPASAJ', 'MICROBUS', 'PASCAMION', 'OMNIBUS', 'TRANVIA',
                   'CAMIONETA', 'CAMION', 'TRACTOR', 'FERROCARRI', 'MOTOCICLET', 'BICICLETA',
                   'OTROVEHIC', 'CAUSAACCI', 'CAPAROD', 'SEXO', 'ALIENTO', 'CINTURON',
                   'ID_EDAD', 'CONDMUERTO', 'CONDHERIDO', 'PASAMUERTO', 'PASAHERIDO', 
                   'PEATMUERTO', 'PEATHERIDO', 'CICLMUERTO', 'CICLHERIDO', 'OTROMUERTO',
                   'OTROHERIDO', 'NEMUERTO', 'NEHERIDO', 'CLASACC', 'ESTATUS'])
    
    df_columns = spark.read \
        .option("header", "true") \
        .option("inferSchema", "true") \
        .csv(file_path) \
        .limit(1).columns
    
    return set(df_columns).issuperset(columns)

def read_file(spark, file_path):
    schema = StructType([
        StructField("COBERTURA", StringType(), False),
        StructField("ID_ENTIDAD", IntegerType(), False),
        StructField("ID_MUNICIPIO", IntegerType(), False),
        StructField("ANIO", IntegerType(), False),
        StructField("MES", IntegerType(), False),
        StructField("ID_HORA", IntegerType(), False),
        StructField("ID_MINUTO", IntegerType(), False),
        StructField("ID_DIA", IntegerType(), False),
        StructField("DIASEMANA", StringType(), False),
        StructField("URBANA", StringType(), False),
        StructField("SUBURBANA", StringType(), False),
        StructField("TIPACCID", StringType(), False),
        StructField("AUTOMOVIL", IntegerType(), False),
        StructField("CAMPASAJ", IntegerType(), False),
        StructField("MICROBUS", IntegerType(), False),
        StructField("PASCAMION", IntegerType(), False),
        StructField("OMNIBUS", IntegerType(), False),
        StructField("TRANVIA", IntegerType(), False),
        StructField("CAMIONETA", IntegerType(), False),
        StructField("CAMION", IntegerType(), False),
        StructField("TRACTOR", IntegerType(), False),
        StructField("FERROCARRI", IntegerType(), False),
        StructField("MOTOCICLET", IntegerType(), False),
        StructField("BICICLETA", IntegerType(), False),
        StructField("OTROVEHIC", IntegerType(), False),
        StructField("CAUSAACCI", StringType(), False),
        StructField("CAPAROD", StringType(), False),
        StructField("SEXO", StringType(), False),
        StructField("ALIENTO", StringType(), False),
        StructField("CINTURON", StringType(), False),
        StructField("ID_EDAD", IntegerType(), False),
        StructField("CONDMUERTO", IntegerType(), False),
        StructField("CONDHERIDO", IntegerType(), False),
        StructField("PASAMUERTO", IntegerType(), False),
        StructField("PASAHERIDO", IntegerType(), False),
        StructField("PEATMUERTO", IntegerType(), False),
        StructField("PEATHERIDO", IntegerType(), False),
        StructField("CICLMUERTO", IntegerType(), False),
        StructField("CICLHERIDO", IntegerType(), False),
        StructField("OTROMUERTO", IntegerType(), False),
        StructField("OTROHERIDO", IntegerType(), False),
        StructField("NEMUERTO", IntegerType(), False),
        StructField("NEHERIDO", IntegerType(), False),
        StructField("CLASACC", StringType(), False),
        StructField("ESTATUS", StringType(), False)
    ])
    
    try:
        return spark.read \
            .option("header", "true") \
            .schema(schema) \
            .csv(file_path) \
            .withColumn("input_file_name", input_file_name()) \
            .withColumn("ingestion_date", current_timestamp())
    except Exception as e:
        print("Error reading ATUS file into DataFrame:", e)
        raise e

def transform_df(df):
    return df.withColumn(
                "FECHA_HORA_REGISTRADA",
                when(
                    (col("ID_DIA") != 32) & (col("ID_HORA") != 99) & (col("ID_MINUTO") != 99),
                    True
                ).otherwise(False)
            ).withColumn(
                "FECHA",
                when(
                    col("FECHA_HORA_REGISTRADA") == True,
                    concat(
                        col("ANIO").cast(StringType()), lit("-"),
                        lpad(col("MES").cast(StringType()), 2, "0"), lit("-"),
                        lpad(col("ID_DIA").cast(StringType()), 2, "0"), lit(" "),
                        lpad(col("ID_HORA").cast(StringType()), 2, "0"), lit(":"),
                        lpad(col("ID_MINUTO").cast(StringType()), 2, "0")
                    ).cast("timestamp")
                ).otherwise(
                    concat(
                        col("ANIO").cast(StringType()), lit("-"),
                        lpad(col("MES").cast(StringType()), 2, "0"), lit("-"),
                        lit("01 00:00")
                    ).cast("timestamp")
                )
            ).withColumn(
                "URBANA",
                when(
                    col("URBANA") == "Sin accidente en esta zona", None
                ).otherwise(col("URBANA"))
            ).withColumn(
                "SUBURBANA",
                when(
                    col("SUBURBANA") == "Sin accidente en esta zona", None
                ).otherwise(col("SUBURBANA"))
            ).withColumn(
                "TIPACCID",
                when(
                    col("TIPACCID") == "Certificado cero", "Otro"
                ).otherwise(col("TIPACCID"))
            ).withColumn(
                "CAUSAACCI",
                when(
                    col("CAUSAACCI") == "Certificado cero", "Otro"
                ).otherwise(col("CAUSAACCI"))
            ).withColumn(
                "CAPAROD",
                when(
                    col("CAPAROD") == "Certificado cero", None
                ).otherwise(col("CAPAROD"))
            ).withColumn(
                "SE_FUGO",
                (when(col("SEXO") != "Se fugó", False).otherwise(True) &
                when(col("ID_EDAD") != 0, False).otherwise(True))
            ).withColumn(
                "SEXO",
                when(
                    col("SEXO").isin("Se fugó", "Certificado cero"), "Desconocido"
                ).otherwise(col("SEXO"))
            ).withColumn(
                "ALIENTO",
                when(
                    col("ALIENTO").isin("Se ignora", "Certificado cero"), "Desconocido"
                ).otherwise(col("ALIENTO"))
            ).withColumn(
                "CINTURON",
                when(
                    col("CINTURON").isin("Se ignora", "Certificado cero"), "Desconocido"
                ).otherwise(col("CINTURON"))
            ).withColumn(
                "ID_EDAD",
                when(
                    (col("ID_EDAD") == 0) | (col("ID_EDAD") == 99), None
                ).otherwise(col("ID_EDAD"))
            ).withColumn(
                "CLASACC",
                when(
                    col("CLASACC") == "Certificado cero", "Otro"
                ).otherwise(col("CLASACC"))
            ).withColumnsRenamed(
                {"TIPACCID": "TIPO_ACCIDENTE", "CAMPASAJ": "CAMIONETA_PASAJEROS", 
                "PASCAMION": "CAMION_PASAJEROS", "FERROCARRI": "FERROCARRIL", 
                "MOTOCICLET": "MOTOCICLETA", "OTROVEHIC": "OTRO_VEHICULO",
                "CAUSAACCI": "CAUSA_ACCIDENTE", "CAPAROD": "ESTA_PAVIMENTADO", 
                "ALIENTO": "COND_CON_ALIENTO_ALCOHOLICO", "CINTURON": "COND_CON_CINTURON",
                "ID_EDAD": "EDAD_CONDUCTOR", "CONDMUERTO": "CONDUCTORES_MUERTOS",
                "CONDHERIDO": "CONDUCTORES_HERIDOS", "PASAMUERTO": "PASAJEROS_MUERTOS",
                "PASAHERIDO": "PASAJEROS_HERIDOS", "PEATMUERTO": "PEATONES_MUERTOS",
                "PEATHERIDO": "PEATONES_HERIDOS", "CICLMUERTO": "CICLISTAS_MUERTOS",
                "CICLHERIDO": "CICLISTAS_HERIDOS", "OTROMUERTO": "OTROS_MUERTOS",
                "OTROHERIDO": "OTROS_HERIDOS", "NEMUERTO": "TOTAL_MUERTOS",
                "NEHERIDO": "TOTAL_HERIDOS", "CLASACC": "CLASIFICACION_ACCIDENTE", 
                "ESTATUS": "ESTATUS_REGISTRO"
                }
            ).drop("ANIO", "MES", "ID_DIA", "ID_HORA", "ID_MINUTO", "FECHA_HORA_REGISTRADA")
   
def process_file(spark, s3, file_key):
    try:
        if re.match(r'atus_data/atus_anual_\d{4}\.csv', file_key):
            BRONZE_PATH = "s3a://bronze/"
            FILE_PATH = BRONZE_PATH + file_key
            
            if not validate_structure(spark, FILE_PATH):
                source = {'Bucket': 'bronze', 'Key': file_key}
                s3.copy(source, 'bronze', Key='atus_data_rejected/' + file_key)
                s3.delete_object(Bucket='bronze', Key=file_key)
                raise ValueError("The file structure is invalid or missing required columns. " \
                "File moved to atus_data_rejected.")
            
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
    print("Starting Bronze to Silver Process")
    print("-"*50)
    if not check_file_exists(s3, file_name):
        print(f"> File {file_name} does not exist in the bronze bucket.")
        exit(1)
    process_file(spark, s3, file_name)
import findspark
from pyspark.sql import SparkSession
from DataIngestion  import DataIngestion
from decimal import Decimal
import os
from dotenv import load_dotenv
from ETLPipeline import ETLPipeline
from StorageConfig import StorageConfig

def main():

    findspark.init()
    jars_dir = "jars"
    all_jars = ",".join([os.path.join(jars_dir, jar) for jar in os.listdir(jars_dir)])


    load_dotenv()

    storage_account = os.getenv("AZURE_STORAGE_ACCOUNT")
    key = os.getenv("AZURE_STORAGE_KEY")
    container = os.getenv("AZURE_CONTAINER")


    spark = SparkSession.builder \
    .appName("App") \
    .master("local") \
    .enableHiveSupport()\
    .config("spark.jars", all_jars) \
    .config("spark.hive.mapred.supports.subdirectories","true") \
    .config("spark.hadoop.mapreduce.input.fileinputformat.input.dir.recursive","true") \
    .config("spark.hadoop.fs.azure.account.key." + storage_account + ".blob.core.windows.net", key) \
    .getOrCreate()

    spark.conf.set("spark.sql.parquet.enableVectorizedReader", "false")

    etl = ETLPipeline(spark, StorageConfig(storage_account, container, key))
    etl.run()

if __name__ == "__main__":
    main()

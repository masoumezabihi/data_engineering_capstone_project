import findspark
from pyspark.sql import SparkSession
from DataIngestion  import DataIngestion
from ETLPipeline import ETLPipeline
from StorageConfig import StorageConfig
from JobTracker import JobTracker 
import os
import sys
from dotenv import load_dotenv
import logging



def main():

    logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
    
    load_dotenv()

    findspark.init()
    jars_dir = "jars"
    all_jars = ",".join([os.path.join(jars_dir, jar) for jar in os.listdir(jars_dir)])

    storage_account = os.getenv("AZURE_STORAGE_ACCOUNT")
    key = os.getenv("AZURE_STORAGE_KEY")
    container = os.getenv("AZURE_CONTAINER")

    if not all([storage_account, key, container]):
        logging.error("Missing required storage environment variables.")
        sys.exit(1)

    dbconfig = {
    "postgres": {
        "host": os.getenv("DB_HOST"),
        "port": os.getenv("DB_PORT"),
        "database": os.getenv("DB_NAME"),
        "user": os.getenv("DB_USER"),
        "password": os.getenv("DB_PASSWORD"),
        "job_tracker_table_name": os.getenv("JOB_TRACKER_TABLE")
        }
    }

    try:
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

        pipeline = ETLPipeline(spark, StorageConfig(storage_account, container, key))

        if len(sys.argv) < 2:
            logging.error("Usage: spark-submit main.py <name_of_the_job>")
            logging.error("job names: ingestion | etl")
            sys.exit(1)

        job_name = sys.argv[1]

        tracker = JobTracker(job_name, dbconfig)

        try:
            if job_name == "ingestion":
                pipeline.run_ingestion()
            elif job_name == "etl":
                pipeline.run_etl()
            else:
                logging.error("Invalid job name. Use 'ingestion' or 'etl'.")
                sys.exit(1)

            logging.info(f"Job {job_name} completed successfully.") 
            tracker.update_job_status("success")

        except Exception as e:
            logging.error(f"Error occurred in job {job_name}: {e}")
            tracker.update_job_status("failed")
            raise e

    except Exception as e:
        logging.error(f"Failed to initialize job: {e}")
        sys.exit(1)

        
if __name__ == "__main__":
    main()

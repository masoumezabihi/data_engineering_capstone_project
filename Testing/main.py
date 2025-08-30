import os
from pyspark.sql import SparkSession
from ETLProcessor import ETLProcessor
from Logger import Logger
from dotenv import load_dotenv
import findspark
from config import BlobStorageConfig, DatabaseConfig 

class MainApp:
    def __init__(self):

        load_dotenv()
        Logger.setup_logger('logs', 'open_fda_etl.log')

        findspark.init()  # Initialize findspark to locate Spark installation

        # Load Azure Blob Storage credentials from env
        storage_account = os.getenv("AZURE_STORAGE_ACCOUNT")
        storage_key = os.getenv("AZURE_STORAGE_KEY")
        container = os.getenv("AZURE_CONTAINER")

        # Prepare config objects
        self.blob_config = BlobStorageConfig(
            storage_account=storage_account,
            storage_key=storage_key,
            container=container,
            path_pattern="*.json"
        )


        # Path to your JAR files directory (add the directory where JARs are located)
        jars_dir = "jars"
        all_jars = ",".join([os.path.join(jars_dir, jar) for jar in os.listdir(jars_dir)])

        # Initialize Spark session with JAR files and Azure Blob Storage config
        self.spark = SparkSession.builder \
            .appName("OPEN_FDA_ETL") \
            .master("local[*]") \
            .config("spark.jars", all_jars) \
            .config("spark.hive.mapred.supports.subdirectories", "true") \
            .config("spark.hadoop.mapreduce.input.fileinputformat.input.dir.recursive", "true") \
            .config(f"spark.hadoop.fs.azure.account.key.{self.blob_config.storage_account}.blob.core.windows.net", self.blob_config.storage_key) \
            .getOrCreate()

        Logger.log("Spark session initialized successfully.", 'info')

    def run(self):
        Logger.log("ETL process starting...", 'info')

        try:
            # Initialize ETLProcessor with Spark session and configs
            etl_processor = ETLProcessor(
                spark=self.spark,
                blob_config=self.blob_config
            )
            etl_processor.run()

            Logger.log("ETL process completed for all files.", 'info')

        except Exception as e:
            Logger.log(f"An error occurred during ETL processing: {str(e)}", 'error')

        finally:
            self.spark.stop()

if __name__ == "__main__":
    app = MainApp()
    app.run()

    
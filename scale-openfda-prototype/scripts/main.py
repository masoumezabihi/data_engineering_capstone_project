import os
from pyspark.sql import SparkSession
from ETLProcessor import ETLProcessor
from Logger import Logger
from config import BlobStorageConfig

class MainApp:
    def __init__(self):
        Logger.setup_logger('logs', 'open_fda_etl.log')

        storage_account = os.environ.get("AZURE_STORAGE_ACCOUNT")
        container = os.environ.get("AZURE_CONTAINER")

        # Just set config in cluster, don't retrieve key here
        self.blob_config = BlobStorageConfig(
            storage_account=storage_account,
            storage_key=None,
            container=container,
            path_pattern="*.json"
        )

        # SparkSession (no need to set the account key in code anymore)
        self.spark = SparkSession.builder \
            .appName("OPEN_FDA_ETL") \
            .config("spark.hive.mapred.supports.subdirectories", "true") \
            .config("spark.hadoop.mapreduce.input.fileinputformat.input.dir.recursive", "true") \
            .getOrCreate()

        Logger.log("Spark session initialized successfully.", 'info')

    def run(self):
        Logger.log("ETL process starting...", 'info')

        try:
            etl_processor = ETLProcessor(
                spark=self.spark,
                blob_config=self.blob_config
            )
            etl_processor.run()
            Logger.log("ETL process completed successfully.", 'info')

        except Exception as e:
            Logger.log(f"An error occurred during ETL processing: {str(e)}", 'error')

        finally:
            self.spark.stop()

if __name__ == "__main__":
    app = MainApp()
    app.run()

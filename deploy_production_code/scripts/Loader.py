from pyspark.sql import SparkSession
from Logger import Logger
import os

class Loader:
    def __init__(self, spark: SparkSession, output_path):
        """
        Initializes the Loader class for writing to Parquet files.
        
        Parameters:
            spark (SparkSession): The Spark session
            output_path (str): Directory to save Parquet files
        """
        self.spark = spark
        self.output_path = output_path

    def write_table(self, df, table_name, mode='overwrite'):
        """
        Writes a Spark DataFrame to a Parquet file.

        Parameters:
            df (DataFrame): Spark DataFrame
            table_name (str): Target folder name
            mode (str): 'overwrite', 'append', etc.
        """
        try:
            if not table_name:
                raise ValueError("Table name must not be empty.")

            output_dir = os.path.join(self.output_path, table_name)
            df.write.mode(mode).parquet(output_dir)
            Logger.log(f"Successfully wrote '{table_name}' to {output_dir}.")

        except Exception as e:
            Logger.log(f"Failed to write '{table_name}' as Parquet: {e}", level='error')
            raise
 
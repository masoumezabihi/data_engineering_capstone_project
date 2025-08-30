from pyspark.sql import SparkSession, DataFrame
from pyspark.sql.functions import explode, col
from etl.Logger import Logger
from etl.config import BlobStorageConfig

class Extractor:
    def __init__(self, spark: SparkSession, blob_config: BlobStorageConfig):
        """
        Initialize Extractor with Spark session and blob storage info.

        Parameters:
            spark (SparkSession): Active Spark session
            container (str): Azure Blob container name
            storage_account (str): Azure Storage account name
            path_pattern (str): Pattern to match JSON files inside the container (default *.json)
        """
        self.spark = spark
        self.blob_config = blob_config
        self.df = None 

    def load_data(self) -> bool:
        """
        Read JSON files from Azure Blob Storage into Spark DataFrame.

        Returns:
            bool: True if data loaded successfully, False otherwise.
        """
        try:
            # Build wasbs URI
            blob_path = f"wasbs://{self.blob_config.container}@{self.blob_config.storage_account}.blob.core.windows.net/{self.blob_config.path_pattern}"
            Logger.log(f"Loading data from: {blob_path}", "info")

            # Read JSON from blob
            self.df = self.spark.read.option("multiLine", "true").json(blob_path)
            Logger.log("Data loaded successfully from blob storage.", "info")
            return True

        except Exception as e:
            Logger.log(f"Error loading data from blob storage: {str(e)}", "error")
            return False

    def extract_results(self) -> DataFrame:
        """
        Extracts and flattens the 'results' field from the loaded DataFrame.

        Returns:
            DataFrame: Spark DataFrame with exploded 'results' records.

        Raises:
            ValueError: If data is not loaded yet.
            KeyError: If 'results' field is missing.
        """
        if self.df is None:
            raise ValueError("Data not loaded. Call load_data() first.")

        if "results" not in self.df.columns:
            Logger.log("Expected key 'results' not found in DataFrame", "error")
            raise KeyError("Expected key 'results' not found in DataFrame")

        # Explode 'results' array and flatten
        extracted_df = self.df.select(explode(col("results")).alias("result")).select("result.*")
        return extracted_df
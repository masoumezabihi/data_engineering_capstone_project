from pyspark.sql import SparkSession
from DataIngestion import DataIngestion
from EODDataLoader import EODDataLoader
from StorageConfig import StorageConfig
from Constants import RAW_CSV_PATH, RAW_JSON_PATH, COMMON_EVENTS_OUTPUT_CSV, COMMON_EVENTS_OUTPUT_JSON, FINAL_TRADE_OUTPUT, FINAL_QUOTE_OUTPUT


class ETLPipeline:
    def __init__(self, spark, storage_cfg):
        self.ingestor = DataIngestion(spark, storage_cfg)
        self.loader = EODDataLoader(spark, storage_cfg)

    def run(self):
        # Step 1: ingest raw data
        #df_csv = ingestor.read_csv(RAW_CSV_PATH)
        #df_json = ingestor.read_json(RAW_JSON_PATH)

        # Step2: Write the ingested data to partitioned Parquet files
        #self.ingestor.write_partitioned_parquet(df_csv, "partition", "overwrite", COMMON_EVENTS_OUTPUT_CSV)
        #self.ingestor.write_partitioned_parquet(df_json, "partition", "overwrite", COMMON_EVENTS_OUTPUT_JSON)


        # Step 3: load partitioned trade data and write final trade data to cloud storage
        trade_common = self.loader.load_data("T")
        self.loader.write_partitioned_parquet(trade_common, "trade_dt", "overwrite", FINAL_TRADE_OUTPUT)

        # Step 4: load partitioned quote data and write final quote data to cloud storage
        quote_common = self.loader.load_data("Q")
        self.loader.write_partitioned_parquet(quote_common, "trade_dt", "overwrite", FINAL_QUOTE_OUTPUT)
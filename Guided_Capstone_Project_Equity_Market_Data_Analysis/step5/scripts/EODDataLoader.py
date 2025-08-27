from pyspark.sql import SparkSession
from StorageConfig import StorageConfig
from Constants import RAW_CSV_PATH, RAW_JSON_PATH, COMMON_EVENTS_OUTPUT_CSV, COMMON_EVENTS_OUTPUT_JSON
import pyspark.sql.functions as F
from pyspark.sql.window import Window
from pyspark.sql.functions import row_number
from StorageHandler import StorageHandler
import logging
from DataIngestion import DataIngestion

logger = logging.getLogger(__name__)

class EODDataLoader(StorageHandler):
    def __init__(self, spark, storage: StorageConfig):
        super().__init__(spark, storage.container_name, storage.account_name)
        self.key = storage.account_key

    def _load_trades(self):
        try:
            logger.info("Loading trade data...")
            path = self._make_path(f"{COMMON_EVENTS_OUTPUT_CSV}/partition=T")
            trade_common = self.spark.read.parquet(path)

            trade = trade_common.select(
                F.col("trade_dt"), F.col("symbol"), F.col("exchange"),
                F.col("event_tm"), F.col("event_seq_nb"), F.col("arrival_tm"),
                F.col("trade_pr")
            )

            trade_corrected = self._apply_latest(
                trade,
                ["trade_dt", "symbol", "exchange", "event_tm", "event_seq_nb"],
                "arrival_tm"
            )

            logger.info("Trade data loaded successfully.")
            return trade_corrected
        except Exception as e:
            logger.error(f"Error loading trades: {e}")
            raise

    def _load_quotes(self):
        try:
            logger.info("Loading quote data...")
            path_csv = self._make_path(f"{COMMON_EVENTS_OUTPUT_CSV}/partition=Q")
            path_json = self._make_path(f"{COMMON_EVENTS_OUTPUT_JSON}/partition=Q")
            quote_common = self.spark.read.parquet(path_csv, path_json)

            quote = quote_common.select(
                F.col("trade_dt"), F.col("symbol"), F.col("exchange"),
                F.col("event_tm"), F.col("event_seq_nb"), F.col("arrival_tm"),
                F.col("bid_pr")
            )

            quote_corrected = self._apply_latest(
                quote,
                ["trade_dt", "symbol", "exchange", "event_tm", "event_seq_nb"],
                "arrival_tm"
            )

            logger.info("Quote data loaded successfully.")
            return quote_corrected
        except Exception as e:
            logger.error(f"Error loading quotes: {e}")
            raise

    def load_data(self, rec_type):
        try:
            if rec_type == "T":
                return self._load_trades()
            elif rec_type == "Q":
                return self._load_quotes()
            else:
                raise ValueError("Invalid rec_type. Must be 'T' or 'Q'.")
        except Exception as e:
            logger.error(f"Error in load_data for rec_type={rec_type}: {e}")
            raise

    def _apply_latest(self, df, partition_cols, order_col):
        windowSpec  = Window.partitionBy(*partition_cols).orderBy(F.col(order_col).desc())
        return df.withColumn("row_number",row_number().over(windowSpec)) \
            .filter(F.col("row_number") == 1) \
            .drop("row_number")

from pyspark.sql import SparkSession
from StorageConfig import StorageConfig
from Constants import RAW_CSV_PATH, RAW_JSON_PATH, COMMON_EVENTS_OUTPUT_CSV, COMMON_EVENTS_OUTPUT_JSON
import pyspark.sql.functions as F
from pyspark.sql.window import Window
from pyspark.sql.functions import row_number
from StorageHandler import StorageHandler


class EODDataLoader(StorageHandler):
    def __init__(self, spark, storage: StorageConfig):
        super().__init__(spark, storage.container_name, storage.account_name)
        self.key = storage.account_key

    def _load_trades(self):
        """Load trade data from CSV files, parse it, and write to Parquet."""
        trade_common = self.spark.read.parquet(self._make_path(f"{COMMON_EVENTS_OUTPUT_CSV}/partition=T"))
       
        trade = trade_common.select(F.col("trade_dt"), F.col("symbol"), F.col("exchange"), F.col("event_tm"),
                                    F.col("event_seq_nb"), F.col("arrival_tm"), F.col("trade_pr"))
        
        trade_corrected = self._apply_latest(trade, ["trade_dt", "symbol", "exchange", "event_tm", "event_seq_nb"], "arrival_tm")
       
        return trade_corrected

    def _load_quotes(self):
        """Load quote data from CSV and JSON files, parse it, and write to Parquet."""
        trade_common = self.spark.read.parquet(self._make_path(f"{COMMON_EVENTS_OUTPUT_CSV}/partition=Q"),
        self._make_path(f"{COMMON_EVENTS_OUTPUT_JSON}/partition=Q"))
       
        trade = trade_common.select(F.col("trade_dt"), F.col("symbol"), F.col("exchange"), F.col("event_tm"),
                                    F.col("event_seq_nb"), F.col("arrival_tm"), F.col("bid_pr"))
        
        trade_corrected = self._apply_latest(trade, ["trade_dt", "symbol", "exchange", "event_tm", "event_seq_nb"], "arrival_tm")
       
        return trade_corrected

    def load_data(self, rec_type):
        """Dispatch to trade or quote loader based on rec_type ('T' or 'Q')."""
        if rec_type == "T":
            return self._load_trades()
        elif rec_type == "Q":
            return self._load_quotes()
        else:
            raise ValueError("Invalid rec_type. Must be 'T' or 'Q'.")

    def _apply_latest(self, df, partition_cols, order_col):
        windowSpec  = Window.partitionBy(*partition_cols).orderBy(F.col(order_col).desc())
        return df.withColumn("row_number",row_number().over(windowSpec)) \
            .filter(F.col("row_number") == 1) \
            .drop("row_number")

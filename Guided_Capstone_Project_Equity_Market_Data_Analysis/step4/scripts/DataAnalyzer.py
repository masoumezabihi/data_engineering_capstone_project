from StorageHandler import StorageHandler
from StorageConfig import StorageConfig
from datetime import datetime, timedelta
from pyspark.sql.types import (
    StructType, StructField, StringType, IntegerType, DecimalType)

event_schema = StructType([
    StructField("rec_type", StringType(), True),
    StructField("symbol", StringType(), True),
    StructField("event_tm", StringType(), True),
    StructField("exchange", StringType(), True),
    StructField("event_seq_nb", IntegerType(), True),
    StructField("arrival_tm", StringType(), True),
    StructField("bid_pr", DecimalType(10, 2), True),
    StructField("bid_size", IntegerType(), True),
    StructField("ask_pr", DecimalType(10, 2), True),
    StructField("ask_size", IntegerType(), True),
    StructField("trade_pr", DecimalType(10, 2), True),
    StructField("mov_avg_pr",  DecimalType(10,2), True)
])

class DataAnalyzer(StorageHandler):
    def __init__(self, spark, storage: StorageConfig):
        super().__init__(spark, storage.container_name, storage.account_name)

    def analyze_trade_data(self, base_dir, trade_date):
        main_df = self.spark.read.parquet(self._make_path(f"{base_dir}/trade_dt={trade_date}"))
        self.creaeTradeHiveTable("trades", base_dir)

        self.calculate_30min_moving_avg(trade_date)
        self.calculate_prior_day_last_trade(trade_date)


    def enrich_quote_data(self, base_dir, trade_date):
        main_df = self.spark.read.parquet(self._make_path(f"{base_dir}/trade_dt={trade_date}"))
        self.creaeQuoteHiveTable("quotes", base_dir)

        quote_union = self.spark.sql("""
        SELECT
            NULL AS trade_dt,
            'T' AS rec_type, 
            symbol,
            NULL AS exchange,
            CAST(event_tm AS STRING) AS event_tm,
            event_seq_nb,
            NULL AS arrival_tm,
            trade_pr,
            NULL AS bid_pr,
            NULL AS bid_size,
            NULL AS ask_pr,
            NULL AS ask_size,
            mov_avg_pr
        FROM temp_trade_moving_avg

        UNION ALL

        SELECT
            trade_dt,
            'Q' AS rec_type,
            symbol,
            exchange,
            event_tm,
            event_seq_nb,
            arrival_tm,
            trade_pr,
            bid_pr,
            bid_size,
            ask_pr,
            ask_size,
            NULL AS mov_avg_pr
        FROM quotes
        """)


        quote_union.createOrReplaceTempView("quote_union")
    

        quote_union_update = self.spark.sql("""
        SELECT *,
            LAST_VALUE(trade_pr, TRUE) OVER(
                PARTITION BY symbol, exchange
                ORDER BY event_tm
                ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
            ) AS last_trade_pr,
            LAST_VALUE(mov_avg_pr, TRUE) OVER(
                PARTITION BY symbol, exchange
                ORDER BY event_tm
                ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
            ) AS last_mov_avg_pr
            FROM quote_union
        """)

        quote_union_update.createOrReplaceTempView("quote_union_update")
        

        quote_update = self.spark.sql("""
        select trade_dt, symbol, event_tm, event_seq_nb, exchange,
        bid_pr, bid_size, ask_pr, ask_size, last_trade_pr, last_mov_avg_pr
        from quote_union_update
        where rec_type = 'Q'
        """)
        quote_update.createOrReplaceTempView("quote_update")

        quote_final = self.spark.sql("""
        select /*+ BROADCAST(tls) */
            qu.trade_dt,
            qu.symbol,
            qu.event_tm,
            qu.event_seq_nb,
            qu.exchange,
            qu.bid_pr,
            qu.bid_size,
            qu.ask_pr,
            qu.ask_size,
            qu.last_trade_pr,
            qu.last_mov_avg_pr,
            (qu.bid_pr - tls.last_pr) AS bid_pr_mv,
            (qu.ask_pr - tls.last_pr) AS ask_pr_mv
        from quote_update qu
        left join temp_last_trade tls 
        on qu.symbol = tls.symbol and qu.exchange = tls.exchange
        """)
        return quote_final


    def calculate_30min_moving_avg(self, trade_date):
        """ Calculate 30-minute moving average for trade data and store it in a Hive table.
        """

        df = self.spark.sql("select symbol, event_tm, event_seq_nb, trade_pr from trades where trade_dt = '{}'".format(trade_date))
        df.createOrReplaceTempView("tmp_trade_moving_avg")

        mov_avg_df = self.spark.sql("""
        select symbol, event_seq_nb, trade_pr,
        CAST(UNIX_TIMESTAMP(event_tm, 'yyyy-MM-dd HH:mm:ss.SSS') AS BIGINT) as event_tm,
        AVG(trade_pr) OVER(
            PARTITION BY symbol
            ORDER BY CAST(UNIX_TIMESTAMP(event_tm, 'yyyy-MM-dd HH:mm:ss.SSS') AS BIGINT)
            RANGE BETWEEN 1800 PRECEDING AND CURRENT ROW
        ) as mov_avg_pr
        from tmp_trade_moving_avg
        """)

        mov_avg_df.write.mode("overwrite").saveAsTable("temp_trade_moving_avg")

    def calculate_prior_day_last_trade(self, trade_date):
        prev_date = datetime.strptime(trade_date, "%Y-%m-%d") - timedelta(days=1)
        prev_date_str = prev_date.strftime("%Y-%m-%d")

        df = self.spark.sql("select symbol, exchange, event_tm, event_seq_nb, trade_pr from trades where trade_dt = '{}'".format(prev_date_str))
        df.createOrReplaceTempView("tmp_last_trade")
    
        last_pr_df = self.spark.sql("""
        SELECT exchange, symbol, trade_pr AS last_pr
        FROM (
            SELECT symbol, exchange, event_tm, event_seq_nb, trade_pr,
                ROW_NUMBER() OVER (
                    PARTITION BY symbol, exchange
                    ORDER BY event_tm DESC
                ) AS rn
            FROM tmp_last_trade
        ) a
        WHERE rn = 1
        """)

        last_pr_df.write.mode("overwrite").saveAsTable("temp_last_trade")
    
    def creaeTradeHiveTable(self, table_name, directory):
        path = self._make_path(directory)
        self.spark.sql(f"""
            CREATE EXTERNAL TABLE IF NOT EXISTS {table_name} (
                symbol STRING,
                exchange STRING,
                event_tm STRING,
                event_seq_nb INT,
                arrival_tm STRING,
                trade_pr DECIMAL(10,2)
            )
            PARTITIONED BY (trade_dt STRING)
            STORED AS PARQUET
            LOCATION '{path}'
            """)
        
        self.spark.sql(f"MSCK REPAIR TABLE {table_name}")

    def creaeQuoteHiveTable(self, table_name, directory):
        path = self._make_path(directory)
        self.spark.sql(f"""
            CREATE EXTERNAL TABLE IF NOT EXISTS {table_name} (
                symbol STRING, 
                exchange STRING,
                event_tm STRING,
                event_seq_nb INT,
                arrival_tm STRING,
                trade_pr DECIMAL(10,2),
                bid_pr DECIMAL(10,2),
                bid_size INT,
                ask_pr DECIMAL(10,2),
                ask_size INT
            )
            PARTITIONED BY (trade_dt STRING)
            STORED AS PARQUET
            LOCATION '{path}'
            """)
        
        self.spark.sql(f"MSCK REPAIR TABLE {table_name}")
        
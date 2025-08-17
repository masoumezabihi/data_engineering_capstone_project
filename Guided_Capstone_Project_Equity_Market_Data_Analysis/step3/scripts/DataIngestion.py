import json
from collections import namedtuple
from pyspark.sql.types import (
    StructType, StructField, StringType, IntegerType, DecimalType
)
from decimal import Decimal
from StorageConfig import StorageConfig
from StorageHandler import StorageHandler


common_event = namedtuple("common_event", [
    "trade_dt", "rec_type", "symbol", "exchange",
    "event_tm", "event_seq_nb", "arrival_tm",
    "trade_pr", "bid_pr", "bid_size", "ask_pr", "ask_size",
    "partition"
])

event_schema = StructType([
    StructField("trade_dt", StringType(), True),
    StructField("rec_type", StringType(), True),
    StructField("symbol", StringType(), True),
    StructField("exchange", StringType(), True),
    StructField("event_tm", StringType(), True),
    StructField("event_seq_nb", IntegerType(), True),
    StructField("arrival_tm", StringType(), True),
    StructField("trade_pr", DecimalType(10, 2), True),
    StructField("bid_pr", DecimalType(10, 2), True),
    StructField("bid_size", IntegerType(), True),
    StructField("ask_pr", DecimalType(10, 2), True),
    StructField("ask_size", IntegerType(), True),
    StructField("partition", StringType(), True)
])

BAD_RECORD = common_event(None, "B", None, None, None, None, None, None, None, None, None, None, "B")


def _safe_decimal(value):
    try:
        return Decimal(value) if value is not None else None
    except Exception:
        return None

def _safe_int(value):
    try:
        return int(value) if value is not None else None
    except Exception:
        return None


def parse_json(line: str):
    try:
        record = json.loads(line)
        rec_type = record.get("event_type")

        if rec_type == "T":
            required = ["trade_dt", "symbol", "exchange", "event_tm", "event_seq_nb", "file_tm", "trade_pr"]
            if all(k in record for k in required):
                return common_event(
                    trade_dt=record["trade_dt"],
                    rec_type="T",
                    symbol=record["symbol"],
                    exchange=record["exchange"],
                    event_tm=record["event_tm"],
                    event_seq_nb=_safe_int(record["event_seq_nb"]),
                    arrival_tm=record["file_tm"],
                    trade_pr=_safe_decimal(record["trade_pr"]),
                    bid_pr=None, bid_size=None,
                    ask_pr=None, ask_size=None,
                    partition="T"
                )

        elif rec_type == "Q":
            required = ["trade_dt", "symbol", "exchange", "event_tm", "event_seq_nb", "file_tm",
                        "bid_pr", "bid_size", "ask_pr", "ask_size"]
            if all(k in record for k in required):
                return common_event(
                    trade_dt=record["trade_dt"],
                    rec_type="Q",
                    symbol=record["symbol"],
                    exchange=record["exchange"],
                    event_tm=record["event_tm"],
                    event_seq_nb=_safe_int(record["event_seq_nb"]),
                    arrival_tm=record["file_tm"],
                    trade_pr=None,
                    bid_pr=_safe_decimal(record["bid_pr"]),
                    bid_size=_safe_int(record["bid_size"]),
                    ask_pr=_safe_decimal(record["ask_pr"]),
                    ask_size=_safe_int(record["ask_size"]),
                    partition="Q"
                )
        return BAD_RECORD

    except Exception:
        return BAD_RECORD


def parse_csv(line: str):
    try:
        record = line.split(",")
        rec_type = record[2]

        if rec_type == "T":
            return common_event(
                trade_dt=record[0],
                rec_type="T",
                symbol=record[3],
                exchange=record[6],
                event_tm=record[1],
                event_seq_nb=_safe_int(record[5]),
                arrival_tm=record[4],
                trade_pr=_safe_decimal(record[7]),
                bid_pr=None, bid_size=None,
                ask_pr=None, ask_size=None,
                partition="T"
            )

        elif rec_type == "Q":
            return common_event(
                trade_dt=record[0],
                rec_type="Q",
                symbol=record[3],
                exchange=record[6],
                event_tm=record[1],
                event_seq_nb=_safe_int(record[5]),
                arrival_tm=record[4],
                trade_pr=None,
                bid_pr=_safe_decimal(record[7]),
                bid_size=_safe_int(record[8]),
                ask_pr=_safe_decimal(record[9]),
                ask_size=_safe_int(record[10]),
                partition="Q"
            )
        return BAD_RECORD

    except Exception:
        return BAD_RECORD


class DataIngestion(StorageHandler):
    def __init__(self, spark, storage: StorageConfig):
        super().__init__(spark, storage.container_name, storage.account_name)
        self.key = storage.account_key  

    def read_csv(self, path_pattern):
        raw = self.spark.sparkContext.textFile(self._make_path(path_pattern))
        parsed = raw.map(parse_csv)
        return self.spark.createDataFrame(parsed, schema=event_schema)

    def read_json(self, path_pattern):
        raw = self.spark.sparkContext.textFile(self._make_path(path_pattern))
        parsed = raw.map(parse_json)
        return self.spark.createDataFrame(parsed, schema=event_schema)
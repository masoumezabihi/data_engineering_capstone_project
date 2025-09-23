from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col
from pyspark.sql.types import StructType, StringType, DoubleType, StructField

# Define schema for transactions
schema = StructType([
    StructField("source", StringType()),
    StructField("target", StringType()),
    StructField("amount", DoubleType()),
    StructField("currency", StringType())
])

spark = SparkSession.builder \
    .appName("FraudDetector") \
    .getOrCreate()

# Read from Kafka
df = spark.readStream.format("kafka") \
    .option("kafka.bootstrap.servers", "kafka:9092") \
    .option("subscribe", "queueing.transactions") \
    .option("startingOffsets", "earliest") \
    .load()

# Parse JSON
parsed = df.selectExpr("CAST(value AS STRING)") \
    .select(from_json(col("value"), schema).alias("data")) \
    .select("data.*")

# Simple fraud rule: amount > 900
fraud = parsed.filter(col("amount") > 900)
legit = parsed.filter(col("amount") <= 900)

# Write to Kafka
fraud.selectExpr("to_json(struct(*)) AS value") \
    .writeStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "kafka:9092") \
    .option("topic", "streaming.transactions.fraud") \
    .option("checkpointLocation", "/tmp/fraud-checkpoint") \
    .start()

legit.selectExpr("to_json(struct(*)) AS value") \
    .writeStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "kafka:9092") \
    .option("topic", "streaming.transactions.legit") \
    .option("checkpointLocation", "/tmp/legit-checkpoint") \
    .start()

spark.streams.awaitAnyTermination()

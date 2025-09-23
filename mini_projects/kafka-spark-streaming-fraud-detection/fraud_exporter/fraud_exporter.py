import json
import time
from kafka import KafkaConsumer
from prometheus_client import Counter, Gauge, Histogram, start_http_server

# -----------------------
# Config
# -----------------------
KAFKA_BOOTSTRAP = "kafka:9092"
FRAUD_TOPIC = "streaming.transactions.fraud"
LEGIT_TOPIC = "streaming.transactions.legit"
METRICS_PORT = 8000

# -----------------------
# Metrics
# -----------------------
fraud_counter = Counter(
    "fraud_transactions_total",
    "Total number of fraudulent transactions observed",
    ["currency"]
)

legit_counter = Counter(
    "legit_transactions_total",
    "Total number of legitimate transactions observed",
    ["currency"]
)

fraud_ratio = Gauge(
    "fraud_ratio",
    "Ratio of fraudulent to total transactions"
)

fraud_consumer = KafkaConsumer(
    FRAUD_TOPIC,
    bootstrap_servers=[KAFKA_BOOTSTRAP],
    auto_offset_reset="latest",
    enable_auto_commit=True,
    value_deserializer=lambda m: json.loads(m.decode("utf-8"))
)

legit_consumer = KafkaConsumer(
    LEGIT_TOPIC,
    bootstrap_servers=[KAFKA_BOOTSTRAP],
    auto_offset_reset="latest",
    enable_auto_commit=True,
    value_deserializer=lambda m: json.loads(m.decode("utf-8"))
)


fraud_total = 0
legit_total = 0

def update_fraud_ratio():
    total = fraud_total + legit_total
    if total > 0:
        fraud_ratio.set(fraud_total / total)


if __name__ == "__main__":
    start_http_server(METRICS_PORT)

    while True:
        for msg in fraud_consumer.poll(timeout_ms=1000).values():
            for record in msg:
                data = record.value
                currency = data.get("currency", "unknown")
                fraud_counter.labels(currency=currency).inc()
                fraud_total += 1
                update_fraud_ratio()

        for msg in legit_consumer.poll(timeout_ms=1000).values():
            for record in msg:
                data = record.value
                currency = data.get("currency", "unknown")
                legit_counter.labels(currency=currency).inc()
                legit_total += 1
                update_fraud_ratio()

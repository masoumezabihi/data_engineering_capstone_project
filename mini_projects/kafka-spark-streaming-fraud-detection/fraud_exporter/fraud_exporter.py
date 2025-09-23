import json
import time
from kafka import KafkaConsumer
from prometheus_client import Counter, start_http_server

KAFKA_BOOTSTRAP = "kafka:9092"
TOPIC = "streaming.transactions.fraud"
METRICS_PORT = 8000

fraud_counter = Counter(
    "fraud_transactions_total",
    "Total number of fraud transactions observed",
    ["currency"]
)

consumer = KafkaConsumer(
    TOPIC,
    bootstrap_servers=[KAFKA_BOOTSTRAP],
    auto_offset_reset="latest",
    enable_auto_commit=True,
    value_deserializer=lambda m: json.loads(m.decode("utf-8"))
)

start_http_server(METRICS_PORT)
print(f"Prometheus metrics available at http://localhost:{METRICS_PORT}/metrics")

for msg in consumer:
    data = msg.value
    currency = data.get("currency", "unknown")
    fraud_counter.labels(currency=currency).inc()
    print(f"Fraud transaction counted: {data}")

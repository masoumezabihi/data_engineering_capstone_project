import os
import json
import time
import signal
import sys
from kafka import KafkaProducer
from transaction import create_random_transaction

KAFKA_BROKER_URL = os.environ.get("KAFKA_BROKER_URL")
TRANSACTIONS_TOPIC = os.environ.get("TRANSACTIONS_TOPIC")
TPS = float(os.environ.get("TRANSACTIONS_PER_SECOND", "1"))
SLEEP_TIME = 1.0 / TPS if TPS > 0 else 1.0

stop = False
def handle(sig, frame):
    global stop
    stop = True

signal.signal(signal.SIGINT, handle)
signal.signal(signal.SIGTERM, handle)

def main():
    print(f"Producer started. Brokers={KAFKA_BROKER_URL}, topic={TRANSACTIONS_TOPIC}, tps={TPS}")

    # kafka-python expects bootstrap_servers as list or comma-separated string
    producer = KafkaProducer(
        bootstrap_servers=KAFKA_BROKER_URL,
        value_serializer=lambda v: json.dumps(v).encode("utf-8"),
        retries=5,
    )

   
    try:
        while not stop:
            txn = create_random_transaction()
            producer.send(TRANSACTIONS_TOPIC, value=txn)
            # optional debug print
            print(txn)
            time.sleep(SLEEP_TIME)
    except Exception as e:
        print("Producer error:", e, file=sys.stderr)
    finally:
        try:
            producer.flush(timeout=10)
        except Exception:
            pass
        print("Producer stopped.")

if __name__ == "__main__":
    main()

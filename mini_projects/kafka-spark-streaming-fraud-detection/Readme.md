## Streaming Fraud Detection System with Kafka, Spark Streaming, Prometheus & Grafana
### Overview

This project implements a real-time fraud detection pipeline using:
- Apache Kafka (KRaft mode) – distributed event streaming
- Apache Spark Structured Streaming – processes transaction streams in real time
- Python (consumer & generator) – generates synthetic transactions and consumes detected fraud events
- Fraud Exporter – exposes fraud detection counts as Prometheus metrics
- Prometheus – scrapes metrics from Spark & custom exporter
- Grafana – visualizes fraud detections and system metrics
- Docker Compose – containerized deployment for all components

### Objectives

- Build a real-time fraud detection system with streaming technologies
- Show how Spark Structured Streaming integrates with Kafka
- Provide monitoring & observability with Prometheus + Grafana
- Deploy everything in Docker with separate composition files

### Project Structure

<pre>
kafka-spark_streaming_fraud_detection/
├── consumer/              
│   ├── Dockerfile
│   ├── app.py
│   └── requirements.txt
├── generator/            
│   ├── Dockerfile
│   ├── app.py
│   └── transactions.py
├── fraud_exporter/        
│   ├── Dockerfile
│   ├── exporter.py
│   └── requirements.txt
├── prometheus/            
│   └── prometheus.yml
├── docker-compose.kafka.yaml  
├── docker-compose.yml         
└── README.md

</pre>

## Setup & Deployment
1. Clone the Repository
git clone https://github.com/masoumezabihi/data_engineering_capstone_project/tree/main/mini_projects/kafka-spark-streaming-fraud-detection
<br>cd kafka-spark_streaming_fraud_detection

2. Create Kafka Network
- Both compose files share the same network:
docker network create kafka-network

3. Start Kafka (KRaft mode)
docker-compose -f docker-compose.kafka.yaml up -d

4. Start the Fraud Detection System
docker-compose up -d

This will bring up:
- **Kafka (KRaft mode)** – event streaming backbone
- **Transaction Generator** – produces synthetic transactions into Kafka
- **Spark Consumer** – detects fraud using Structured Streaming
- **Fraud Exporter** – exposes fraud counts as Prometheus metrics
- **Prometheus** – scrapes metrics
- **Grafana** – visualizes fraud detection stats and system metrics

### How It Works
Transaction Generator
Generates random transactions with schema:

{
  "source": "account123",
  "target": "account987",
  "amount": 754.23,
  "currency": "USD"
}


- Publishes them into Kafka topic queueing.transactions.
- Fraud Detection Logic (Spark Streaming)
- Consumes transactions from Kafka
- Flags a transaction as fraud if:
    Amount ≥ 900 USD
- Writes results into two topics:
    streaming.transactions.legit
    streaming.transactions.fraud
- Fraud Exporter
    Reads fraud detection counts
    Exposes metrics in Prometheus format (HTTP endpoint)
- Monitoring
  Prometheus scrapes metrics from Spark + fraud exporter
- Grafana dashboards show:
- Fraud detections per second

### Dashboards & Metrics
Prometheus

📍 URL: http://localhost:9090

Prometheus scrapes metrics from the fraud-exporter service. The main metrics available:
| Metric                       | Description                                                           |
| ---------------------------- | --------------------------------------------------------------------- |
| `fraud_transactions_total`   | Total number of fraudulent transactions observed, labeled by currency |
| `legit_transactions_total`   | Total number of legitimate transactions observed, labeled by currency |
| `fraud_ratio`                | Ratio of fraudulent to total transactions (0–1 or as a percentage)    |


Grafana

📍 URL: http://localhost:3000

Login credentials:

Username: admin<br>
Password: admin

The Grafana dashboard includes three panels:
- Fraud Transactions Total – counts of fraudulent transactions over time.
- Legit Transactions Total – counts of legitimate transactions over time.
- Fraud Ratio – gauge showing the proportion of fraud relative to total transactions.

  Dashbaord:
  ![Grafana Dashboard](iamges/grafana.gif)

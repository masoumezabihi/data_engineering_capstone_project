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
- Transaction Generator (produces synthetic transactions)
- Spark Consumer (detects fraud using Structured Streaming)
- Fraud Exporter (exposes Prometheus metrics)
- Prometheus
- Grafana

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

Grafana

📍 URL: http://localhost:3000

Login credentials:
  Username: admin
  Password: admin


Dashboards included:


Improve fraud detection logic with machine learning

Add real-time alerts (Slack, Email, Webhooks) for fraud events

Scale to a multi-broker Kafka cluster

Store transactions in Cassandra, PostgreSQL, or Elasticsearch

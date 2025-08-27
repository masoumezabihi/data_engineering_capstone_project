# Equity Market Data Analysis - Guided Capstone Project

Spring Capital is an investment bank that relies heavily on Big Data analytics to make critical investment decisions based on high-frequency stock market data. This project builds an end-to-end scalable data pipeline to ingest, process, and analyze stock trade and quote data from multiple exchanges.

---

## Project Overview

This project implements a data pipeline to handle **high-frequency financial data** including trades and quotes. The pipeline processes billions of records daily, stores structured data efficiently, and produces analytical results to support business analysts at Spring Capital.

Key business goals include:
- Track latest trade price and prior day closing price
- Compute 30-minute moving average trade price to smooth out noise
- Analyze bid and ask price movement relative to last day’s trade price

---

## Data Sources and Formats

| Data Type | Description | Format |
| --------- | ----------- | ------ |
| Trades    | Records of transactions of stock shares | CSV / JSON |
| Quotes    | Best bid/ask price updates for stocks | CSV / JSON |

### Trade Data Columns

| Column            | Type      |
|-------------------|-----------|
| Trade Date        | Date      |
| Record Type       | Varchar(1) (T = Trade) |
| Symbol            | String    |
| Execution ID      | String    |
| Event Time        | Timestamp |
| Event Sequence No | Int       |
| Exchange          | String    |
| Trade Price       | Decimal   |
| Trade Size        | Int       |

### Quote Data Columns

| Column            | Type      |
|-------------------|-----------|
| Trade Date        | Date      |
| Record Type       | Varchar(1) (Q = Quote) |
| Symbol            | String    |
| Event Time        | Timestamp |
| Event Sequence No | Int       |
| Exchange          | String    |
| Bid Price         | Decimal   |
| Bid Size          | Int       |
| Ask Price         | Decimal   |
| Ask Size          | Int       |

---

## Technical Requirements

- Use **Apache Spark** for scalable data processing
- Ingest data continuously and pre-process as it arrives throughout the trading day
- Maintain source data partitioned by date for efficient querying
- Correct duplicate or updated records by unique identifier
- Produce analytical outputs for quote data based on trade indicators

---

## Project Steps

### Step 1: Database Table Design

- Design daily partitioned tables for trade and quote data
- Optimize schema for daily volume and high query performance
- Use composite keys (trade date, record type, symbol, event time, event seq) for uniqueness

### Step 2: Data Ingestion

- Ingest raw CSV/JSON files containing mixed trade and quote records
- Identify records by `rec_type` column (`T` or `Q`)
- Drop any malformed records that do not conform to schema

### Step 3: End of Day Batch Load

- Aggregate and deduplicate all records for the day based on unique ID
- Discard old records if updated records with same ID arrive
- Load final daily tables for trade and quote at 5 PM every day

### Step 4: Analytical ETL Job

For each quote event, calculate:
- Latest trade price **before** the quote timestamp
- 30-minute moving average trade price **before** the quote timestamp
- Bid and ask price movement relative to prior day's last trade price

### Step 5: Pipeline Orchestration

- Implement workflows for ingestion, batch load, and analytical ETL jobs
- Track job statuses in a dedicated status table
- Support job retry and rerun upon failure

---

## Azure Storage Setup

- Data is stored and read from **Azure Blob Storage** containers
- Credentials and container info  set in env file.
- Update the `StorageConfig` with your Azure storage account details

---

## Environment Setup

Create a `.env` file at the root of the project with the following content (replace placeholders with your actual credentials):

```env
AZURE_STORAGE_ACCOUNT="your_azure_storage_account_name"
AZURE_STORAGE_KEY="storage_account_access_key"
AZURE_CONTAINER="your_container_name"

DB_USER=<your databse user name>
DB_PASSWORD=<your password>
DB_HOST=127.0.0.1
DB_NAME=<database name>
DB_PORT=5432

JOB_TRACKER_TABLE=<table name>
```

Important: Do not commit this file or your credentials to any public repository.

## Running the Pipeline 
### Run Data Ingestion
```bash
./run_ingestion.sh 
This script ingests raw trade and quote files from Azure Blob Storage, validates them, and stores pre-processed data.

### Run ETL Analytical 
```bash
./run_etl.sh
This script ingests raw trade and quote files from Azure Blob Storage, validates them, and stores pre-processed data.

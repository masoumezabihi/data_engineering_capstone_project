# Prototyping Data Pipeline

This project is part of the **Data Engineering Bootcamp Capstone – Step 5: Prototype Your Data Pipeline**. The goal is to build an automated data pipeline that acquires, transforms, and stores OpenFDA drug event data using Python and PostgreSQL.

---

## Features

- ✅ Full data pipeline: **Download → Transform → Load**
- ✅ Uses object-oriented Python
- ✅ Loads data into **PostgreSQL** using `pandas.to_sql`
- ✅ Automatic logging of all actions and metrics
- ✅ Environment-based configuration for credentials and paths
- ✅ Designed to run end-to-end without user interaction

---
## Setup Instructions

### 1. Clone the Repository

git clone (https://github.com/masoumezabihi/data_engineering_capstone_project/edit/main/protyping_Data_pipeline)<br>
cd prototyping_Data_pipeline

### 2. Create a `.env` File

A sample environment configuration file `env.example` is included in the repo.  
- Copy it to `.env` and update the values with your own credentials:
- In the root directory, create a file named .env with the following content:
 - Local folder to store raw data: RAW_DATA_FOLDER=raw_data/
 - PostgreSQL configuration
```bash
    POSTGRES_USER=<your_postgres_username>
    POSTGRES_PASSWORD=<your_postgres_password>
    POSTGRES_HOST=localhost
    POSTGRES_PORT=<your_postgres_port>
    POSTGRES_DB=<database_name><br>
```
⚠️ Important: Never commit your .env file to version control.

### 3. Running the Pipeline

To execute the full pipeline:   python scripts/pipeline_runner.py <br>
This script orchestrates the entire process:
- Downloads and extracts OpenFDA drug event files
- Transforms and cleans the data
- Loads the cleaned data into a PostgreSQL table
- Logs all relevant metrics and errors

---

## Logging

Logs include:
- File download status
- Number of records and columns
- Errors, warnings, and progress updates
- Logs are  stored in open_fda_etl.log using Logger.py.

---
## PostgreSQL Integration

- Cleaned data is loaded into a PostgreSQL database table (e.g., report)
- Schema is auto-generated using pandas.to_sql()
- PostgreSQL credentials are managed via the .env file

---
## Requirements
- Python 3.8+
- PostgreSQL server

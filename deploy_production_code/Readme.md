# OpenFDA Adverse Event Data Pipeline on Azure Databricks

This repository contains a data pipeline that processes the [OpenFDA Drug Adverse Event](https://open.fda.gov/apis/drug/event/) dataset using **Azure Databricks** and **PySpark**.

The pipeline reads raw JSON data from **Azure Blob Storage**, performs data transformation and normalization using PySpark, and writes the processed output as partitioned **Parquet files** back to Blob Storage for downstream analysis.

---

## 📌 Data Extraction (Handled Separately)

> ⚠️ The **data extraction** step—retrieving data from the OpenFDA API—is not included in this repository.

Raw JSON files were collected from the OpenFDA public API in a separate step (via manual download or external script) and uploaded to **Azure Blob Storage**, which serves as the raw data layer for this pipeline.

This project focuses on the core **ELT pipeline**, which includes:
- **Loading** raw JSON files from Blob Storage,
- **Transforming** the data into structured DataFrames using PySpark,
- **Saving** the curated data back to Blob Storage in Parquet format.

This separation between extraction and transformation reflects common practice in modern data lake architectures.


---

## Dataset
- **Source:** [OpenFDA Drug Adverse Event Data](https://open.fda.gov/apis/drug/event/)
- **Size:** ~50 GB
- **Format:** JSON 
- **Contains:** Adverse drug event reports submitted to the FDA by healthcare professionals, manufacturers, and consumers.

---

## Tech Stack

- **Platform:** Azure Databricks
- **Language:** Python (PySpark)
- **Cluster:** Single node, 8 cores
- **Storage:** Azure Blob Storage
- **Output Format:** Parquet

---

##  Pipeline Steps

1. **Ingest Data**
   - Load raw OpenFDA adverse event JSON files from Azure Blob Storage.
   - Use `self.spark.read.option("multiLine", "true").json(blob_path)`

2. **Data Transformation**
   - Flattening: All nested JSON fields are flattened for easier analysis.
   - Cleaning: Columns with consistently missing data are dropped.
   - Normalization: Date strings are parsed and standardized.
   - Enrichment: Fields like sex and age_group are enriched with human-readable labels using mapping dictionaries.
   - Deduplication: Duplicate entries (e.g., reports with the same safetyreportid) are dropped.
   - Validation: Missing data percentages are calculated before dropping columns.
    
3. **Save as Parquet**
   - Write the cleaned and transformed data back to Azure Blob Storage.
   - Save in Parquet format.

---

## How to Run

### Prerequisites
- Azure subscription
- Azure Databricks workspace
- Azure Blob Storage account
- Databricks cluster with:
  - Databricks runtime: 16.4 LTS (includes Apache Spark 3.5.2, Scala 2.12)
  - Node type: Standard_D8s_v3 (32GB Memory, 8 cores)
 
 ### Steps to Execute the Pipeline
 
 #### 1. Upload Raw Dataset to Azure Blob Storage
- Place the OpenFDA adverse event JSON files directly into your Azure Blob Storage.

 #### 2. Set Up Configuration in Azure Databricks
 Before running the ETL pipeline, you need to configure your cluster to access your Azure Blob Storage and define the necessary environment variables.
 > ##### a. Configure Spark with Storage Access Key
 1. Go to your cluster in Databricks (e.g., `openfda-etl-cluster`)
2. Click **Edit > Advanced Options > Spark**
3. Under **Spark Config**, add the following entry (replace with your actual storage account name and key):
spark.hadoop.fs.azure.account.key.<your-storage-account>.blob.core.windows.net <your-storage-access-key>>
 > ##### b. Set Environment Variables for Storage
Under the same **Advanced Options**, scroll to the **Environment Variables** section and set the following:
AZURE_STORAGE_ACCOUNT=<your-storage-account>
AZURE_CONTAINER=<your-blob-container>

These variables will be accessible inside your Python code using `os.environ`:
```python
import os

storage_account = os.getenv("AZURE_STORAGE_ACCOUNT")
container = os.getenv("AZURE_CONTAINER")
```
This allows dynamic and cleaner configuration without hardcoding paths in your scripts.

#### 3 Upload Python Code to Azure Databricks
Upload your entire Python module or scripts (Extractor.py, Transformer.py, Loader.py, ETLProcessor.py, Logger.py, etc.) into Workspace > Users > YourUser > Repos or Folders in Databricks.

#### 4 Create and Run a Databricks Job
- Go to Jobs > Create Job
- Set the main Python file to run: e.g., ETLProcessor.py or a wrapper script.
- Choose your cluster (single node with 8 cores).
- Optionally schedule it or run it manually.

---

## Output
Transformed data is saved in your configured output/ path in Azure Blob Storage.<br>
- Format: Parquet
- Tables: report, patient, drug, reaction

---

## Testing & Logs
Custom logging is handled via the Logger class.<br>
Output logs are printed to Databricks driver logs (accessible from the job run page).<br>
Errors during transformation or loading are captured and reported in logs.


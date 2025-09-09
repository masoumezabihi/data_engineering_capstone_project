# OpenFDA Adverse Event Data Pipeline on Azure Databricks

This repository contains a data pipeline that processes the [OpenFDA Drug Adverse Event](https://open.fda.gov/apis/drug/event/) dataset using **Azure Databricks**. 
The pipeline reads raw JSON data from Azure Blob Storage, performs data transformation using PySpark, and saves the processed data as partitioned Parquet files.

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
 
 ### Execution Steps

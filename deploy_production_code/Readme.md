# OpenFDA Adverse Event Data Pipeline on Azure Databricks

This repository contains a data pipeline that processes the [OpenFDA Drug Adverse Event](https://open.fda.gov/apis/drug/event/) dataset using **Azure Databricks**. 
The pipeline reads raw JSON data from Azure Blob Storage, performs data transformation using PySpark, and saves the processed data as partitioned Parquet files.

---

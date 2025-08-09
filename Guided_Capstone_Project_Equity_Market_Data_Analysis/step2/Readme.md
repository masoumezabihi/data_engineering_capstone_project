# Azure Data Processing Pipeline with PySpark

## Overview
This project demonstrates how to build an **ETL (Extract, Transform, Load)** pipeline on Azure using **PySpark**.  
The workflow starts with **local source data**, uploads it to **Azure Blob Storage** using AzCopy, processes it with PySpark, and writes the results in **Parquet format**, partitioned for efficient querying.


## Features
- **Local → Azure Blob Storage** upload using `azcopy`.
- Supports **CSV** and **JSON** source data formats.
- Converts raw data into a **common schema** for analysis.
- Writes data in **Parquet format**, partitioned by record type (`T` or `Q`).
- Uses an **`.env` file** for secure storage of sensitive configuration values.
- Handles **bad records** gracefully.

  
## Prerequisites
Before running the project, ensure you have:
- An **Azure Storage Account** with a **Blob container**.
- **AzCopy** installed for uploading data.
- **Apache Spark** environment (local or cluster).

## Environment Variables (`.env` file)
Create a `.env` file in your project root to store your Azure Storage credentials securely.  
The file should have the following format (replace the values with your own credentials):

```env
AZURE_STORAGE_ACCOUNT="storage-account-name"
AZURE_STORAGE_KEY="access_key"
AZURE_CONTAINER="container_name"

# Capstone Project – Step 6: Scale Your Prototype

## Project Overview
In this step of the capstone project, the data pipeline prototype was scaled using Apache Spark on Azure Databricks with Azure Blob Storage as the input/output source.
The goal was to:
- Migrate the Python ETL pipeline to PySpark for large-scale processing.
- Leverage Azure Databricks clusters for distributed computing.
- Store input data in Azure Blob Storage and save processed data as Parquet.
- Compare performance improvements with the earlier prototype.

  ## Spark cluster Configuration for Azure Blob Storage
  For this project, I configured the Azure Storage credentials directly in
  the Databricks Cluster UI → Spark Config by setting environment variables and Hadoop configurations
   (e.g., AZURE_STORAGE_ACCOUNT, AZURE_CONTAINER, and spark.hadoop.fs.azure.account.key.<account>.blob.core.windows.net).

  This approach works for development and demonstration purposes.
  However, the recommended best practice for production environments is to use Databricks Secret Scopes (or integrate with Azure Key Vault) to securely manage credentials.


 ## Execution Workflow

1. Upload Python scripts  to Databricks Workspace.
2. Create a Databricks Job / pipeline using these scripts.
3. Configure the cluster with the correct Azure Blob Storage credentials (environment variables and Spark config).
4. Run the Databricks Job, pointing to the OpenFDA dataset in Blob Storage.
5. Output is written as Parquet files back to Azure Blob Storage.

## Results & Observations

The ETL pipeline successfully processed the full dataset in Azure Databricks.
Output Parquet files were generated in the Blob Storage container.
Performance improvements were expected with a multi-node cluster, but:
Note: Since this project used a free (non–Pay-As-You-Go) Azure account, only a single-node Databricks cluster was available.
As a result, performance gains from distributed execution could not be fully demonstrated.


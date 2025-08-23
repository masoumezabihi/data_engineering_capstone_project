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

- The PySpark ETL pipeline successfully processed the datasets both locally (3GB) and in Azure Databricks (50GB).
Output Parquet files were generated in Azure Blob Storage as expected.

> [!NOTE] 
> The datasets used for local testing (3GB) and cloud execution (50GB) are different, so a direct comparison is not meaningful.
> Additionally, due to using a single-node Databricks cluster (free-tier account), the benefits of Spark’s distributed processing could not be fully observed.
> Despite this, the pipeline demonstrates scalability and is ready to leverage multi-node clusters for larger datasets in       production environments.


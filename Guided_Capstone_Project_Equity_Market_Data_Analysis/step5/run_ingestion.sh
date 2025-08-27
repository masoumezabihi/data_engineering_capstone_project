#!/bin/sh
set -e

echo "Starting ingestion Job..."

spark-submit \
  --master local[*] \
  --jars jars/azure-storage-8.6.5.jar,jars/hadoop-azure-3.3.0.jar,jars/jetty-client-9.4.48.v20220622.jar,jars/jetty-http-9.4.48.v20220622.jar,jars/jetty-io-9.4.48.v20220622.jar,jars/jetty-util-9.4.48.v20220622.jar,jars/jetty-util-ajax-9.4.48.v20220622.jar \
  --py-files scripts/DataIngestion.py,scripts/StorageHandler.py,scripts/StorageConfig.py \
  scripts/main.py ingestion

echo "Ingestion job finished successfully."

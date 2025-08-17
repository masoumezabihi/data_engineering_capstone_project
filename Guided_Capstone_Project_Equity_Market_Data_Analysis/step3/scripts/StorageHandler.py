from StorageConfig import StorageConfig

class StorageHandler:
    def __init__(self, spark, container, storage_account):
        self.spark = spark
        self.container = container
        self.storage_account = storage_account

    def _make_path(self, path_pattern, sub_dir=""):
        return f"wasbs://{self.container}@{self.storage_account}.blob.core.windows.net/{sub_dir}{path_pattern}"

    def write_partitioned_parquet(self, df, partition_key, mode, output_dir):
        path = self._make_path("", output_dir)
        df.write.partitionBy(partition_key).mode(mode).parquet(path)


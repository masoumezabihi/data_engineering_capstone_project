import pytest
from pyspark.sql import SparkSession
from etl.ETLProcessor import ETLProcessor
from etl.config import BlobStorageConfig


@pytest.fixture(scope="module")
def spark():
    return SparkSession.builder.master("local[*]").appName("unit-tests").getOrCreate()

@pytest.fixture
def mock_blob_config():
    return BlobStorageConfig(
        storage_account="mockstorage",
        storage_key="mockkey",
        container="mockcontainer",
        path_pattern="raw/data/"
    )

def test_make_path(spark, mock_blob_config):
    etl = ETLProcessor(spark, mock_blob_config)
    path = etl._make_path("myfolder/file.json")
    expected = "wasbs://mockcontainer@mockstorage.blob.core.windows.net/myfolder/file.json"
    assert path == expected
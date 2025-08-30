import pytest
from pyspark.sql import SparkSession
from etl.ETLProcessor import ETLProcessor
from etl.config import BlobStorageConfig
from etl.Loader import Loader



@pytest.fixture(scope="session")
def spark_session():
    spark = (
        SparkSession.builder.master("local[*]")
        .appName("pytest-transformer")
        .getOrCreate()
    )
    yield spark
    spark.stop()

def test_loader_with_none_dataframe(spark_session, tmp_path, caplog):
    loader = Loader(spark_session, str(tmp_path))

    with pytest.raises(Exception):
        loader.write_table(None, "test_table")

    assert "Failed to write" in caplog.text

def test_loader_with_empty_table(spark_session, tmp_path, caplog):
    data = [("Alice", 25), ("Bob", 30), ("Charlie", 22)]
    columns = ["name", "age"]
    df = spark_session.createDataFrame(data, columns)

    loader = Loader(spark_session, str(tmp_path))

    with pytest.raises(Exception):
         loader.write_table(df, "")

    assert "Failed to write" in caplog.text



def test_write_table(spark_session, tmp_path):
    data = [("Alice", 25), ("Bob", 30), ("Charlie", 22)]
    columns = ["name", "age"]

    df = spark_session.createDataFrame(data, columns)

    # Create loader instance with temporary directory
    output_path = tmp_path 
    loader = Loader(spark_session, str(output_path))

    # Act: write the table
    table_name = "test_table"
    loader.write_table(df, table_name)

    # Assert: check if file was created
    written_path = output_path / table_name
    assert written_path.exists()

    # Optional: read back and compare
    df_read = spark_session.read.parquet(str(written_path))
    assert df_read.count() == 3
    assert df_read.columns == ["name", "age"]
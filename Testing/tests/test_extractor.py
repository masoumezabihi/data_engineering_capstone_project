import pytest
from pyspark.sql import SparkSession
from etl.Extractor import Extractor
from etl.config import BlobStorageConfig
from pyspark.sql.types import (
    StructType, StructField, StringType, ArrayType
)

# ------------------ SCHEMAS ------------------ #

reaction_schema = ArrayType(
    StructType([
        StructField("reactionmeddraversionpt", StringType(), True),
        StructField("reactionmeddrapt", StringType(), True),
        StructField("reactionoutcome", StringType(), True),
    ])
)

drug_schema = ArrayType(
    StructType([
        StructField("drugcharacterization", StringType(), True),
        StructField("medicinalproduct", StringType(), True),
        StructField("drugindication", StringType(), True),
        StructField("actiondrug", StringType(), True),
        StructField("drugadditional", StringType(), True),
        StructField("activesubstance", StructType([
            StructField("activesubstancename", StringType(), True),
        ])),
        StructField("openfda", StructType([
            StructField("application_number", ArrayType(StringType()), True)
        ])),
    ])
)

patient_schema = StructType([
    StructField("patientsex", StringType(), True),
    StructField("reaction", reaction_schema, True),
    StructField("drug", drug_schema, True),
])

results_schema = ArrayType(
    StructType([
        StructField("safetyreportversion", StringType(), True),
        StructField("safetyreportid", StringType(), True),
        StructField("primarysourcecountry", StringType(), True),
        StructField("primarysource", StructType([
            StructField("reportercountry", StringType(), True),
            StructField("qualification", StringType(), True),
        ])),
        StructField("sender", StructType([
            StructField("sendertype", StringType(), True),
            StructField("senderorganization", StringType(), True),
        ])),
        StructField("receiver", StructType([
            StructField("receivertype", StringType(), True),
            StructField("receiverorganization", StringType(), True),
        ])),
        StructField("patient", patient_schema, True),
    ])
)

meta_schema = StructType([
    StructField("disclaimer", StringType(), True)
])

full_schema = StructType([
    StructField("meta", meta_schema, True),
    StructField("results", results_schema, True)
])

# ------------------ FIXTURES ------------------ #

@pytest.fixture(scope="session")
def spark_session():
    spark = (
        SparkSession.builder.master("local[*]")
        .appName("pytest-spark-session")
        .getOrCreate()
    )
    yield spark
    spark.stop()


@pytest.fixture
def mock_blob_config():
    return BlobStorageConfig(
        storage_account="mockstorage",
        storage_key="mockkey",
        container="mockcontainer",
        path_pattern="mockpath/*.json"
    )


@pytest.fixture
def mock_openfda_data():
    return {
        "meta": {
            "disclaimer": "Do not rely on openFDA to make decisions regarding medical care..."
        },
        "results": [
            {
                "safetyreportversion": "2",
                "safetyreportid": "13526645",
                "primarysourcecountry": "US",
                "primarysource": {
                    "reportercountry": "COUNTRY NOT SPECIFIED",
                    "qualification": "5"
                },
                "sender": {
                    "sendertype": "2",
                    "senderorganization": "FDA-Public Use"
                },
                "receiver": {
                    "receivertype": "6",
                    "receiverorganization": "FDA"
                },
                "patient": {
                    "patientsex": "2",
                    "reaction": [
                        {
                            "reactionmeddraversionpt": "20.0",
                            "reactionmeddrapt": "Incorrect route of drug administration",
                            "reactionoutcome": "6"
                        }
                    ],
                    "drug": [
                        {
                            "drugcharacterization": "1",
                            "medicinalproduct": "COSENTYX",
                            "drugindication": "PRODUCT USED FOR UNKNOWN INDICATION",
                            "actiondrug": "5",
                            "drugadditional": "3",
                            "activesubstance": {
                                "activesubstancename": "SECUKINUMAB"
                            },
                            "openfda": {
                                "application_number": ["BLA125504"]
                            }
                        }
                    ]
                }
            }
        ]
    }

# ------------------ TESTS ------------------ #

def test_load_data_success(mocker, spark_session, mock_blob_config, mock_openfda_data):
    # Create mock DataFrame
    mock_df = spark_session.createDataFrame([mock_openfda_data], schema=full_schema)

    # Mock Spark read.option().json()
    mock_json_reader = mocker.Mock()
    mock_json_reader.option.return_value.json.return_value = mock_df

    mocker.patch.object(type(spark_session), 'read', return_value=mock_json_reader)

    # Run test
    extractor = Extractor(spark_session, mock_blob_config)
    assert extractor.load_data() is True
    df = extractor.df
    assert df is not None

    # Check extract_results
    if "results" in df.columns:
        extracted = extractor.extract_results()
        assert "safetyreportid" in extracted.columns
    else:
        with pytest.raises(KeyError):
            extractor.extract_results()


def test_load_data_failure(mocker, spark_session, mock_blob_config):
    extractor = Extractor(spark_session, mock_blob_config)

    mock_read = mocker.Mock()
    mock_option = mocker.Mock()
    mock_read.option.return_value = mock_option
    mock_option.json.side_effect = Exception("Simulated read failure")

    mocker.patch.object(type(spark_session), "read", new_callable=mocker.PropertyMock, return_value=mock_read)

    assert extractor.load_data() is False
    assert extractor.df is None


def test_extract_results_no_data(mocker, spark_session, mock_blob_config):
    extractor = Extractor(spark_session, mock_blob_config)

    # Don't call load_data()
    with pytest.raises(ValueError):
        extractor.extract_results()


def test_extract_results_missing_results_field(mocker, spark_session, mock_blob_config):
    extractor = Extractor(spark_session, mock_blob_config)

    # Create DataFrame with no 'results' field
    mock_df = spark_session.createDataFrame([{"meta": {"disclaimer": "Test disclaimer"}}])

    mock_read = mocker.Mock()
    mock_option = mocker.Mock()
    mock_read.option.return_value = mock_option
    mock_option.json.return_value = mock_df

    mocker.patch.object(type(spark_session), "read", new_callable=mocker.PropertyMock, return_value=mock_read)

    extractor.load_data()
    with pytest.raises(KeyError):
        extractor.extract_results()

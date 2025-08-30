import pytest
from pyspark.sql import Row
from etl.Transformer import Transformer
from etl.Logger import Logger
from pyspark.sql.types import StructType, StructField, StringType, ArrayType
from pyspark.sql import SparkSession
from unittest.mock import patch
from pyspark.sql.functions import lit
from pyspark.sql.types import (
    StructType, StructField, StringType, ArrayType
)
from datetime import date


@pytest.fixture(scope="session")
def spark_session():
    spark = (
        SparkSession.builder.master("local[*]")
        .appName("pytest-transformer")
        .getOrCreate()
    )
    yield spark
    spark.stop()


@pytest.fixture
def mock_data(spark_session):
    schema = StructType([
        StructField("safetyreportid", StringType(), True),
        StructField("patient", StructType([
            StructField("patientsex", StringType(), True),
            StructField("patientonsetage", StringType(), True),
            StructField("patientonsetageunit", StringType(), True),
            StructField("patientweight", StringType(), True),
            StructField("patientagegroup", StringType(), True),
            StructField("summary", StructType([
                StructField("narrativeincludeclinical", StringType(), True),
            ])),
            StructField("patientdeath", StructType([
                StructField("patientdeathdate", StringType(), True),
                StructField("patientdeathdateformat", StringType(), True),
            ])),
            StructField("drug", ArrayType(StructType([
                StructField("drugcharacterization", StringType(), True),
                StructField("medicinalproduct", StringType(), True),
                StructField("drugindication", StringType(), True),
                StructField("drugauthorizationnumb", StringType(), True),
                StructField("drugdosagetext", StringType(), True),
                StructField("drugstartdate", StringType(), True),
                StructField("drugenddate", StringType(), True),
                StructField("drugenddateformat", StringType(), True),
                StructField("drugstartdateformat", StringType(), True),
                StructField("drugtreatmentduration", StringType(), True),
                StructField("openfda", StructType([
                    StructField("application_number", ArrayType(StringType()), True)
                ])),
            ]))),
            StructField("reaction", ArrayType(StructType([
                StructField("reactionmeddrapt", StringType(), True),
                StructField("reactionoutcome", StringType(), True),
            ])))
        ]))
    ])

    data = [
        {
            "safetyreportid": "123",
            "patient": {
                "patientsex": "1",
                "patientonsetage": "45",
                "patientonsetageunit": "801",
                "patientweight": "80",
                "patientagegroup": "003",
                "summary": {
                    "narrativeincludeclinical": "Patient experienced headache"
                },
                "patientdeath": {
                    "patientdeathdate": "20210101",
                    "patientdeathdateformat": "102"
                },
                "drug": [
                    {
                        "drugcharacterization": "1",
                        "medicinalproduct": "DRUG_A",
                        "drugindication": "Headache",
                        "drugauthorizationnumb": "XYZ123",
                        "drugdosagetext": "1 tablet daily",
                        "drugstartdate": "20210101",
                        "drugenddate": "20210110",
                        "drugenddateformat": "102",
                        "drugstartdateformat": "102",
                        "drugtreatmentduration": "10",
                        "openfda": {"application_number": ["APP123"]}
                    }
                ],
                "reaction": [
                    {
                        "reactionmeddrapt": "Headache",
                        "reactionoutcome": "2"
                    }
                ]
            }
        }
    ]

    return spark_session.createDataFrame(data, schema=schema)

# ---------------------- TEST CASES ---------------------- #

def test_extract_report_table(mock_data, spark_session):
    transformer = Transformer(spark_session, mock_data)
    report_df = transformer.extract_report_table()

    assert "patient" not in report_df.columns
    assert report_df.count() == 1

def test_extract_report_table_missing_column(spark_session):
    data = [
        {"safetyreportid": "123"}
    ]
    df = spark_session.createDataFrame(data)
    transformer = Transformer(spark_session, df)

    # This should not raise an error, .drop('patient') is safe
    result_df = transformer.extract_report_table()

    # But patient column shouldn't exist
    assert "patient" not in result_df.columns
    assert "safetyreportid" in result_df.columns


def test_extract_patient_table(mock_data, spark_session):
    transformer = Transformer(spark_session, mock_data)
    patient_df = transformer.extract_patient_table()

    assert "onset_age" in patient_df.columns
    assert "sex" in patient_df.columns
    assert patient_df.count() == 1


def test_extract_patient_table_missing_nested_field(spark_session, caplog):
    data = [{
        "safetyreportid": "123",
        "patient": {
            "patientonsetage": "45",
            "patientonsetageunit": "801",
            "patientweight": "80",
            "patientsex": "1",
            "patientagegroup": "003"
            # "summary" and "patientdeath" fields are missing
        }
    }]

    df = spark_session.createDataFrame(data)
    transformer = Transformer(spark_session, df)
    with pytest.raises(Exception):
         transformer.extract_patient_table()

    assert "Column extraction failed" in caplog.text


def test_extract_drug_table(mock_data, spark_session):
    transformer = Transformer(spark_session, mock_data)
    drug_df = transformer.extract_drug_table()

    assert "safetyreportid" in drug_df.columns
    assert "medicinalproduct" in drug_df.columns
    assert drug_df.count() == 1

def test_extract_drug_table_raises_analysis_exception(spark_session, caplog):
    # Data without 'patient.drug' field, so explode will fail
    data = [
        {
            "safetyreportid": "123",
            "patient": {
                # 'drug' key is missing here intentionally to cause failure
                "patientsex": "1"
            }
        }
    ]
    
    df = spark_session.createDataFrame(data)
    transformer = Transformer(spark_session, df)

    with pytest.raises(Exception):
        transformer.extract_drug_table()

    assert "Column extraction failed" in caplog.text


def test_extract_reaction_table(mock_data, spark_session):
    transformer = Transformer(spark_session, mock_data)
    reaction_df = transformer.extract_reaction_table()

    assert "safetyreportid" in reaction_df.columns
    assert "meddrapt" in reaction_df.columns
    assert reaction_df.count() == 1

def test_extract_reaction_table_fail_missing_reaction(spark_session, caplog):
    # Data without 'patient.reaction' to cause failure
    data = [
        {
            "safetyreportid": "123",
            "patient": {
                # 'reaction' field missing intentionally
                "patientsex": "1"
            }
        }
    ]

    df = spark_session.createDataFrame(data)
    transformer = Transformer(spark_session, df)

    with pytest.raises(Exception):
        transformer.extract_reaction_table()

    assert "Column extraction failed" in caplog.text

def test_drop_columns(spark_session):
    df = spark_session.createDataFrame([("1", "A", "B")], ["id", "drop_me", "keep_me"])
    transformer = Transformer(spark_session, df)

    result_df = transformer.drop_columns(df, ["drop_me"])
    assert "drop_me" not in result_df.columns
    assert "keep_me" in result_df.columns

def test_drop_columns_fail_nonexistent_column(spark_session):
    data = [("value1", "value2")]
    df = spark_session.createDataFrame(data, ["col1", "col2"])
    transformer = Transformer(spark_session, df)

    # Try to drop a column that doesn't exist
    columns_to_drop = ["nonexistent_col"]
    result_df = transformer.drop_columns(df, columns_to_drop)

    # The schema should remain unchanged because the column didn't exist
    assert "col1" in result_df.columns
    assert "col2" in result_df.columns
    assert "nonexistent_col" not in result_df.columns  

    # We can also assert that the dataframe content stays the same
    assert result_df.count() == df.count()
    assert result_df.schema == df.schema
    assert result_df.collect() == df.collect()


def test_convert_date_columns(spark_session):
    df = spark_session.createDataFrame([("20230101",)], ["start_date"])
    transformer = Transformer(spark_session, df)

    converted_df = transformer.convert_date_columns(df, ["start_date"])
    assert converted_df.schema["start_date"].dataType.typeName() == "date"
    result = converted_df.collect()[0]["start_date"]
    assert result == date(2023, 1, 1)

def test_convert_date_columns_invalid_column(spark_session):
    df = spark_session.createDataFrame([("20230101",)], ["some_other_column"])
    transformer = Transformer(spark_session, df)

    # start_date doesn't exist
    result_df = transformer.convert_date_columns(df, ["start_date"])  

    # Nothing changes, schema remains the same
    assert "some_other_column" in result_df.columns
    assert "start_date" not in result_df.columns
    assert result_df.schema["some_other_column"].dataType.typeName() == "string"


def test_add_category_label(spark_session):
    df = spark_session.createDataFrame([("1",), ("2",), ("3",)], ["code"])
    transformer = Transformer(spark_session, df)

    mapping = {"1": "Male", "2": "Female"}
    updated_df = transformer.add_category_label(df, "code", "gender", mapping)

    rows = [row["gender"] for row in updated_df.select("gender").collect()]
    assert rows == ["Male", "Female", "Unknown"]


def test_show_missing_percentage(spark_session):
    df = spark_session.createDataFrame([
        ("123", None),
        ("456", "A"),
        ("789", None),
        (None, "B"),
    ], ["id", "value"])

    transformer = Transformer(spark_session, df)
    result_df = transformer.show_missing_percentage(df)

    result = {row["column_name"]: row["percent_missing"] for row in result_df.collect()}
    assert result["value"] == 50.0
    assert result["id"] == 25.0

def test_show_missing_percentage_no_missing_values(spark_session):
    df = spark_session.createDataFrame([
        ("123", "A"),
        ("456", "B"),
        ("789", "C"),
        ("101", "D"),
    ], ["id", "value"])

    transformer = Transformer(spark_session, df)
    result_df = transformer.show_missing_percentage(df)

    result = {row["column_name"]: row["percent_missing"] for row in result_df.collect()}

    # Checking that no column has missing values
    assert result["id"] == 0.0 
    assert result["value"] == 0.0 

def test_show_missing_percentage_empty_dataframe(spark_session):
    schema = StructType([
        StructField("id", StringType(), True),
        StructField("value", StringType(), True)
    ])

    df = spark_session.createDataFrame([], schema)

    transformer = Transformer(spark_session, df)
    result_df = transformer.show_missing_percentage(df)

    result = {row["column_name"]: row["percent_missing"] for row in result_df.collect()}

    # Checking that the percentages are all 0 because the DataFrame is empty
    assert result["id"] == 0.0 
    assert result["value"] == 0.0  

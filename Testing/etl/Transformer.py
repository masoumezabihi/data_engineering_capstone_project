import json
import uuid
from pyspark.sql import SparkSession
from pyspark.sql import DataFrame
from pyspark.sql.functions import col, lit, to_date, udf, explode
from pyspark.sql.types import StringType
from etl.Logger import Logger
from pyspark.sql import functions as F
from pyspark.sql.functions import when, col


class Transformer:
    def __init__(self, spark:SparkSession, df: DataFrame):
        """
        Transformer initialized with raw DataFrame (from extracted JSON).
        """
        self.spark = spark
        self.df = df

    def extract_report_table(self):
        """
        Removes nested 'patient' fields to isolate report data.
        """
        Logger.log("Extracting report table...")
        report_df = self.df.drop('patient')
        Logger.log(f"Report table extracted with {report_df.count()} rows.")
        return report_df

    def extract_patient_table(self):
        """
        Extracts and flattens patient-related fields.
        """
        Logger.log("Extracting patient table...")

        try:
            patient_df = self.df.select(
            col("safetyreportid"),
            col("patient.patientonsetage").alias("onset_age"),
            col("patient.patientonsetageunit").alias("onset_age_unit"),
            col("patient.patientweight").alias("weight"),
            col("patient.patientsex").alias("sex"),
            col("patient.patientagegroup").alias("age_group"),
            col("patient.summary.narrativeincludeclinical").alias("narrative"),
            col("patient.patientdeath.patientdeathdate").alias("death_date"),
            col("patient.patientdeath.patientdeathdateformat").alias("death_date_format"),
            )
        except Exception as e:
            Logger.log(f"Column extraction failed: {e}", level='error')
            raise

        Logger.log(f"Patient table extracted with {patient_df.count()} rows.")
        return patient_df

    def extract_drug_table(self):
        """
        Extracts drug records with flattened openfda fields.
        """
        Logger.log("Extracting drug table...")

        try:
            exploded = self.df.select("safetyreportid", explode("patient.drug").alias("drug"))

            drug_df = exploded.select(
                "safetyreportid",
                col("drug.drugcharacterization").alias("characterization"),
                col("drug.medicinalproduct").alias("medicinalproduct"),
                col("drug.drugauthorizationnumb").alias("authorizationnumb"),
                col("drug.drugdosagetext").alias("dosage_text"),
                col("drug.drugindication").alias("indication"),
                col("drug.drugstartdate").alias("start_date"),
                col("drug.drugenddate").alias("end_date"),
                col("drug.drugenddateformat").alias("end_date_format"),
                col("drug.drugstartdateformat").alias("start_date_format"),
                col("drug.drugtreatmentduration").alias("treatment_duration"),
                col("drug.openfda").cast("string").alias("openfda")
                )
        except Exception as e:
            Logger.log(f"Column extraction failed: {e}", "error")
            raise

        Logger.log(f"Drug table extracted with {drug_df.count()} rows.")
        return drug_df

    def extract_reaction_table(self):
        """
        Extracts reactions as a flat table.
        """
        Logger.log("Extracting reaction table...")

        try:
            exploded = self.df.select("safetyreportid", explode("patient.reaction").alias("reaction"))

            reaction_df = exploded.select(
                "safetyreportid",
                col("reaction.reactionmeddrapt").alias("meddrapt"),
                col("reaction.reactionoutcome").alias("outcome")
                )
        except Exception as e:
            Logger.log(f"Column extraction failed: {e}", "error")
            raise

        Logger.log(f"Reaction table extracted with {reaction_df.count()} rows.")
        return reaction_df

    def drop_columns(self, df: DataFrame, columns: list):
        """
        Drops specified columns from DataFrame if present.
        """
        Logger.log(f"Dropping columns: {columns}")
        for col_name in columns:
            if col_name in df.columns:
                df = df.drop(col_name)
                Logger.log(f"Column {col_name} dropped.")
        return df

    def convert_date_columns(self, df: DataFrame, columns: list, date_format: str = "yyyyMMdd"):
        """
        Converts string columns to date type.
        """
        for col_name in columns:
            if col_name in df.columns:
                Logger.log(f"Converting column {col_name} to date format {date_format}")
                df = df.withColumn(col_name, to_date(col(col_name), date_format))
        return df

    def add_category_label(self, df: DataFrame, column: str, new_column: str, value_map: dict, default_value="Unknown"):
        """
        Adds a new column with labels using a dictionary and when/otherwise logic.

        Parameters:
            df (DataFrame): Input DataFrame.
            column (str): Name of the column to map.
            new_column (str): Name of the new label column.
            value_map (dict): Dictionary mapping values to labels.
            default_value (str): Default value if no match is found.

        Returns:
            DataFrame: Updated DataFrame with new column.
        """

        if column not in df.columns:
            return df

            
        expr = None
        for key, value in value_map.items():
            condition = (col(column) == key)
            expr = when(condition, value) if expr is None else expr.when(condition, value)

        expr = expr.otherwise(default_value)
        return df.withColumn(new_column, expr)

    def show_missing_percentage(self, df: DataFrame):
        """
        Calculates the percentage of missing (null) values for each column
        using Spark expressions.

        Returns:
            A Spark DataFrame with columns: ["column_name", "percent_missing"]
        """
        Logger.log("Calculating missing value percentages (optimized)...")

        total_rows = df.count()

        if total_rows == 0:
            Logger.log("DataFrame is empty. Returning 0% for all columns.")
            return self.spark.createDataFrame(
                [(col_name, 0.0) for col_name in df.columns],
                ["column_name", "percent_missing"]
            )

        # Create expressions for null percentages
        missing_exprs = [
            ((F.count(F.when(F.col(c).isNull(), 1)) / total_rows) * 100).alias(c)
            for c in df.columns
        ]

        # Perform aggregation (1 row, many columns)
        percent_row = df.agg(*missing_exprs).collect()[0]

        # Convert to list of (column_name, percent_missing)
        percent_list = [(col_name, percent_row[col_name]) for col_name in df.columns]

        return self.spark.createDataFrame(percent_list, ["column_name", "percent_missing"])


    def normalize_schema(self, df: DataFrame, expected_columns: list):
        """
        Ensures DataFrame contains all expected columns.
        """
        for col_name in expected_columns:
            if col_name not in df.columns:
                df = df.withColumn(col_name, lit(None).cast(StringType()))
        return df.select(*expected_columns)

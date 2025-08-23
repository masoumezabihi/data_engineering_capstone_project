from pyspark.sql import SparkSession
from pyspark.sql.functions import col, when, to_date, lit, monotonically_increasing_id
from Extractor import Extractor
from Transformer import Transformer
from Loader import Loader
from Logger import Logger
import uuid
from config import BlobStorageConfig
from pyspark import StorageLevel


MISSING_PERCENTAGE_THRESHOLD = 95 

class ETLProcessor:
    def __init__(self, spark: SparkSession, blob_config: BlobStorageConfig):
        self.spark = spark
        self.blob_config = blob_config

    def _make_path(self, path):
        """Constructs a full path for the blob storage."""
        return f"wasbs://{self.blob_config.container}@{self.blob_config.storage_account}.blob.core.windows.net/{path}"

    def run(self):
        Logger.log("Starting Spark ETL process...")

        blob_path = self._make_path(self.blob_config.path_pattern)
        Logger.log(f"Loading data from: {blob_path}", "info")

        # Read JSON from blob
        extractor = Extractor(self.spark, self.blob_config)
        if extractor.load_data():
            records_df = extractor.extract_results()
            records_df.persist(StorageLevel.MEMORY_AND_DISK) 
            Logger.log(f"Extracted {records_df.count()} records.")
            transformer = Transformer(self.spark, records_df)

            try:
                # REPORT TABLE
                report_df = transformer.extract_report_table()
                report_df = report_df.dropna(subset=['safetyreportid']).dropDuplicates(['safetyreportid'])
                columns_to_drop = ["transmissiondateformat", "receivedateformat", "receiptdateformat"]
                report_df = transformer.drop_columns(report_df, columns_to_drop)
                report_df = transformer.convert_date_columns(report_df, ['receivedate', 'transmissiondate', 'receiptdate'])
                
                
                # PATIENT TABLE
                patient_df = transformer.extract_patient_table()

                patient_df = patient_df.withColumn("id", monotonically_increasing_id())
                patient_df = transformer.drop_columns(patient_df, ["death_date_format"])
                patient_df = transformer.convert_date_columns(patient_df, ['death_date'])
                
                missing_df = transformer.show_missing_percentage(patient_df)
                cols_to_drop = [row['column_name'] for row in missing_df.collect() if row['percent_missing'] > MISSING_PERCENTAGE_THRESHOLD]
                patient_df = transformer.drop_columns(patient_df, cols_to_drop)

                agegroup_map = {'1': 'Neonate', '2': 'Infant', '3': 'Child', '4': 'Adolescent', '5': 'Adult', '6': 'Elderly'}
                sex_map = {'0': 'Unknown', '1': 'Male', '2': 'Female'}

                patient_df = transformer.add_category_label(patient_df, 'age_group', 'age_group_label', value_map = agegroup_map)
                patient_df = transformer.add_category_label(patient_df, 'sex', 'sex_label', value_map = sex_map)
                
                # DRUG TABLE
                drug_df = transformer.extract_drug_table()
                Logger.log(f"Extracted drug table with {drug_df.count()} rows.")

                drug_df = drug_df.withColumn("id", monotonically_increasing_id())
                drug_df = transformer.drop_columns(drug_df, ["end_date_format", "start_date_format"])
                drug_df = transformer.convert_date_columns(drug_df, ["end_date", "start_date"])

                # REACTION TABLE
                reaction_df = transformer.extract_reaction_table()
                Logger.log(f"Extracted reaction table with {reaction_df.count()} rows.")

                reaction_df = reaction_df.withColumn("id", monotonically_increasing_id())

                missing_df = transformer.show_missing_percentage(reaction_df)
                cols_to_drop = [row['column_name'] for row in missing_df.collect() if row['percent_missing'] > MISSING_PERCENTAGE_THRESHOLD]
                reaction_df = transformer.drop_columns(reaction_df, cols_to_drop)

                Logger.log("Data transformation completed.")

            except Exception as e:
                Logger.log(f"An error occurred during data transformation: {str(e)}", 'error')
                return

            # LOAD

            
            records_df.unpersist()
            loader = Loader(self.spark,  output_path = self._make_path("output/"))
            try:
                loader.write_table(report_df, "report")
                Logger.log("Report table loaded into the database.")

                loader.write_table(patient_df, "patient")
                Logger.log("Patient table loaded into the database.")

                loader.write_table(drug_df, "drug")
                Logger.log("Drug table loaded into the database.")

                loader.write_table(reaction_df, "reaction")
                Logger.log("Reaction table loaded into the database.")

            except Exception as e:
                Logger.log(f"Failed to load data into the database: {str(e)}") 

            Logger.log("ETL process completed successfully.")
        else:
            Logger.log("Failed to load data. ETL process aborted.")

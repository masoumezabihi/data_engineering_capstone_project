from Extractor import Extractor
from Transformer import Transformer
from Loader import Loader
from sqlalchemy.dialects.postgresql import JSONB
from Logger import Logger

class ETLProcessor:
    def __init__(self, json_file, username, password, host, port, database):
        self.json_file = json_file
        self.username = username
        self.password = password
        self.host = host
        self.port = port
        self.database = database

    def run(self):
        Logger.log("Starting ETL process...")

        extractor = Extractor(self.json_file)
        if extractor.load_data():
            records = extractor.extract_results()
            transformer = Transformer(records)

            # Report
            report_df = transformer.extract_report_table()
            report_df = transformer.drop_high_missing(report_df)
            report_df = transformer.convert_dates(report_df, ["receiptdate", "receivedate", "transmissiondate"])

            # Patient
            patient_df = transformer.extract_patient_table()
            patient_df = transformer.drop_high_missing(patient_df)
            patient_df = transformer.convert_dates(patient_df, ["death_date"])
            patient_df = transformer.add_category_label(patient_df, "sex", "sex_label", {"1": "Male", "2": "Female", "0": "Unknown"})
            patient_df = transformer.add_category_label(patient_df, "age_group", "age_group_label", {
                "1": "Neonate", "2": "Infant", "3": "Child", "4": "Adolescent", "5": "Adult", "6": "Elderly"
            })

            # Drug
            drug_df = transformer.extract_drug_table()
            drug_df = transformer.drop_high_missing(drug_df)
            drug_df = transformer.convert_dates(drug_df, ["start_date", "end_date"])

            # Reaction
            reaction_df = transformer.extract_reaction_table()
            reaction_df = transformer.drop_high_missing(reaction_df)

            # Load
            loader = Loader(self.username, self.password, self.host, self.port, self.database)
            loader.write_table(report_df, "report")
            loader.write_table(patient_df, "patient")
            loader.write_table(drug_df, "drug", dtype={"openfda": JSONB})
            loader.write_table(reaction_df, "reaction")

            Logger.log("ETL completed successfully.")
        else:
            Logger.log("Failed to load data.")

from Extractor import Extractor  
from Transformer import Transformer  
from Loader import Loader 
from sqlalchemy.dialects.postgresql import JSONB
import os
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

        # Load the data using the Extractor
        extractor = Extractor(self.json_file) 
        if extractor.load_data(): 
            records = extractor.extract_results() 
            Logger.log(f"Extracted {len(records)} records.")

          
            transformer = Transformer(records) 
            report_df = transformer.extract_report_table()
            Logger.log(f"Extracted report table with {len(report_df)} rows.")
            patient_df = transformer.extract_patient_table()
            Logger.log(f"Extracted patient table with {len(patient_df)} rows.")
            drug_df = transformer.extract_drug_table()
            Logger.log(f"Extracted drug table with {len(drug_df)} rows.")
            reaction_df = transformer.extract_reaction_table()
            Logger.log(f"Extracted reaction table with {len(reaction_df)} rows.")
            
            Logger.log("Data transformation completed.")

        
            loader = Loader(self.username, self.password, self.host, self.port, self.database)
            try:
                loader.write_table(report_df, "report")
                Logger.log("Report table loaded into the database.")

                loader.write_table(patient_df, "patient")
                Logger.log("Patient table loaded into the database.")

                loader.write_table(drug_df, "drug", dtype={"openfda": JSONB})
                Logger.log("Drug table loaded into the database.")

                loader.write_table(reaction_df, "reaction")
                Logger.log("Reaction table loaded into the database.")

            except Exception as e:
                Logger.log(f"Failed to load data into the database: {e}")

            Logger.log("ETL process completed successfully.")
        else:
            Logger.log("Failed to load data. ETL process aborted.")

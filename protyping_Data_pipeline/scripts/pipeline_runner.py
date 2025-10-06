import os
import logging
from ETLProcessor import ETLProcessor  
from Logger import Logger  
import os
from dotenv import load_dotenv
from Ingestor import DataIngestor


class MainApp:
    def __init__(self, raw_data_folder, username, password, host, port, database):
        Logger.setup_logger('logs', 'open_fda_etl.log')  

        self.raw_data_folder = raw_data_folder
        self.username = username
        self.password = password
        self.host = host
        self.port = port
        self.database = database

        Logger.log(f"Initialized MainApp with folder: {self.raw_data_folder}", 'info')

    def run(self):
        Logger.log("Pipeline starting...", 'info')

        try:
            # Step 1: Ingest Data
            Logger.log("Starting data ingestion...", 'info')
            ingestor = DataIngestor(target_folder=self.raw_data_folder, max_files=5)
            downloaded_files = ingestor.download_and_extract()
            Logger.log(f"Ingestion completed. {len(downloaded_files)} files downloaded.", 'info')

            # Step 2: ETL Process
            Logger.log("Starting ETL process...", 'info')
            for file_path in downloaded_files:
                if file_path.endswith('.json'):
                    Logger.log(f"Processing file: {file_path}")
                    etl_processor = ETLProcessor(file_path, self.username, self.password, self.host, self.port, self.database)
                    etl_processor.run()

            Logger.log("ETL process completed for all files.", 'info')

        except Exception as e:
            Logger.log(f"An error occurred during pipeline execution: {str(e)}", 'error')


if __name__ == "__main__":
    load_dotenv()

    app = MainApp(
        raw_data_folder=os.getenv("RAW_DATA_FOLDER"),
        username=os.getenv("POSTGRES_USER"),
        password=os.getenv("POSTGRES_PASSWORD"),
        host=os.getenv("POSTGRES_HOST"),
        port=int(os.getenv("POSTGRES_PORT")),
        database=os.getenv("POSTGRES_DB")
    )
    app.run()
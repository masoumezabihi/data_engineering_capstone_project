import os
import logging
from ETLProcessor import ETLProcessor  
from Logger import Logger  

class MainApp:
    def __init__(self, json_file, username, password, host, port, database):
        Logger.setup_logger('logs', 'open_fds_etl.log')  

        self.json_file = os.path.join('raw_data', json_file) 
        self.username = username
        self.password = password
        self.host = host
        self.port = port
        self.database = database

    
        Logger.log( f"Initialized MainApp with json_file: {self.json_file}",'info')

    def run(self):
        Logger.log( "ETL process starting...", 'info')

        try:
            etl_processor = ETLProcessor(self.json_file, self.username, self.password, self.host, self.port, self.database)
            etl_processor.run()

            Logger.log( "ETL process completed successfully.", 'info')

        except Exception as e:
            Logger.log(f"An error occurred during ETL processing: {str(e)}", 'error')


# Entry point for the application
if __name__ == "__main__":
    app = MainApp(
        json_file="drug-event-0001-of-0005.json", 
        username="postgres", 
        password="Masoume1367", 
        host="localhost", 
        port=5432, 
        database="openfda_db"
    )
    app.run()

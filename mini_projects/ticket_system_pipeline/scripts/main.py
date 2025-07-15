from DatabaseHandler import DatabaseHandler
from ETLProcessor import ETLProcessor
from Loader import Loader
from Extractor import Extractor
from pathlib import Path
from ReportGenerator import ReportGenerator
from Logger import Logger
from dotenv import load_dotenv
import os
from pathlib import Path

env_path = Path(__file__).resolve().parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

config = {
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'host': os.getenv('DB_HOST'),
    'database': os.getenv('DB_NAME'),
    'port': int(os.getenv('DB_PORT'))
}


BASE_DIR = Path(__file__).resolve().parent
Logger.setup_logger('logs', 'data_pipeline.log') 
Logger.log("ETL pipeline started.", 'info')

try:
    # Initialize and connect to database
    db_handler = DatabaseHandler(config)
    db_handler.connect()
    db_handler.create_third_party_table()

    # Run ETL
    loader = Loader(db_handler)
    etl = ETLProcessor(Extractor(), loader)
    etl.run(BASE_DIR.parent / 'data' / 'third_party_sales_1.csv')

    # Generate report
    try:
        report = ReportGenerator(db_handler.get_connection())
        popular_tickets = report.query_popular_tickets()
        formatted_report = report.format_popular_tickets(popular_tickets)
        Logger.log("Report generated successfully:\n" + formatted_report, 'info')
        print(formatted_report)
    except Exception as e:
        Logger.log(f"Failed to generate report: {e}", 'error')

except Exception as e:
    Logger.log(f"ETL pipeline failed: {e}", 'error')

finally:
    try:
        db_handler.close()
    except Exception as e:
        Logger.log(f"Failed to close DB connection: {e}", 'warning')

Logger.log("ETL pipeline finished.", 'info')

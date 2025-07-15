from DatabaseHandler import DatabaseHandler
from ETLProcessor import ETLProcessor
from Loader import Loader
from Extractor import Extractor
from pathlib import Path
from ReportGenerator import ReportGenerator
from Logger import Logger

# Setup paths and config
config = {
    'user': 'massi_user',
    'password': 'Masoume_1367',
    'host': '127.0.0.1',
    'database': 'ticket_system',
    'port': 3306
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

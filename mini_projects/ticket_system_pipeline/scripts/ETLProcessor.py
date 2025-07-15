from Extractor import Extractor
from Logger import Logger

class ETLProcessor:
    def __init__(self, extractor, loader):
        self.extractor = extractor
        self.loader = loader

    def run(self, source_file):
        
        try:
            raw_data = self.extractor.read_csv(source_file)
            Logger.log(f"Extracted {len(raw_data)} rows from {source_file}", 'info')
        except Exception as e:
            Logger.log(f"Extraction failed: {e}", 'error')
            return

        try:
            self.loader.insert_to_third_party(raw_data)
            Logger.log("Data successfully loaded into the database.", 'info')
        except Exception as e:
            Logger.log(f"Loading failed: {e}", 'error')

        Logger.log("ETL process completed.", 'info')

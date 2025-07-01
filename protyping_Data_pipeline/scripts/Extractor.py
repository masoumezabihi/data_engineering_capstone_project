import json
from pathlib import Path
from Logger import Logger 

class Extractor:
    def __init__(self, path: str):
        """
        Initialize the Extractor with the path to the input file.

        Parameters:
            path (str): Path to the input file.
        """
        self.path = Path(path)
        self.data = None

    def load_data(self):
        """
        Load the input file and handle potential errors.
        
        Returns:
            bool: True if the file is loaded successfully, False otherwise.
        """
        try:
            if not self.path.exists():
                Logger.log(f"Error: File not found: {self.path}")
                return False
            content = self.path.read_text(encoding="utf-8")
            self.data = json.loads(content)
            Logger.log(f"Successfully loaded data from {self.path}")
            return True
        except FileNotFoundError:
            Logger.log(f"Error: File not found: {self.path}")
        except json.JSONDecodeError:
            Logger.log(f"Error: Invalid JSON format in: {self.path}")
        except Exception as e:
            Logger.log(f"An unexpected error occurred while loading the file: {e}")
        return False

    def extract_results(self):
        """
        Extracts the 'results' key from the loaded JSON data.
        
        Returns:
            list[dict]: List of dictionaries in the 'results' key, if present.
        
        Raises:
            KeyError: If the 'results' key is not found in the JSON data.
        """
        if self.data is None:
            raise ValueError("JSON data is not loaded. Please call 'load_data()' first.")
        
        if "results" not in self.data:
            raise KeyError("Expected key 'results' not found in JSON.")
        
        Logger.log(f"Extracted {len(self.data['results'])} records from the 'results' key.")
        return self.data["results"]

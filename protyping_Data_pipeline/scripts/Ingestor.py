import requests
import zipfile
import io
import os
import time
from urllib.parse import urlparse
from Logger import Logger  # Assuming you have a Logger class in Logger.py


class DataIngestor:
    def __init__(self, target_folder="raw_data", max_files=1):
        """
        Downloads OpenFDA drug event zip files, extracts JSON, and saves in target_folder.

        Parameters:
            target_folder (str): Folder where JSON files will be stored (created if missing)
            max_files (int): Maximum number of files to download
        """
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.target_folder = os.path.join(project_root, target_folder)
        self.max_files = max_files

        os.makedirs(self.target_folder, exist_ok=True)

    def fetch_partitions(self):
        """Fetch metadata of OpenFDA drug event dataset with retry logic."""
        url = "https://api.fda.gov/download.json"
        max_retries = 3
        delay_seconds = 3

        for attempt in range(1, max_retries + 1):
            try:
                Logger.log(f"Attempt {attempt} to fetch partition metadata...")
                resp = requests.get(url, timeout=10)
                resp.raise_for_status()
                meta = resp.json()
                partitions = meta["results"]["drug"]["event"]["partitions"]
                return partitions[:self.max_files]

            except (requests.exceptions.ConnectionError,
                    requests.exceptions.Timeout,
                    requests.exceptions.RequestException) as err:
                Logger.log(f"Attempt {attempt} failed: {err}", level='error')
                if attempt < max_retries:
                    Logger.log(f"Retrying in {delay_seconds} seconds...\n")
                    time.sleep(delay_seconds)
                else:
                    raise Exception("All retry attempts to fetch partitions failed.")

    def download_and_extract(self):
        """Download zip files, extract JSON, save in target folder."""
        try:
            partitions = self.fetch_partitions()
            downloaded_files = []

            for part in partitions:
                file_url = part["file"]
                filename = os.path.basename(urlparse(file_url).path)
                json_filename = filename.replace(".zip", "")
                save_path = os.path.join(self.target_folder, json_filename)

                if os.path.exists(save_path):
                    Logger.log(f"{json_filename} already exists. Skipping.")
                    downloaded_files.append(save_path)
                    continue

                Logger.log(f"Downloading {filename} ...")
                resp = requests.get(file_url, stream=True)
                resp.raise_for_status()

                zip_buffer = io.BytesIO(resp.content)
                with zipfile.ZipFile(zip_buffer, "r") as z:
                    for info in z.infolist():
                        json_bytes = z.read(info.filename)
                        with open(save_path, "wb") as f:
                            f.write(json_bytes)
                        Logger.log(f"Saved {json_filename} to {self.target_folder}")
                        downloaded_files.append(save_path)

            Logger.log(f"Downloaded and extracted {len(downloaded_files)} JSON files.")
            return downloaded_files

        except Exception as e:
            Logger.log(f"An error occurred during download or extraction: {e}", level='error')
            raise

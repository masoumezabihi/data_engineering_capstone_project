from dataclasses import dataclass

@dataclass
class BlobStorageConfig:
    storage_account: str
    storage_key: str
    container: str
    path_pattern: str = "*.json"

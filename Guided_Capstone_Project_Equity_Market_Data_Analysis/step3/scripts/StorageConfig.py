from dataclasses import dataclass

@dataclass
class StorageConfig:
    account_name: str
    container_name: str
    account_key: str

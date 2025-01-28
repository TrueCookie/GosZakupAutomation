from dataclasses import dataclass

@dataclass
class Config:
    org_type: str
    account_name: str
    account_password: str
    cert_path: str
    cert_password: str
    key_number: str



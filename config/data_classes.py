from dataclasses import dataclass

@dataclass
class Config:
    login_url: str
    windows_credential: str
    signature_name: str
    cert_path: str
    cert_password: str
    account_password: str
    key_number: str
    base_url: str
    org_type: str

@dataclass
class Order:
    number: str
    lots_count: int


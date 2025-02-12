from dataclasses import dataclass

from numpy import float64

@dataclass
class Config:
    org_type: str
    account_name: str
    account_password: str
    cert_path: str
    cert_password: str
    key_number: str
    lots: set
    include_specific: float64
    include_all: float64
    exclude_lots: float64



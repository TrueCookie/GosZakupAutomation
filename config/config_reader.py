import os
import pandas as pd
from config.data_classes import Config

class ConfigReader:
    def __init__(self, config_path: str = "data/Config.xlsx"):
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"Config file not found: {config_path}")
        self.config_df = pd.read_excel(config_path)

    def get_config(self) -> Config:
        # Предполагаем определенную структуру Config.xlsx
        config_row = self.config_df.iloc[0]
        # return Config(
        #     windows_credential=config_row['windows_credential'],
        #     signature_name=config_row['signature_name'],
        #     cert_password=config_row['cert_password'],
        #     base_url=config_row['base_url']
        # )
    
        # TBD: Пока хардкод
        return Config(
            login_url="https://v3bl.goszakup.gov.kz/ru/user/login",
            windows_credential='test_windows_credential',
            signature_name='test_signature_name',
            cert_path="C:\dev\__bite_dev\PROJGosZakupAutomation\cert\GOST512_02213f9c53acb47ee1fc17fa8592e2bd0b98df29.p12",
            cert_password='Aa1234',
            base_url='https://v3bl.goszakup.gov.kz',

            org_type='ТОО' # TBD add desc to config: ТОО/ИП
        )

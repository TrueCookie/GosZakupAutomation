import os
import pandas as pd
from config.data_classes import Config

class ConfigReader:
    def __init__(self, config_path: str = "data/Config.xlsx"):
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"Config file not found: {config_path}")
        self.config_df = pd.read_excel(config_path)

    def get_config(self) -> Config:
        # ИП:
        # return Config(
        #     login_url="https://v3bl.goszakup.gov.kz/ru/user/login",
        #     windows_credential='test_windows_credential',
        #     signature_name='test_signature_name',
        #     cert_path=r"C:\Users\artemiy.ogloblin\Downloads\GOST512_b32b00ee0727c13e6a843c4dec9d653d4a9adf9c (1).p12",
        #     cert_password='Aa123456',
        #     account_password='Aa1234@_',
        #     key_number='13526367-1',
        #     base_url='https://v3bl.goszakup.gov.kz',

        #     org_type='ИП' # TBD add desc to config: ТОО/ИП
        # )
        # Предполагаем определенную структуру Config.xlsx
        #config_row = self.config_df.iloc[0]
        # return Config(
        #     windows_credential=config_row['windows_credential'],
        #     signature_name=config_row['signature_name'],
        #     cert_password=config_row['cert_password'],
        #     base_url=config_row['base_url']
        # )
    
        # TBD: Пока хардкод
        # ТОО:
        return Config(
            login_url="https://v3bl.goszakup.gov.kz/ru/user/login",
            windows_credential='test_windows_credential',
            signature_name='test_signature_name',
            cert_path="C:\dev\__bite_dev\PROJGosZakupAutomation\cert\GOST512_02213f9c53acb47ee1fc17fa8592e2bd0b98df29.p12",
            cert_password='Aa1234',
            account_password='Ernarstroy2013',
            key_number='test_key_number',
            base_url='https://v3bl.goszakup.gov.kz',

            org_type='ТОО' # TBD add desc to config: ТОО/ИП
        )
    


import logging
import os
import pandas as pd
from config.data_classes import Config

class ConfigReader:
    def __init__(self, config_path: str = "data/Config.xlsx"):
        self.logger = logging.getLogger(__name__)
        logging.basicConfig(level=logging.NOTSET)
        
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"Config file not found: {config_path}")
        
        # Читаем лист "Настройка аккаунта"
        self.config_df = pd.read_excel(config_path, sheet_name="Настройка аккаунта")
        #self.config_df = pd.read_excel(config_path)

        # Читаем лист "Режим отладки"
        self.debug_df = pd.read_excel(config_path, sheet_name="Режим отладки")

        # Получаем номер строки для чтения из поля "Настроить номер"
        self.row_number = self.config_df["Настроить номер"].iloc[0]
        self.logger.info(f"CONFIG: Using account number: {self.row_number}")

        # Проверяем режим отладки
        self.debug_mode = self.debug_df["Режим отладки"].iloc[0] == "Да"

        # Получаем список активных шагов если включен режим отладки
        if self.debug_mode:
            self.active_steps = self.debug_df[self.debug_df["Включать?"] == "Да"]["№ п/п"].tolist()
        else:
            self.active_steps = list(range(1, 7))  # все шаги с 1 по 6

    def get_config(self) -> Config:
        # Находим строку по номеру в поле "№ п/п"
        config_row = self.config_df[self.config_df["№ п/п"] == self.row_number].iloc[0]

        # Предполагаем определенную структуру Config.xlsx
        return Config(
            org_type=config_row['Тип организации'],
            account_name=config_row['Имя УЗ'],
            account_password=config_row['Пароль УЗ'],
            cert_path=config_row['Путь до сертификата'],
            cert_password=config_row['Пароль от сертификата'],
            key_number=config_row['Номер заявки для копирования данных']
        )

        # TBD: Пока хардкод
        # ТОО:
        return Config(
            org_type='ТОО',
            account_name="1",
            account_password='Ernarstroy2013',
            cert_path=r"C:\dev\__bite_dev\PROJGosZakupAutomation\cert\GOST512_02213f9c53acb47ee1fc17fa8592e2bd0b98df29.p12",
            cert_password='Aa1234',
            key_number='test_key_number'
        )
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

    def should_execute_step(self, step_number: int) -> bool:
        return step_number in self.active_steps
import logging
import os
import sys
import pandas as pd
from config.data_classes import Config

class ConfigReader:
    def __init__(self, config_path: str = "data/Config.xlsx"):
        self.logger = logging.getLogger(__name__)
        logging.basicConfig(level=logging.NOTSET)
        
        # Ищем конфиг сначала в текущей директории, потом в папке с exe
        if os.path.exists(config_path):
            self.config_path = config_path
        else:
            self.config_path = self.resource_path(config_path)
        
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

    def should_execute_step(self, step_number: int) -> bool:
        return step_number in self.active_steps
    
    def resource_path(relative_path):
        """Получает абсолютный путь к ресурсу"""
        try:
            # PyInstaller создает временную папку и хранит путь в _MEIPASS
            base_path = sys._MEIPASS
        except Exception:
            base_path = os.path.abspath(".")

        return os.path.join(base_path, relative_path)
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
        
        # ----
        # 1. Читаем лист "Настройка аккаунта"
        self.config_df = pd.read_excel(config_path, sheet_name="Настройка аккаунта")
        
        # Получаем номер строки для чтения из поля "Настроить номер"
        self.row_number = self.config_df["Настроить номер"].iloc[0]
        self.logger.info(f"CONFIG: Using account number: {self.row_number}")


        # ----
        # 2. Читаем лист "Настройка лотов"
        self.lots_df = pd.read_excel(config_path, sheet_name="Настройка лотов")
        
        # Получаем значения чекбоксов раздела "Режим выбора"
        self.include_specific = self.lots_df.iloc[0, 3]  # Столбец D, строка 1
        self.include_all = self.lots_df.iloc[1, 3]       # Столбец D, строка 2
        self.exclude_lots = self.lots_df.iloc[2, 3]      # Столбец D, строка 3
        
        # Проверяем, что выбран только один режим
        selected_modes = sum([
            bool(self.include_specific),
            bool(self.include_all),
            bool(self.exclude_lots)
        ])
        
        if selected_modes != 1:
            raise ValueError(
                "Должен быть выбран ровно один режим выбора лотов! "
                "Проверьте настройки в файле конфигурации."
            )

        # Получаем номера лотов
        # TBD: добавить .strip()/Проверить, что astype(int) парсит строки с пробелами
        if self.include_all:
            self.lots = set()
        else:    
            self.lots = set(self.lots_df["Номер лота"].dropna().astype(int).map(lambda x: str(x)).tolist())
        

        # ----
        # 3. Читаем лист "Режим отладки"
        self.debug_df = pd.read_excel(config_path, sheet_name="Режим отладки")

        # Проверяем режим отладки
        self.debug_mode = bool(self.debug_df["Режим отладки"].iloc[0])

        # Получаем список активных шагов если включен режим отладки
        if self.debug_mode:
            self.active_steps = self.debug_df[self.debug_df["Включать?"].astype(bool)]["№ п/п"].tolist() # ^ Если да, замени здесь
        else:
            self.active_steps = list(range(0, 7))  # все шаги с 1 по 6

        # Считываем максимальное время ожидания кнопки "Доступные действия"
        self.actions_button_timeout = float(self.debug_df['Время ожидания кнопки "Доступные действия"'].iloc[0])


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
            key_number=config_row['Номер заявки для копирования данных'],
            lots=self.lots,
            include_specific=self.include_specific,
            include_all=self.include_all,
            exclude_lots=self.exclude_lots,
            actions_button_timeout=self.actions_button_timeout
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
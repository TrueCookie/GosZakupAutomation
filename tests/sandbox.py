from datetime import datetime
import logging
import os
from config.config_reader import ConfigReader
from automation.browser import BrowserAutomation
from automation.actions.auth_actions import AuthActions
from automation.goszakup import GosZakupAutomation

def main():

    # Читаем конфигурацию
    config_reader = ConfigReader()
    config = ConfigReader().get_config()
    
    # Инициализируем браузер
    automation = BrowserAutomation(config)

    # НАЧАЛО
    automation.start(page_url_base='https://v3bl.goszakup.gov.kz/ru/announce/index')
    #automation.start(page_url_base='https://v3bl.goszakup.gov.kz/ru/application/create')
    #automation.start(page_url_base='https://v3bl.goszakup.gov.kz/ru/application/lots')
    #automation.page.set_default_timeout(5000)
    
    screenshots_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Screenshots")
    os.makedirs(screenshots_dir, exist_ok=True)

    # При возникновении любого исключения делаем скриншот
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    screenshot_path = os.path.join(screenshots_dir, f"error_{timestamp}.png")
    if automation.page:
        automation.page.screenshot(path=screenshot_path)
        logging.info(f"Скриншот сохранен в: {screenshot_path}")
        print(f"Скриншот сохранен в: {screenshot_path}")
    else:
        logging.info(f"Неудалось сделать скриншот. Не создано подключение к странице браузера.")    
    print("")

if __name__ == "__main__":
    main()
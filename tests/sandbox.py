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
    #automation.start(page_url_base='https://v3bl.goszakup.gov.kz/ru/announce/index')
    #automation.start(page_url_base='https://v3bl.goszakup.gov.kz/ru/application/create')
    #automation.start(page_url_base='https://v3bl.goszakup.gov.kz/ru/application/lots')
    #automation.page.set_default_timeout(5000)

    lots_count_in_app_text = "98"
    lots_count_in_app = int(lots_count_in_app_text)

    print("")

if __name__ == "__main__":
    main()
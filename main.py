from playwright.sync_api import sync_playwright
from config.config_reader import ConfigReader
from automation.browser import BrowserAutomation
from automation.actions.auth_actions import AuthActions

def main():
    # Читаем конфигурацию
    config = ConfigReader().get_config()
    
    # Инициализируем браузер
    automation = BrowserAutomation(config)
    
    try:
        # TBD: переходим на страницу заказа
        automation.start(is_debug=True, visible=True)
        
        print(f"Opened page: {automation.page.title()}")
        
        # TBD: Если открыта страница авторизации - авторизуйся

        # Шаг 1
        if config.org_type == 'ТОО':
            automation.page.click('//a[contains(text(), \'Заявка на участие в конкурсе для юридических лиц (Приложение 4)\')]')
        elif config.org_type == 'ИП':
            automation.page.click('//a[contains(text(), \'Заявка на участие в конкурсе для физических лиц (Приложение 5)\')]')
    finally:
        automation.close(is_debug=True)

if __name__ == "__main__":
    main()
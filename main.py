from playwright.sync_api import sync_playwright
from config.config_reader import ConfigReader
from automation.browser import BrowserAutomation
from automation.actions.auth_actions import AuthActions
from automation.goszakup import GosZakupAutomation

def main():
    # Читаем конфигурацию
    config = ConfigReader().get_config()
    
    # Инициализируем браузер
    automation = BrowserAutomation(config)
    goszakup_actions = GosZakupAutomation(config)
    
    try:
        # TBD: переходим на страницу заказа
        automation.start(is_debug=True, visible=True)
        
        print(f"Opened page: {automation.page.title()}")
        
        # TBD: Если открыта страница авторизации - авторизуйся

        # Шаг 1
        # if config.org_type == 'ТОО':
        #     automation.page.click('//a[contains(text(), \'Заявка на участие в конкурсе для юридических лиц (Приложение 4)\')]')
        # elif config.org_type == 'ИП':
        #     automation.page.click('//a[contains(text(), \'Заявка на участие в конкурсе для физических лиц (Приложение 5)\')]')

        # goszakup_actions.sign_participation_application(automation.page)
        
        # Шаг 2
        # automation.page.click("//a[contains(text(), 'Перечень приобретаемых товаров(Приложение 2)')]")
        # goszakup_actions.sign_goods_list(automation.page)

        # Шаг 3
        # automation.page.click("//a[contains(text(), 'Техническое задание(Приложение 3)')]")
        # goszakup_actions.sign_technical_spec(automation.page)

        # Шаг 4 TBD: Протестировать
        automation.page.click("//a[contains(text(), 'Сведения о квалификации работников потенциального поставщика (Приложение 6)')]")
        goszakup_actions.copy_qualification_data(automation.page)

        # Шаг 5 TBD: Попросить чатгпт написать
        automation.page.click("//a[contains(text(), 'Обеспечение заявки, либогарантийный денежный взнос')]")
        goszakup_actions.submit_application(automation.page)

    except Exception as e:
        print(f"Error while processing main steps")
    finally:
        automation.close(is_debug=True)

if __name__ == "__main__":
    main()
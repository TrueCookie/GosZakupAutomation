import logging
import sys

from config.config_reader import ConfigReader
from automation.browser import BrowserAutomation
from automation.actions.auth_actions import AuthActions
from automation.goszakup import GosZakupAutomation

def main():
    # Настраиваем логирование
    logging.basicConfig(
        filename='program.log',
        level=logging.DEBUG,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    # Читаем конфигурацию
    config_reader = ConfigReader()
    config = ConfigReader().get_config()
    
    # Инициализируем браузер
    automation = BrowserAutomation(config)
    
    try:
        logging.info("Программа запущена")
        
        start_url = ""
        if config_reader.should_execute_step(0):
            start_url = 'https://v3bl.goszakup.gov.kz/ru/announce/index'
        else: # страница со списком документации (с 1 шага)
            start_url = 'https://v3bl.goszakup.gov.kz/ru/application/docs'
        
        # # TBD: Remove
        # start_url = 'https://v3bl.goszakup.gov.kz/ru/application/lots'
        
        automation.start(page_url_base=start_url)
        goszakup_actions = GosZakupAutomation(config, automation.page)
        
        print(f"Открыта страница: {automation.page.title()}")
        
        # TBD: Если открыта страница авторизации - авторизуйся
        # # Шаг 0 - Начальные действия подачи заявки на участие на странице 'Просмотр объявления'
        if config_reader.should_execute_step(0): # TBD: Сделать более user-frienldy (начинать с 1 или вынести в отдельное поле)
            goszakup_actions.start_submit_application(automation.page)
        
        # Шаг 1
        if config_reader.should_execute_step(1):
            if config.org_type == 'ТОО':
                automation.page.click('//a[contains(text(), \'Заявка на участие в конкурсе для юридических лиц (Приложение 4)\')]')
            elif config.org_type == 'ИП':
                automation.page.click('//a[contains(text(), \'Заявка на участие в конкурсе для физических лиц (Приложение 5)\')]')
            goszakup_actions.sign_participation_application(automation.page)

        # Шаг 2
        if config_reader.should_execute_step(2):
            automation.page.click("//a[contains(text(), 'Перечень приобретаемых товаров(Приложение 2)')]")
            goszakup_actions.sign_goods_list(automation.page)

        # Шаг 3
        if config_reader.should_execute_step(3):
            automation.page.click("//a[contains(text(), 'Техническое задание(Приложение 3)')]")
            goszakup_actions.sign_technical_spec(automation.page)

        # Шаг 4
        if config_reader.should_execute_step(4):
            automation.page.click("//a[contains(text(), 'Сведения о квалификации работников потенциального поставщика (Приложение 6)')]")
            goszakup_actions.copy_qualification_data(automation.page)

        # Шаг 5
        if config_reader.should_execute_step(5):
            automation.page.click("//a[contains(text(), 'Обеспечение заявки, либогарантийный денежный взнос')]")
            goszakup_actions.submit_application(automation.page)

        # Шаг 6
        if config_reader.should_execute_step(6):
            automation.page.click("//button[text()='Далее']")
            goszakup_actions.last_action(automation.page)

        print("\n-- Программа успешно завершена! --")
        input("Нажмите Enter для выхода...")
        sys.exit(1)

    except FileNotFoundError:
        print("\nОшибка: Файл конфигурации не найден. Убедитесь, что файл Config.xlsx находится в папке data/")
        input("Нажмите Enter для выхода...")
        sys.exit(1)

    except Exception as e:
        logging.error(f"Ошибка: {str(e)}")
        print(f"\nПроизошла ошибка: {str(e)}")
        input("Нажмите Enter для выхода...")
        sys.exit(1)

    finally:
        logging.info("Программа завершена")
        automation.close(is_debug=True)

if __name__ == "__main__":
    main()
from config.data_classes import Config
from .base_actions import BaseActions
from automation.actions.certificate_selector import CertificateSelector

class AuthActions(BaseActions):
    def __init__(self, config: Config):
        self.cert_selector = CertificateSelector(config)
        self.config = config

    def full_auth(self, page):
        try:
            self.login(page)

            # self.cert_selector.select_certificate_by_coords()
            self.cert_selector.select_certificate_in_explorer()
            
            self.auth_confirm(page)

        except Exception as e:
            print(f"Error while processing login")

    def login(self, page):
        # Проверяем страницу
        #? page.wait_for_selector('selector_for_password_field', timeout=5000)
        page.wait_for_url("https://v3bl.goszakup.gov.kz/ru/user/login", timeout=5000)

        # Кликаем 'Выберите ключ'
        page.click("//input[@name='selectP12File']")

    def auth_confirm(self, page):
        # Проверяем страницу
        page.wait_for_url("https://v3bl.goszakup.gov.kz/ru/user/auth_confirm", timeout=5000)
        
        # Вводим пароль
        page.fill("//input[@type='password']", self.config.account_password) # TBD: брать из конфига
        print("Password entered")

        # Кликаем чекбокс
        page.click("//input[@type='checkbox' and @id='agreed_check']")
        print("Checkbox checked")

        # Нажимаем Войти
        page.click("//button[contains(text(),'Войти')]")
        print("Login pressed")
        
        



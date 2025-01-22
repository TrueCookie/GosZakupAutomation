from .base_actions import BaseActions


class AuthActions(BaseActions):
    def __init__(self):
        pass
        #self.config = config
    
    def login(self, page):
        # Проверяем страницу
        page.wait_for_url("https://v3bl.goszakup.gov.kz/ru/user/login", timeout=5000)
        
        # Кликаем 'Выберите ключ'
        page.click("//input[@name='selectP12File']")


    def auth_confirm(self, page):
        # Проверяем страницу
        page.wait_for_url("https://v3bl.goszakup.gov.kz/ru/user/auth_confirm", timeout=5000)
        
        # Вводим пароль
        # .fill?
        page.fill("//input[@type='password']", 'Ernarstroy2013') # TBD: брать из конфига
        
        # Кликаем чекбокс
        page.click("//input[@type='checkbox' and @id='agreed_check']")

        # Нажимаем Войти
        page.click("//button[contains(text(),'Войти')]")



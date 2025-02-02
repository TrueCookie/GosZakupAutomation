import logging

from config.data_classes import Config

from automation.browser import BrowserAutomation
from automation.actions.auth_actions import AuthActions
from automation.actions.certificate_selector import CertificateSelector

from playwright.async_api import TimeoutError

class GosZakupAutomation:
    def __init__(self, config: Config):
        self.config = config
        self.playwright = None
        self.browser = None
        self.auth_actions = AuthActions(config)
        self.cert_selector = CertificateSelector(config)        
        self.logger = logging.getLogger(__name__)
        logging.basicConfig(level=logging.NOTSET)
        
    def sign_participation_application(self, page):
        """
        Подписание заявки на участие
        page: объект страницы Playwright
        """
        try:
            self.logger.info("Starting participation application signing")
            
            try:
                # 0. Проверяем, что мы на нужной странице
                if self.config.org_type == 'ТОО':
                    page.wait_for_selector("//h4[text()='Заявка на участие в конкурсе для юридических лиц (Приложение 4)']", timeout=5000)
                elif self.config.org_type == 'ИП':
                    page.wait_for_selector("//h4[text()='Заявка на участие в конкурсе для физических лиц (Приложение 5)']", timeout=5000)
            
            except TimeoutError:
                self.logger.debug("Required page is not found. Check if its login page")
                self.auth_actions.full_auth(page)

            # 1. Нажимаем кнопку "Подписать"
            page.click("//button[.//span[contains(text(),'Подписать')]]")
            self.logger.debug("Clicked sign button")

            # 2. Ждем появления окна выбора сертификата и выбираем сертификат
            if not self.cert_selector.select_certificate_in_explorer():
                raise Exception("Failed to select certificate") # TBD: invoke select_cert_in_explorer method
            self.logger.debug("Certificate selected")
            
            # 3. Возвращаемся к списку документации
            self.return_to_main_page(
                page,
                'Вернуться к списку документации',
                "//div[@class='panel-heading' and .//h4[contains(text(),'Заявка №')]]"
            )

        except Exception as e:
            self.logger.error(f"Error signing participation application: {str(e)}")
            raise

    def sign_goods_list(self, page):
        """
        Подписание перечня товаров
        page: объект страницы Playwright
        """
        try:
            self.logger.info("Starting goods list signing")

            # 1. Ожидаем загрузки страницы
            page.wait_for_selector("//h3[text()='Перечень приобретаемых товаров(Приложение 2)']", timeout=5000)
            self.logger.debug("Goods list section loaded")

            # 4. Нажимаем кнопку "Сохранить подпись"
            self.try_to_sign(
                page,
                "//button[.//span[contains(text(),'Подписать')]]",
                "//input[@type='submit' and @value='Сохранить подпись']",
                "//div[text()='Подпись успешно сохранена']"
            )

            # 6. Возвращаемся к списку документации
            self.return_to_main_page(
                page,
                'Вернутъся к заявке',
                "//div[@class='panel-heading' and .//h4[contains(text(),'Заявка №')]]"
            )

            self.logger.debug("Clicked get back to order")

            #self.return_to_main_page(page)

        except Exception as e:
            self.logger.error(f"Error signing goods list: {str(e)}")
            raise

    def sign_technical_spec(self, page):
        """
        Подписание технического задания
        page: объект страницы Playwright
        lots_count: количество лотов
        """
        try:
            # 1. Ожидаем загрузки страницы
            page.wait_for_selector("//h3[text()='Техническое задание']", timeout=5000)
            self.logger.debug("Technical spec section loaded")

            # Получаем все строки таблицы
            rows = page.locator('table tr')

            # Считаем количество строк (вычитаем 1, т.к. первая строка - заголовок)
            lots_count = rows.count() - 1
            self.logger.info(f"Starting technical specification signing for {lots_count} lots")

            # Для каждого лота
            for lot_number in range(1, lots_count + 1):
                self.logger.debug(f"Processing lot {lot_number}")

                # 1. Нажимаем "Посмотреть" для текущего лота
                # row_number - это номер строки, в которой нужно кликнуть
                # +1 добавляем т.к. первая строка - заголовок
                page.click(f"//table//tr[{lot_number + 1}]//td[last()]//a[contains(text(),'Просмотреть')]", timeout=5000)
                self.logger.debug(f"Clicked view button for lot {lot_number}")
                
                # 1. Ожидаем загрузки страницы
                page.wait_for_selector("//h3[contains(text(),'Подписание технического задания по лоту')]", timeout=5000)
                self.logger.debug("Lot technical spec signing section loaded")

                # 2. Нажимаем "Подписать"
                page.click("//button[.//span[contains(text(),'Подписать')]]")
                self.logger.debug("Clicked sign button")

                # 3. Выбираем сертификат
                if not self.cert_selector.select_certificate_in_explorer():
                    raise Exception(f"Failed to select certificate for lot {lot_number}")
                self.logger.debug("Certificate selected")


                # Если это не последний лот, переходим к следующему
                if lot_number < lots_count:
                    self.return_to_main_page(
                        page,
                        'Вернуться к лотам',
                        "//h3[text()='Техническое задание']"
                    )
                    #page.click("//a[text()='Вернуться к лотам']")
                    self.logger.debug(f"Moving to next lot")
                else:
                    # 4. Возвращаемся в заявку
                    self.return_to_main_page(
                        page,
                        'Вернуться в заявку',
                        "//div[@class='panel-heading' and .//h4[contains(text(),'Заявка №')]]"
                    )
                    #page.click("//a[text()='Вернуться в заявку']", timeout=5000)
                    self.logger.debug("Clicked get back to order")

            self.logger.info("Technical specification signing completed successfully")
            return True

        except Exception as e:
            self.logger.error(f"Error signing technical specification: {str(e)}")
            raise

    def copy_qualification_data(self, page):
        """
        Копирование данных о квалификации из другой заявки
        page: объект страницы Playwright
        """
        try:
            self.logger.info("Starting qualification data copying")

            # 1. Нажимаем кнопку "копировать сведения из других закупок"
            page.click("//a[contains(text(),'Копировать сведения из других закупок')]")
            self.logger.debug("Clicked copy button")

            # 2. Ждем появления поля для ввода номера
            page.wait_for_selector("//input[@name='anno_number']", timeout=5000)
            self.logger.debug("Number input field appeared")

            # 3. Вводим номер заявки
            page.fill("//input[@name='anno_number']", self.config.key_number)
            self.logger.debug("Entered application number")

            # 4. Нажимаем "найти"
            page.click("//input[@value='Найти']")
            self.logger.debug("Clicked search button")

            # 5. Ждем появления результатов поиска
            page.wait_for_selector("//input[@value='Применить']", timeout=10000)
            self.logger.debug("Search results appeared")

            # 6.1 Выбираем найденную заявку
            page.click("//p[starts-with(text(),'Копирование сведения о квалификации из  лота')]/following::table[1]//tr[2]/td[1]//input[@type='radio']")
            self.logger.debug("Selected application")
            
            # 6.2 Выбираем лоты в текущей заявке
            # Получаем все строки таблицы
            rows = page.locator("//p[starts-with(text(),'Копирование сведения о квалификации в лот')]/following::table[1]//tr")

            # Считаем количество строк (вычитаем 1, т.к. первая строка - заголовок)
            lots_count = rows.count() - 1
            self.logger.info(f"Starting technical specification signing for {lots_count} lots")

            # Для каждого лота
            for lot_number in range(1, lots_count + 1):
                self.logger.debug(f"Processing lot {lot_number}")

                # Выбираем лот в текущей заявке
                page.click(f"//p[starts-with(text(),'Копирование сведения о квалификации в лот')]/following::table[1]//tr[{lot_number + 1}]/td[1]//input[@type='checkbox']")
                self.logger.debug("Selected lot")

            # 7. Нажимаем "Применить"
            page.click("//input[@value='Применить']")
            self.logger.debug("Clicked apply button")

            # 8. Возвращаемся к списку документации
            page.click("//a[contains(text(),'Вернутся в заявку')]", timeout=5000)
            self.logger.debug("Clicked get back to order")

            # 9. Ждем завершения копирования
            page.wait_for_selector("//button[contains(text(),'Сформировать приложение')]", timeout=15000)
            self.logger.debug("Copy completed")

            # 9. Выбираем в списке опцию "Нет"
            page.select_option('select[name="bankruptcy"]', label='Нет')
            self.logger.debug("Selected 'No' option")

            # 11. Нажимаем "Сформировать приложение"
            page.click("//button[contains(text(),'Сформировать приложение')]", timeout=5000)
            self.logger.debug("Clicked generate button")

            # 12. Ждем формирования приложения
            page.wait_for_selector("//button[.//span[contains(text(),'Подписать')]]", timeout=20000)
            self.logger.debug("Application generation completed")

            # 13. Нажимаем кнопку "Подписать"
            page.click("//button[.//span[contains(text(),'Подписать')]]")
            self.logger.debug("Clicked sign button")

            # 2. Ждем появления окна выбора сертификата и выбираем сертификат
            self.cert_selector.select_certificate_in_explorer()
            self.logger.debug("Certificate selected")

            # 3. Возвращаемся к списку документации
            self.return_to_main_page(
                page,
                ' Вернуться в список документов ',
                "//div[@class='panel-heading' and .//h4[contains(text(),'Заявка №')]]"
            )


            self.logger.info("Qualification data copying completed successfully")
            return True

        except Exception as e:
            self.logger.error(f"Error copying qualification data: {str(e)}")
            self._handle_error(page)
            raise

    def submit_application(self, page):
        """
        Подача заявки
        page: объект страницы Playwright
        lots_count: количество лотов
        """
        try:
            self.logger.info("Starting application submission")

            # Получаем все строки таблицы
            rows = page.locator("//div[text()='Добавление обеспечение заявки']/following-sibling::div//table//tr")

            # Считаем количество строк (вычитаем 1, т.к. первая строка - заголовок)
            lots_count = rows.count() - 1
            self.logger.info(f"Starting to add {lots_count} lots")

            # Для каждого лота
            for lot_number in range(1, lots_count + 1):
                self.logger.debug(f"Processing lot {lot_number}")

                # Выбираем лот в текущей заявке
                page.click(f"//div[text()='Добавление обеспечение заявки']/following-sibling::div//table//tr[{lot_number + 1}]//a[contains(text(),'Добавить')]")
                self.logger.debug("Added lot")

                # Выбираем в списке опцию 'Деньги, с электронного кошелька'
                page.select_option("select[name='typeDoc']", label='Деньги, с электронного кошелька')
                self.logger.debug("Selected option 'Деньги, с электронного кошелька'")

                # Ждем появления кнопки "Сохранить"
                page.wait_for_selector("//input[@value='Сохранить']", timeout=10000)
                self.logger.debug("Save button appeared")

                # Нажимаем кнопку "Сохранить"
                page.click("//input[@value='Сохранить']")
                self.logger.debug("Clicked save button")

                # Ждем появления кнопки "Назад"
                page.wait_for_selector("//a[contains(text(),'Назад')]", timeout=10000)
                self.logger.debug("Back button appeared")

                # Возвращаемся к списку лотов
                self.return_to_main_page(
                    page,
                    'Назад',
                    "//a[contains(text(),'Вернуться в заявку')]"
                )

            # Возвращаемся к списку документации
            self.return_to_main_page(
                page,
                'Вернуться в заявку',
                "//div[@class='panel-heading' and .//h4[contains(text(),'Заявка №')]]"
            )

            return True

        except Exception as e:
            self.logger.error(f"Error submitting application: {str(e)}")
            self._handle_submission_error(page)
            raise

    def last_action(self, page):
        """
        Последнее действие
        page: объект страницы Playwright
        lots_count: количество лотов
        """
        try:
            self.logger.info("Starting application submission")

            page.wait_for_selector("//button[text()='Подписать заявку']", timeout=10000)
            page.click(f"//button[text()='Подписать заявку']")
            self.logger.debug("Added lot")
            
            page.wait_for_selector("//div[contains(text(),'Ваша заявка успешно подписана')]", timeout=10000)
            page.click(f"//button[text()='Далее']")
            self.logger.debug("Added lot")

            page.wait_for_selector("//button[text()='Подать заявку']", timeout=10000)
            page.click(f"//button[text()='Подать заявку']")
            self.logger.debug("Added lot")

            return True

        except Exception as e:
            self.logger.error(f"Error submitting application: {str(e)}")
            self._handle_submission_error(page)
            raise



    def verify_main_page_return(self, page, ver_main_page_selector):
        """Проверка успешности возвращения на страницу со списком документации"""
        success = page.wait_for_selector(
            ver_main_page_selector, 
            timeout=10000,
            state='visible'
        )

        if success:
            self.logger.info("Return is successfully")
            return True
        else:
            raise False # Exception("Success indicator not found after signing")
        
    def return_to_main_page(self, page, return_butt_text, ver_main_page_selector, try_max=3):
        # Действия для возвращения на страницу со списком документации
        is_on_main_page = False
        try_count = 0
        while is_on_main_page != True and try_count < try_max:
            # 3. Нажимаем "Вернуться к списку документации"
            page.wait_for_selector(f"//a[text()='{return_butt_text}']", timeout=10000, state='visible')
            page.wait_for_timeout(2000)
            page.click(f"//a[text()='{return_butt_text}']")
            self.logger.debug("Clicked 'Back to doc list' button")

            # 4. Ждем возвращения на страницу со списком документации
            is_on_main_page = self.verify_main_page_return(page, ver_main_page_selector)
            try_count = try_count + 1
            if is_on_main_page == False:
                self.logger.debug(f"Failded to return on main page. Try counter: {try_count}/{try_max}")

        if is_on_main_page == False:
            raise Exception("Exceed tries to return on main page")
        
        # Подтверждаем возвращение на страницу со списком документации
        self.logger.debug(f"Returning on main page succeed. Try counter: {try_count}/{try_max}")

    def try_to_sign(self, page, sign_button_selector, save_sign_button, ver_element_selector, try_max=3):
        # Действия для возвращения на страницу со списком документации
        is_on_main_page = False
        try_count = 0
        while is_on_main_page != True and try_count < try_max:
            # Нажимаем "Подписать"
            page.wait_for_selector(sign_button_selector, timeout=10000, state='visible')
            page.wait_for_timeout(2000)
            page.click(sign_button_selector)
            self.logger.debug("Clicked sign button")

            # Ждем появления окна выбора сертификата и выбираем сертификат
            if not self.cert_selector.select_certificate_in_explorer():
                raise Exception("Failed to select certificate")
            self.logger.debug("Certificate selected")

            page.wait_for_selector(save_sign_button, timeout=5000)
            page.click(save_sign_button, timeout=5000)
            self.logger.debug("Clicked save sign")

            # 4. Ждем возвращения на страницу со списком документации
            is_on_main_page = self.verify_main_page_return(page, ver_element_selector)
            try_count = try_count + 1
            if is_on_main_page == False:
                self.logger.debug(f"Failded to sign. Try counter: {try_count}/{try_max}")

        if is_on_main_page == False:
            raise Exception("Exceed tries to sign")
        
        # Подтверждаем возвращение на страницу со списком документации
        self.logger.debug(f"Signing succeed. Try counter: {try_count}/{try_max}")
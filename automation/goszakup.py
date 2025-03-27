import logging
import time
from config.data_classes import Config

from automation.browser import BrowserAutomation
from automation.actions.auth_actions import AuthActions
from automation.actions.base_actions import BaseActions
from automation.actions.certificate_selector import CertificateSelector
from automation.actions.lots_selector import LotSelector

from playwright.sync_api import Page
from playwright.async_api import TimeoutError

class GosZakupAutomation:
    def __init__(self, config: Config, page):
        self.config = config
        self.page = page
        self.auth_actions = AuthActions(config)
        self.actions = BaseActions(page)
        self.cert_selector = CertificateSelector(config)        
        self.logger = logging.getLogger(__name__)
        logging.basicConfig(level=logging.NOTSET)

    def start_submit_application(self, page: Page):
        """
        Начальные действия подачи заявки на участие на странице 'Просмотр объявления'
        page: объект страницы Playwright
        """
        try:
            self.logger.info("Starting submitting application")
            
            page.set_default_timeout(3000)
            
            lots_count_in_app = None

            # 1.1 Подтверждаем переход на нужную страницу
            try:
                page.wait_for_selector("//h4[contains(text(),'Просмотр объявления')]", timeout=5000)            
            except TimeoutError:
                self.logger.debug("Required page is not found. Check if its login page")
                self.auth_actions.full_auth(page)
            
            # 1.2 Ожидаем появления кнопки "Доступные действия"
            if not self.wait_for_actions_button(page, timeout_minutes=self.config.actions_button_timeout):
                raise Exception(
                    f"""Превышено кол-во времени для ожидания кнопки 'Доступные действия' 
                    (Максимальное ожидание: {self.config.actions_button_timeout} минут)"""
                )
                                          
            # Проверяем, что открыта вкладка "Общие сведения". Если нет - открываем
            self.check_opened_tab(page, target_tab_text='Общие сведения', check_tab_timeout=1000)

            # Запоминаем кол-во лотов в заявке
            lots_count_in_app_text = page.text_content("//table//tr[.//th[text()='Кол-во лотов в объявлении']]//td")
            lots_count_in_app = int(lots_count_in_app_text)

            # 1.3 Нажимаем кнопку "Доступные действия"
            page.click("//button[text()='Доступные действия ']")
            self.logger.debug("Clicked 'Available actions' button")

            # 1.4 Выбираем "Создать заявку"
            page.click("//ul[@class='dropdown-menu']//a[text()='Создать заявку']")
            self.logger.debug("Selected 'Create application'")

            # TBD: Если мы на этой странице - выполнять действия ниже. Если нет - залогировать, но пропустить
            # 2.1 Подтверждаем переход на нужную страницу
            try:
                page.wait_for_selector("//h4[contains(text(),'Создание заявки')]", timeout=5000)            
            except TimeoutError:
                self.logger.debug("Required page is not found")
                raise
                        
            # 2.2 Выбираем первый адрес в поле "Юридический адрес"
            page.select_option("//select[@name='subject_address']", index=1)
            self.logger.debug("Selected first option in list 'Subject address'")

            # 2.3 Выбираем первый адрес в поле "ИИК"
            page.select_option("//select[@name='iik']", index=1)
            self.logger.debug("Selected first option in list 'IIK'")
            
            # 2.4 Вводим случайный номер в поле "Контактный телефон"
            page.fill("//input[@name='contact_phone']", "89001234567")
            self.logger.debug("Entered random number")

            # 2.5 Нажимаем кнопку "Далее"
            page.click("//button[text()='Далее']")
            self.logger.debug("Clicked 'Next' button")

            # 3.1 Подтверждаем переход на нужную страницу
            try:
                page.wait_for_selector("//h4[contains(text(),'Добавление лотов для участия в закупке')]", timeout=60000)            
            except TimeoutError:
                self.logger.debug("Required page is not found")
                raise
            
            # 3.2 Выбираем нужные лоты
            lots_selector = LotSelector(self.config)
            self.select_lots(page, lots_selector, lots_count_in_app)

            # 4. Нажимаем кнопку "Далее"
            page.click("//button[text()='Далее']", timeout=5000)
            self.logger.debug("Clicked 'Next' button")

            # 5. Подтверждаем переход страницу со списком документации
            try:
                page.wait_for_selector(
                    "//div[@class='panel-heading' and .//h4[contains(text(),'Заявка №')]]",
                    timeout=5000
                )            
            except TimeoutError:
                self.logger.debug("Page with Document list is not found")
                raise

        except Exception as e:
            self.logger.error(f"Error adding lots to application: {str(e)}")
            raise


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
            page.select_option('//select[@name="bankruptcy"]', label='Нет') # TBD: Проверить, что здесь name, а не @name
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
                page.select_option("//select[@name='typeDoc']", label='Деньги, с электронного кошелька') # TBD: Проверить, что здесь name, а не @name
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

    # Функции утилит

    def wait_for_button(self, page, selector, timeout=60*40, refresh_interval=10):
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            button = page.query_selector(selector)
            if button:
                return True
                
            page.reload()
            time.sleep(refresh_interval) # TBD: Оптимизируй здесь
        
        return False

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

    def should_select_lot(self, lot_number: str) -> bool:
        """
        Определяет, нужно ли выбрать конкретный лот
        """
        if self.config.include_all:
            return True
        elif self.config.exclude_lots:
            return lot_number not in self.config.lots
        else:  # include_specific
            return lot_number in self.config.lots
        
    def select_lots(self, page: Page, lot_selector: LotSelector, declaration_lots_count: int):
        """
        Выбирает лоты на всех страницах согласно настройкам
        """
        logging.info(f"Режим выбора лотов: {lot_selector.get_selection_mode()}")
        
        total_processed = set()
        current_page = 1
        
        while True:
            # Подсчитываем лоты на текущей странице
            selected_on_page = 0
            
            # Ждем стабилизации DOM
            page.wait_for_load_state("domcontentloaded")

            # Ждем появления таблицы
            try:
                page.wait_for_selector("//div[contains(@class, 'active')]//table//tbody//tr", 
                                state="visible", 
                                timeout=1000) # TBD: Оптимизация, поставить меньшее время: 1000
            except Exception as e:
                # Если на предыдущем шаге мы выбрали все лоты, на странице их не окажется
                logging.error(f"На странице не представлено лотов для выбора. Переходим к оформлению заявки")
                break
            
            # Используем локатор для надежного доступа к элементам
            table_rows = page.locator("//div[contains(@class, 'active')]//table//tbody//tr")
            
            # TBD: Оптимизация: скрипт 1 лишний раз проходит по всем лотам на странице - изменить алгоритм обработки
            # Обрабатываем лоты на текущей странице
            for i in range(table_rows.count()):
                try:
                    row = table_rows.nth(i)
                    cell = row.locator("td").nth(1)
                    
                    # Ждем появления текста в ячейке
                    cell.wait_for(state="visible")
                    
                    lot_number_with_letters = cell.text_content()
                    number_separator_index = lot_number_with_letters.find('-')
                    lot_number = lot_number_with_letters[:number_separator_index]
                    
                    checkbox = row.locator("input[type='checkbox']")
                    if lot_selector.should_select_lot(lot_number):
                        checkbox.check()
                        selected_on_page += 1
                        lot_selector.mark_lot_processed(lot_number)

                    total_processed.add(lot_number)
            
                except Exception as e:
                    logging.error(f"Ошибка при обработке строки {i}: {str(e)}")
                    continue
            ### КОНЕЦ ЦИКЛА ПО СТРОКАМ
            
            # Ждем стабилизации DOM
            page.wait_for_load_state("domcontentloaded")

            # Нажимаем "Добавить выбранные"
            try:
                page.wait_for_selector("//button[text()='Добавить выбранные']", timeout=5000)
                add_button = page.query_selector("//button[text()='Добавить выбранные']")
                if add_button:
                    add_button.click(timeout=1000)
                    logging.info("Нажата кнопка 'Добавить выбранные'")
                else:
                    raise ValueError("Кнопка 'Добавить выбранные' не найдена")
            except Exception as e:
                is_last_page = (len(total_processed) >= declaration_lots_count)
                
                if not lot_selector.has_remaining_lots() or is_last_page:
                    break
                else:
                    raise

            # Проверяем был ли переход на вкладку Просмотра выбранных лотов
            #self.check_opened_tab(page, target_tab_text='Лоты', check_tab_timeout=2000)
            # Проверяем был ли переход на вкладку Просмотра выбранных лотов
            lots_viewer_tab_active = None
            try:
                # TBD: Оптимизация: возможно для подтверждения не-перехода на страницу просмотра 
                # выбранных лотов нужно меньше времени
                # NOTE: Селектор работает неправильно, но алгоритм отрабатывает
                lots_viewer_tab_active = page.wait_for_selector(
                        "//li[//a[text()='Просмотр выбранных '] and @class='active']",
                        timeout=10000
                    )
            except TimeoutError:
                self.logger.debug("Tab with Lots viewer is not found")
            
            # Если перешли на вторую вкладку - возвращаемся на первую
            if(lots_viewer_tab_active != None):
                # Переходим обратно на вкладку Выбора лотов
                # Нажимаем вкладку "Лоты"
                page.click("//li/a[text()='Лоты']")

                # Подтверждаем переход на вкладку Выбора лотов
                try:
                    page.wait_for_selector("//li[//a[text()='Лоты'] and @class='active']", timeout=5000)            
                except TimeoutError:
                    self.logger.debug("Tab with Lots selecting is not found")
                    raise

            
            # Подводим итоги итерации
            logging.info(f"Страница {current_page}: выбрано {selected_on_page} лотов")

            if selected_on_page == 0:
                # Проверяем, нужно ли продолжать поиск
                is_last_page = (len(total_processed) >= declaration_lots_count)
                
                if not lot_selector.has_remaining_lots() or is_last_page:
                    break

                # Переход на следующую страницу
                next_button = page.query_selector("//a[text()='>']")
                if not next_button:
                    logging.info("Кнопка перехода на следующую страницу не найдена")
                    break
                
                logging.info("Кнопка перехода на следующую страницу найдена")
                next_button.click(timeout=30000)
                logging.info("Кнопка перехода на следующую страницу нажата")
                current_page += 1
                # Ждем загрузки следующей страницы
                page.wait_for_load_state("networkidle") # NOTE: Тут могут быть проблемы. Неизвестный функционал
            elif selected_on_page > 0:
                # Ждем загрузки следующей страницы
                page.wait_for_load_state("networkidle") # NOTE: Тут могут быть проблемы. Неизвестный функционал
                continue
        
        # Проверяем результаты
        if lot_selector.remaining_lots and not lot_selector.config.include_all:
            missing_lots = sorted(lot_selector.remaining_lots)
            # TBD: Отредактировать сообщение, в зависимости от режима. 
            # Если режим "Исключить", сообщение "не выбраны лоты:"
            warning_msg = f"Один или несколько лотов не удалось найти в заявке: {', '.join(missing_lots)}"
            logging.warning(warning_msg)
            print(warning_msg)

    def wait_for_actions_button(self, page, timeout_minutes: int = 5) -> bool:
        start_time = time.time()
        end_time = start_time + (timeout_minutes * 60)
        reload_count = 0
        
        while time.time() < end_time:
            try:
                reload_count += 1
                remaining_minutes = int((end_time - time.time()) / 60)
                
                self.logger.info(
                    f"Попытка {reload_count}. "
                    f"Осталось примерно {remaining_minutes} минут"
                )
                
                # Ждем загрузки страницы
                page.wait_for_load_state("networkidle")
                
                # Быстрая проверка наличия кнопки
                if page.query_selector("//button[text()='Доступные действия ']"):
                    self.logger.info("Кнопка 'Доступные действия' найдена")
                    self.logger.debug(f"Время ожидания: {time.time() - start_time}. Перезагрузок страницы: {reload_count}.")
                    return True
                    
                # Если кнопки нет - сразу перезагружаем
                self.logger.info("Кнопка не найдена, перезагрузка страницы...")
                page.reload()
                
                # Минимальная пауза для избежания излишней нагрузки
                time.sleep(2)
                
            except Exception as e:
                self.logger.error(f"Ошибка при проверке кнопки: {str(e)}")
                if time.time() < end_time:
                    time.sleep(2)
                    continue
                break
        
        self.logger.warning(
            f"Кнопка не появилась после {timeout_minutes} минут ожидания "
            f"и {reload_count} попыток"
        )
        return False
    
    def check_opened_tab(self, page: Page, target_tab_text: str, check_tab_timeout):
        # Ждем стабилизации DOM
        page.wait_for_load_state("domcontentloaded")

        # Проверяем активна ли нужная вкладка
        target_tab_active = None
        try:
            target_tab_active = page.wait_for_selector(f"//li[./a[text()='{target_tab_text}'] and @class='active']", timeout=200)
            self.logger.info(f"Tab {target_tab_text} is active.")
        except TimeoutError:
            self.logger.info(f"Tab {target_tab_text} is not active. Open tab.")
        
        # Если нужная вкладка не активна, переходим на неё
        if(target_tab_active == None):
            # Нажимаем вкладку "Лоты"
            page.click(f"//li/a[text()='{target_tab_text}']")

            # Подтверждаем переход на вкладку Выбора лотов
            try:
                page.wait_for_selector(f"//li[./a[text()='{target_tab_text}'] and @class='active']", timeout=5000)            
            except TimeoutError:
                self.logger.error(f"Не удалось открыть вкладку {target_tab_text} для получения кол-ва лотов в заявке.")
                raise
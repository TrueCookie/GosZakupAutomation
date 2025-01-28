from playwright.sync_api import sync_playwright
from config.data_classes import Config

class BrowserAutomation:
    def __init__(self, config: Config):
        self.config = config
        self.playwright = None
        self.browser = None
        self.page = None

    def start(self, visible, is_debug: bool = False):
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.connect_over_cdp("http://localhost:9222")
        
        # Получить все открытые страницы
        pages = self.browser.contexts[0].pages
        #self.page = self.browser.contexts[0].pages[0]
        
        # Найти нужную страницу по URL
        target_page = next(
            (page for page in pages 
            if page.url.startswith('https://v3bl.goszakup.gov.kz/ru/application/docs/')), 
            None
        )
        self.page = target_page

    def close(self, is_debug: bool = False):
        if is_debug:
            pass
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()
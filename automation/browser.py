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
        if not is_debug:
            self.browser = self.playwright.chromium.launch(headless=not visible)
            self.page = self.browser.new_page()
        else:
            self.browser = self.playwright.chromium.connect_over_cdp("http://localhost:9222")
            self.page = self.browser.contexts[0].pages[0]
        return self

    def close(self, is_debug: bool = False):
        if is_debug:
            pass
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()
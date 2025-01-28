from config.config_reader import ConfigReader
from automation.browser import BrowserAutomation
from automation.actions.auth_actions import AuthActions
from automation.actions.certificate_selector import CertificateSelector

def test():
    config = ConfigReader().get_config()

    print("fff")

if __name__ == "__main__":
    test()
from config.config_reader import ConfigReader
from automation.browser import BrowserAutomation
from automation.actions.auth_actions import AuthActions
from automation.actions.certificate_selector import CertificateSelector
from automation.goszakup import GosZakupAutomation

def test():
    config = ConfigReader().get_config()
    automation = BrowserAutomation(config)

    automation.start(is_debug=True, visible=True)
    goszakup_actions = GosZakupAutomation(config)

if __name__ == "__main__":
    test()
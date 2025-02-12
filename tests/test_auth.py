from config.config_reader import ConfigReader
from automation.browser import BrowserAutomation
from automation.actions.auth_actions import AuthActions
from automation.actions.certificate_selector import CertificateSelector

def test():
    config = ConfigReader().get_config()
    automation = BrowserAutomation(config)

    try:
        automation.start(page_url_base='https://v3bl.goszakup.gov.kz/ru/user/login')

        auth_actions = AuthActions(config)
        auth_actions.full_auth(automation.page)        

    except Exception as e:
        print(f"Error while processing login")
    finally:
        automation.close(is_debug=True)

if __name__ == "__main__":
    test()
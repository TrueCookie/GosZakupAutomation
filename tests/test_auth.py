from config.config_reader import ConfigReader
from automation.browser import BrowserAutomation
from automation.actions.auth_actions import AuthActions
from automation.actions.certificate_selector import CertificateSelector

def test():
    config = ConfigReader().get_config()
    automation = BrowserAutomation(config)
    cert_selector = CertificateSelector(config)

    try:
        automation.start(is_debug=True, visible=True)
        
        auth_actions = AuthActions(config)
        
        #auth_actions.login(automation.page)
        cert_selector.select_certificate_in_explorer()
        
        #auth_actions.auth_confirm(automation.page)

        

    except Exception as e:
        print(f"Error while processing login")
    finally:
        automation.close(is_debug=True)

if __name__ == "__main__":
    test()
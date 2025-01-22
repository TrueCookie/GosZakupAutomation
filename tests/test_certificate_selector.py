from automation.actions.certificate_selector import CertificateSelector
import pyautogui

def test():
    cert_selector = CertificateSelector()

    # Выбираем сертификат через pywinauto
    if not cert_selector.select_certificate_by_coords():
        raise Exception("Failed to select certificate")


if __name__ == "__main__":
    test()
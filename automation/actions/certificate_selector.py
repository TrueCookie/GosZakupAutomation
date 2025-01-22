import time
from pywinauto.application import Application
import pyautogui
import keyboard
import win32gui
import win32con

class CertificateSelector:
    def __init__(self):
        self.app = None
 
    def select_certificate(self):
        try:
            # Подключаемся к окну выбора сертификата
            self.app = Application().connect(title="Creating CSP")
            
            # Получаем окно
            dialog = self.app.window(title="Creating CSP")
            
            # Ждем появления окна
            dialog.wait('visible', timeout=10)

            # Печатаем всю информацию о контролах
            dialog.print_control_identifiers()

            # Получаем все элементы окна
            elements = dialog.children()

            # Ищем элемент с желтым фоном
            for element in elements:
                try:
                    if "yellow" in element.get_properties()['background_color']:
                        element.click()
                        return True
                except:
                    continue

            return False

        except Exception as e:
            print(f"Error selecting certificate: {str(e)}")
            return False

    # Альтернативный вариант с поиском по координатам
    def select_certificate_by_coords(self):
        try:
            # Подключаемся к окну по заголовку
            app = Application().connect(title="Creating CSP", visible_only=True, timeout=10)
            dialog = app.top_window()
            
            # Ждем появления окна
            dialog.wait('visible', timeout=10)

            # Получаем handle окна
            hwnd = dialog.handle
        
            # Перемещаем окно в позицию (0,0)
            win32gui.SetWindowPos(hwnd, win32con.HWND_TOP, 0, 0, 0, 0, 
                            win32con.SWP_NOSIZE)  # SWP_NOSIZE сохраняет текущий размер окна

            # Ждем перемещения
            time.sleep(0.5)

            # Получаем координаты окна
            rect = dialog.rectangle()
            
            # Кликаем по желтой области (подберите координаты)
            # X: отступ слева + половина ширины
            # Y: отступ сверху + высота строки
            x = rect.left + 150  # подберите значение
            y = rect.top + 50    # подберите значение            

            dialog.click_input(coords=(x, y))
            
            # Получаем текущие координаты мыши и цвет пикселя
            pixel_color = pyautogui.screenshot().getpixel((x, y))            
            print(f"\rPosition: ({x}, {y}) RGB: {pixel_color}", end='')

            self.enter_password()

            return True
            
        except Exception as e:
            print(f"Error selecting certificate: {str(e)}")
            return False

    def enter_password(self):
        try:
            keyboard.write("Aa1234") # TBD: брать из конфига
            keyboard.press_and_release('enter')
                        
        except Exception as e:
            print(f"Error entering password: {str(e)}")
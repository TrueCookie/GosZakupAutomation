import time
from pywinauto.application import Application
import pywinauto.timings
import pyautogui
import keyboard
import win32gui
import win32con

from config.data_classes import Config

class CertificateSelector:
    def __init__(self, config: Config):
        self.app = None
        self.config = config
    
    # Вариант с поиском по координатам
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
            x = rect.left + 150
            y = rect.top + 50        

            dialog.click_input(coords=(x, y))
            
            # Получаем текущие координаты мыши и цвет пикселя
            pixel_color = pyautogui.screenshot().getpixel((x, y))            
            print(f"\rPosition: ({x}, {y}) RGB: {pixel_color}", end='')

            self.enter_password()

            return True
            
        except Exception as e:
            print(f"Error selecting certificate by coords: {str(e)}")
            return False

    def enter_password(self):
        try:
            keyboard.write(self.config.cert_password)
            keyboard.press_and_release('enter')
                        
        except Exception as e:
            print(f"Error entering password: {str(e)}")

    def enter_cert_path(self):
        try:
            keyboard.write(self.config.cert_path)
            keyboard.press_and_release('enter')
                        
        except Exception as e:
            print(f"Error entering path: {str(e)}")

    def select_certificate_in_explorer(self):
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
            
            # Кликаем по кнопке "File system"
            x = rect.left + 150
            y = rect.bottom - 20          

            dialog.click_input(coords=(x, y))

            # Получаем текущие координаты мыши и цвет пикселя
            pixel_color = pyautogui.screenshot().getpixel((x, y))            
            print(f"\rPosition: ({x}, {y}) RGB: {pixel_color}", end='')
 
        except Exception as e: #TimeoutError
            print(f"WARN: 'Creating CSP' window is not found. Next step is find window with title 'Select certificate'. Error desc: {str(e)}")
            pass

        try:    
            pywinauto.timings.wait_until_passes(
                timeout=30,
                retry_interval=1,
                func=lambda: Application().connect(title='Select certificate').window()
            )
            self.enter_cert_path()

            pywinauto.timings.wait_until_passes(
                timeout=30,
                retry_interval=1,
                func=lambda: Application().connect(title='Enter password:').window()
            )
            self.enter_password()

            return True
            
        except Exception as e:
            print(f"Error selecting certificate in explorer: {str(e)}")
            return False

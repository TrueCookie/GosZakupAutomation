import pyautogui
import time
import keyboard

def get_mouse_position():
    print("Press 'q' to quit...")
    try:
        while True:
            # Получаем текущие координаты мыши
            x, y = pyautogui.position()
            # Получаем цвет пикселя
            pixel_color = pyautogui.screenshot().getpixel((x, y))
            
            print(f"\rPosition: ({x}, {y}) RGB: {pixel_color}", end='')
            
            # Выход по нажатию 'q'
            if keyboard.is_pressed('q'):
                break
            
            time.sleep(0.1)
            
    except KeyboardInterrupt:
        print("\nDone.")

if __name__ == "__main__":
    # Даем время на переключение окна
    print("Starting in 3 seconds...")
    time.sleep(3)
    get_mouse_position()
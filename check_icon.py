# Проверьте иконку с помощью Python
from PIL import Image

def test():
    try:
        img = Image.open(r"C:\Users\artemiy.ogloblin\Downloads\Saki-NuoveXT-Actions-player-play.ico")
        print("Icon is valid")
    except Exception as e:
        print(f"Icon error: {e}")



if __name__ == "__main__":
    test()
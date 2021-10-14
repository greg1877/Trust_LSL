import mouse
from datetime import datetime
import pygame

# Query Mouse Position from Windows
def query_mouse_position():
    mPos = pyautogui.position()
    mButton = pygame.mouse.get_pressed()
    return [mPos.x, mPos.y, int(mButton[0]), int(mButton[1]), int(mButton[2])]

try:
 while True:
     a = mouse.is_pressed(button="left")
     b = mouse.is_pressed(button="right")
     c,d = mouse.get_position()
     print(str(a) + str(b) + str(c) + str(d))
except KeyboardInterrupt:
    pass
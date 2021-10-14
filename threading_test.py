

import logging
import threading
import time
from datetime import datetime
import os

path = "C:/Users/GB_SurfaceBook/LSL_Executables/Standard Input"
os.chdir(path)

def thread_function1():
    os.system("keyboard.exe")

def thread_function2():
    os.system("mouse.exe")

x1 = threading.Thread(target=thread_function1)
x2 = threading.Thread(target=thread_function2)
x1.start()
x2.start()

os.system("Stop-Process -Name 'keyboard'")
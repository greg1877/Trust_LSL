import mouse
from datetime import datetime



try:
 while True:
     a=mouse.is_pressed(button="left")
     if a:
         now = datetime.now()
         current_time = now.strftime("%H:%M:%S:%MS")
         print("current time = ", current_time)
except KeyboardInterrupt:
    pass
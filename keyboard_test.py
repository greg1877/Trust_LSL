import keyboard
import time

def on_space():
    print('space was pressed')

# try:
#     while True:
#         print("line \n")
#         keyboard.add_hotkey('space', on_space)
#         time.sleep(.1)
# except KeyboardInterrupt:
#     pass

import logging

logging.basicConfig(filename='example.log', encoding='utf-8', level=logging.DEBUG)
logging.debug('This message should go to the log file')
logging.info('So should this')
logging.warning('And this, too')
logging.error('And non-ASCII stuff, too, like Øresund and Malmö')
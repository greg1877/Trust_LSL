

import logging
import threading
import time
from datetime import datetime

now = datetime.now()
current_time = now.strftime("%H:%M:%S")
print("current time = ", current_time)

log_file_name = "BIOPAC_LSL_" + datetime.now().strftime("%H:%M:%S:%MS") + ".log"
FORMAT = '%(asctime)s %(message)s'
logging.basicConfig(format='%(asctime)s %(message)s',
    level=logging.INFO,
    filename='logs.txt')

logger = logging.getLogger()
logger.debug('This message should go to the log file')
logger.info('So should this')
logger.warning('And this, too')

def thread_function(name):
    logger.info("Thread %s: starting", name)
    time.sleep(2)
    logger.info("Thread %s: finishing", name)


if __name__ == "__main__":
    format = "%(asctime)s: %(message)s"
 #   logger.basicConfig(format=format, level=logging.INFO,
 #                       datefmt="%H:%M:%S")

    logger.info("Main    : before creating thread")
    x = threading.Thread(target=thread_function, args=(1,))
    logger.info("Main    : before running thread")
    x.start()
    logger.info("Main    : wait for the thread to finish")
    # x.join()
    logger.info("Main    : all done")
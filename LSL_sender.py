import time
import numpy as np
from random import random as rand
from pylsl import StreamInfo, StreamOutlet

# First Stream
info1 = StreamInfo('Pseudo Noise', 'EEG', 20, 100, 'float32', 'myuid123')
outlet1 = StreamOutlet(info1)

# Second Stream
info2 = StreamInfo('Local_Minute', 'Minute', 1, 100, 'float32', 'myuid456')
outlet2 = StreamOutlet(info2)

# Third Stream
info3 = StreamInfo('Local_Second', 'Second', 1, 100, 'float32', 'myuid789')
outlet3 = StreamOutlet(info3)

print("now sending data...")
try:
    while True:
        mysample1 = [rand(), rand(), rand(), rand(), rand(), rand(), rand(), rand(), rand(), rand(),
                    rand(), rand(), rand(), rand(), rand(), rand(), rand(), rand(), rand(), rand()]
        # Change the other "mysampleX" lists as desired
        mysample2 = [time.localtime().tm_min]
        mysample3 = [time.localtime().tm_sec]

        outlet1.push_sample(mysample1)
        outlet2.push_sample(mysample2)
        outlet3.push_sample(mysample3)
        time.sleep(0.01)
except KeyboardInterrupt:
    pass
print("LSL streams Stopped")
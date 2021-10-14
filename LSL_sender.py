import time
from random import random as rand
from pylsl import StreamInfo, StreamOutlet

info1 = StreamInfo('BioSemi_1', 'EEG', 20, 100, 'float32', 'myuid67890')
#info2 = StreamInfo('BioSemi_2', 'EEG', 20, 100, 'float32', 'myuidddd')
#info3 = StreamInfo('BioSemi_3', 'Biophys', 20, 100, 'float32', 'myuidddd')
outlet1 = StreamOutlet(info1)
#outlet2 = StreamOutlet(info2)
#outlet3 = StreamOutlet(info3)

print("now sending data...")
try:
    while True:
        mysample = [rand(), rand(), rand(), rand(), rand(), rand(), rand(), rand(), rand(), rand(),
                    rand(), rand(), rand(), rand(), rand(), rand(), rand(), rand(), rand(), rand()]
        outlet1.push_sample(mysample)
        #outlet2.push_sample(mysample)
        #outlet3.push_sample(mysample)
        time.sleep(0.01)
except KeyboardInterrupt:
    pass
print("LSL streams Stopped")
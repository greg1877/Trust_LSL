# -*- coding: utf-8 -*-
"""
Created on Tue Jul  6 12:38:00 2021

@author: GB_SurfaceBook
"""
import biopacndt
import sys
#import os
import time
#import getopt
from pylsl import StreamInfo, StreamOutlet, local_clock

class StreamData:
    def __init__(self,server):
        self.__server = server
        self.__chanData = [] #initialize the data point list of acquired amplitudes. 
    
    def handleAcquiredData(self, hardwareIndex, frame, channelsInSlice):
        self.__chanData.append(list(frame)) #change the tuple into a list
        
    def returnList(self):
        lastSample = len(self.__chanData)
        if(lastSample > 1):
            return self.__chanData[lastSample-1:] #append the list to chanData

#%% START THE SERVERS AND CREATE THE STREAM

acqServer = biopacndt.AcqNdtQuickConnect()
if not acqServer:
    print("Could not connect to AcqKnowledge Server")
    sys.exit()

enabledChannels = acqServer.DeliverAllEnabledChannels() #Change if only specific channels are required

singleConnectPort = acqServer.getSingleConnectionModePort()

#resourcePath  = os.getcwd() + os.sep + "resources"
#channelToRecord = enabledChannels
#filename = "%s-%s.bin" % (channelToRecord.Type, channelToRecord.Index)
#fullpath = resourcePath + os.sep + filename
#recorder = biopacndt.AcqNdtChannelRecorder(fullpath, channelToRecord)

dataServer = biopacndt.AcqNdtDataServer(singleConnectPort, enabledChannels)

streamData = StreamData(acqServer)
dataServer.RegisterCallback("OutputData", streamData.handleAcquiredData)
#dataServer.RegisterCallback("BinaryRecorder",recorder.Write)

# START THE SERVER
dataServer.Start()

#%% PRINT SOME CHANNEL INFORMATION
acqServer.DeliverAllEnabledChannels()
time.sleep(1)
#%% TURN ON THE ACQUISITION FROM THE COMMAND LINE
acqServer.toggleAcquisition()
print("Toggled Biopac Acquisition... wait 5 seconds")
time.sleep(5)

#%% STREAM INFORMATION

srate = 500
name = 'Biopac_LSL'
stream_type = 'PsychoPhys'
n_channels = 5
channel_names = ["EDA", "ECG", "BPM", "RR-Interval", "ECG Wave Amplitude"]

help_string = 'SendData.py -s <sampling_rate> -n <stream_name> -t <stream_type>'
info = StreamInfo(name, stream_type, n_channels, srate, 'float32', 'myuid34234')

#append some meta-data
info.desc().append_child_value("manufacturer", "Biopac")
chns = info.desc().append_child("channels")
for label in channel_names:
    ch = chns.append_child("channel")
    ch.append_child_value("label", label)
    ch.append_child_value("unit", "microvolts")
    ch.append_child_value("type", label)
#%% PUSH THE DATA ONTO THE STREAM

outlet = StreamOutlet(info)
print("now sending data...")
print("Press Ctrl-c to stop sending")
start_time = local_clock()
sent_samples = 0
jj = 0
try:
    while True: 
        elapsed_time = local_clock() - start_time
        required_samples = int(srate * elapsed_time) - sent_samples
        if required_samples > 0:
            for sample_ix in range(required_samples):
                #get sample from BIOPAC stream
                mysample = streamData.returnList()[0] #This is a hack to obtain the list within the list
                # now send it
                outlet.push_sample(mysample)
            sent_samples += required_samples
            jj+=1;
        # now send it and wait for a bit before trying again.
        time.sleep(0.002) #The sleep time is 1/srate
except KeyboardInterrupt:
        pass
####### STOP HERE: START LAB_RECORDER TO OBTAIN DATA FROM THE STREAM #########    
   
    
#%% TURN OFF THE ACQUISITION FROM THE COMMAND LINE
acqServer.toggleAcquisition()
print("Toggled Biopac Acquisition... wait 5 seconds")
time.sleep(5)


#%% STOP THE SERVER
dataServer.Stop()
print("Stopping the data server")
time.sleep(1)

#%% CLEAN UP

print("Cleaning up...")
del dataServer
del streamData
del acqServer
print("ALl Finished")

        



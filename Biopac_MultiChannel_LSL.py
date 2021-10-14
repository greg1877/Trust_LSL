# -*- coding: utf-8 -*-
"""
Created on Tue Jul  6 12:38:00 2021

@author: GB_SurfaceBook
"""
import biopacndt
import sys
import time
import logging
import keyboard
from datetime import datetime
from pylsl import StreamInfo, StreamOutlet, local_clock

aq_toggle_state = False
srate = 500
rest_time = 1/srate


def get_time_vec():
    year = datetime.now().strftime("%Y")
    month = datetime.now().strftime("%m")
    day = datetime.now().strftime("%d")
    hour = datetime.now().strftime("%H")
    minute = datetime.now().strftime("%M")
    second = datetime.now().strftime("%S")
    micro_second = datetime.now().strftime("%f")
    right_now = int(year + month + day + hour + minute + second + micro_second)
    return right_now

fileName = "bp_s_" + str(get_time_vec()) + ".log"

logging.basicConfig(format='%(asctime)s %(message)s',
    level = logging.INFO,
    filename = fileName)

logger = logging.getLogger()


class StreamData:
    def __init__(self, server):
        self.__server = server
        self.__chanData = []  # initialize the data point list of acquired amplitudes.

    def handleAcquiredData(self, hardwareIndex, frame, channelsInSlice):
        self.__chanData.append(list(frame))  # change the tuple into a list

    def returnList(self):
        lastSample = len(self.__chanData)
        if (lastSample > 1):
            return self.__chanData[lastSample - 1:]  # append the list to chanData


def start_biopac_server():
    global acq_server, data_server, stream_data

    print("Attempting to connect to Acknowledge ")
    acq_server = biopacndt.AcqNdtQuickConnect()
    if not acq_server:
        logger.info("Could not connect to Acknowledge Server")
        print("Could not connect to AcqKnowledge Server ")
        sys.exit()
    else:
        logger.info("Established connection to AcqKnowledge Server")
        print("Established connection to AcqKnowledge Server")

    enabledChannels = acq_server.DeliverAllEnabledChannels()  # Change if only specific channels are required
    singleConnectPort = acq_server.getSingleConnectionModePort()

    data_server = biopacndt.AcqNdtDataServer(singleConnectPort, enabledChannels)
    stream_data = StreamData(acq_server)
    data_server.RegisterCallback("OutputData", stream_data.handleAcquiredData)

    # START THE SERVER
    data_server.Start()
    logger.info("Started Aquisition Server")
    print("Aquisition server started ... wait 5 seconds ")

    # %% PRINT SOME CHANNEL INFORMATION
    acq_server.DeliverAllEnabledChannels()
    time.sleep(5)


def create_biopac_stream():
    global stream_info, stream_outlet

    # %% STREAM INFORMATION
    name = 'Biopac Data'
    stream_type = 'PsychoPhys'
    n_channels = 5
    channel_names = ["EDA", "ECG", "BPM", "RR-Interval", "ECG Wave Amplitude"]

    help_string = 'SendData.py -s <sampling_rate> -n <stream_name> -t <stream_type>'
    stream_info = StreamInfo(name, stream_type, n_channels, srate, 'float32', 'myuid33333')

    # append some meta-data
    stream_info.desc().append_child_value("manufacturer", "Biopac")
    chns = stream_info.desc().append_child("channels")
    for label in channel_names:
        ch = chns.append_child("channel")
        ch.append_child_value("label", label)
        ch.append_child_value("unit", "microvolts")
        ch.append_child_value("type", label)

    logger.info("Created LSL Stream")
    stream_outlet = StreamOutlet(stream_info)


def toggle_aquisition():
    global aq_toggle_state
    print("Current toggle state is ", aq_toggle_state)
    toggle_request = input("Do you want to toggle the Aquisition? Y/N  ")
    if toggle_request.lower() == "y":
        aq_toggle_state = not aq_toggle_state
        acq_server.toggleAcquisition()
        logger.info("Toggled Aquisition")
        print("Toggled Biopac Acquisition... wait 5 seconds... ")
        print("Toggle state is ", aq_toggle_state)
        time.sleep(5)
    else:
        print("Keeping the current state ")


def return_nan():
    return [float("nan"), float("nan"), float("nan"), float("nan"), float("nan")]


def send_biopac_data():  ## Make this a thread
    if not aq_toggle_state:
        toggle_aquisition()
    else:
        send_request = input("Press Y to begin streaming data")
        if send_request.lower() == "y":
            print("now sending data...")
            logger.info("Begin sending data")
            print("Press Ctrl-c to stop sending")

        start_time = local_clock()
        sent_samples = 0

        try:
            while True:
                elapsed_time = local_clock() - start_time
                required_samples = int(srate * elapsed_time) - sent_samples
                if required_samples > 0:
                    for sample_ix in range(required_samples):
                        # get sample from BIOPAC stream
                        if aq_toggle_state:
                            mysample = stream_data.returnList()[0]  # This is a hack to obtain the list within the list
                        else:
                            mysample = return_nan()
                        stream_outlet.push_sample(mysample)
                        sent_samples += required_samples
                # now send it and wait for a bit before trying again.
                time.sleep(rest_time)  #The sleep time is 1/srate
        except KeyboardInterrupt:
            tidy_up()


def tidy_up():
    # %% STOP THE SERVER
    data_server.Stop()
    logger.info("Stopped data server")
    print("Stopping the data server ")
    time.sleep(2)

    # %% TURN OFF THE ACQUISITION FROM THE COMMAND LINE
    acq_server.toggleAcquisition()
    logger.info("Toggled Biopac Acquisition")
    print("Toggled Biopac Acquisition... wait 5 seconds ")
    time.sleep(2)

    print("Cleaning up...")
    del data_server
    del stream_data
    del acq_server
    logger.info("Cleaned up")
    print("All Finished ")

# the channels should be toggled, and when they are, the state
def main():
    start_biopac_server()   # start server
    create_biopac_stream()  # create the stream
    toggle_aquisition()     # toggle the aquisition
    # ask to start the aquisition and check the keyboard to see if some key hasn't been pressed.  If the key is pressed,
    # the aquisition will send null
    send_biopac_data()

if __name__ == '__main__':
    main()










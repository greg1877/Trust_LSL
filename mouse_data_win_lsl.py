# -*- coding: utf-8 -*-
"""
mouse_data_lsl.py takes the mouse position and button clicks and pushes them out to a stream on LSL
Created on Tue Jul  6 12:38:00 2021

@author: Greg Bales
"""
import mouse
import pyautogui
from pylsl import StreamInfo, StreamOutlet, local_clock
import time
from datetime import datetime
import logging

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


fileName = "mouse_stream_" + str(get_time_vec()) + ".log"
logging.basicConfig(format='%(asctime)s %(message)s',
    level = logging.INFO,
    filename = fileName)

logger = logging.getLogger()
srate = 2000
rest_time = 1/srate

screenDim = pyautogui.size()

# Query Mouse Position from Windows
def query_mouse_position():
    x, y = mouse.get_position()
    x = x/screenDim.width
    y = y/screenDim.height

    return [x, y, int(mouse.is_pressed(button="left")),
            int(mouse.is_pressed(button="middle")),
            int(mouse.is_pressed(button="right"))]


class StreamData:
    def __init__(self, server):
        self.__server = server
        self.__chanData = []  # initialize the data point list of acquired amplitudes.

    def handleAcquiredData(self, hardwareIndex, frame, channelsInSlice):
        self.__chanData.append(list(frame))  # change the tuple into a list

    def returnList(self):
        lastSample = len(self.__chanData)
        if lastSample > 1:
            return self.__chanData[lastSample - 1:]  # append the list to chanData


def create_lsl_mouse_stream(srate):
    name = 'Mouse_Info'
    stream_type = 'Mouse_Input'
    n_channels = 5
    channel_names = ["x_m", "y_m", "left_button", "right_button", "middle_button"]

    help_string = 'SendData.py -s <sampling_rate> -n <stream_name> -t <stream_type>'
    info = StreamInfo(name, stream_type, n_channels, srate, 'float32', 'myuid123456')

    # append some meta-data
    info.desc().append_child_value("manufacturer", "none")

    a = info.desc().append_child("screen dimensions")
    a.append_child_value("width", chr(screenDim[0]))
    a.append_child_value("height", chr(screenDim[1]))
    a.append_child_value("unit", "pixels")

    chns = info.desc().append_child("channels")
    for label in channel_names:
        ch = chns.append_child("channel")
        ch.append_child_value("label", label)

    print("Mouse stream created. Now sending data...")
    logger.info("Started mouse stream")
    print("Press Ctrl-c to stop sending")
    return StreamOutlet(info)

def main():
    outlet = create_lsl_mouse_stream(srate)
    start_time = local_clock()
    sent_samples = 0
    jj = 0
    try:
        while True:
            elapsed_time = local_clock() - start_time
            required_samples = int(srate * elapsed_time) - sent_samples
            if required_samples > 0:
                for sample_ix in range(required_samples):
                    # get sample for Stream
                    mysample = query_mouse_position()
                    # now send it
                    outlet.push_sample(mysample)
                    sent_samples += required_samples
                    jj += 1
            # now send it and wait for a bit before trying again.
            time.sleep(rest_time)  # The sleep time is 1/srate
    except KeyboardInterrupt:
        pass
    print("Mouse stream Stopped")
    logger.info("Stopped mouse stream")
    print("Cleaning up...")

    ####### STOP HERE: START LAB_RECORDER TO OBTAIN DATA FROM THE STREAM #########
    del outlet
    logger.info("Stream vars deleted")


if __name__ == '__main__':
    main()

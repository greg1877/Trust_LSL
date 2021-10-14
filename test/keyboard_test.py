# -*- coding: utf-8 -*-
"""
mouse_data_lsl.py takes the mouse position and button clicks and pushes them out to a stream on LSL
Created on Tue Jul  6 12:38:00 2021

@author: Greg Bales
"""
from pynput.keyboard import Key, Listener
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


fileName = "keyboard_stream_" + str(get_time_vec()) + ".log"
logging.basicConfig(format='%(asctime)s %(message)s',
    level = logging.INFO,
    filename = fileName)

logger = logging.getLogger()
srate = 120
rest_time = 1/srate


def query_mouse_position():
    x, y = mouse.get_position()
    #x = x/screenDim.width
    #y = y/screenDim.height
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


def create_keyboard_stream(srate):
    name = 'Keyboard_Info'
    stream_type = 'Keyboard_Input'
    n_channels = 1
    channel_names = ["key"]

    help_string = 'SendData.py -s <sampling_rate> -n <stream_name> -t <stream_type>'
    info = StreamInfo(name, stream_type, n_channels, srate, 'float32', 'myuid123456')

    # append some meta-data
    info.desc().append_child_value("manufacturer", "none")

    chns = info.desc().append_child("channels")
    for label in channel_names:
        ch = chns.append_child("channel")
        ch.append_child_value("label", label)

    print("Keyboard stream created. Now sending data...")
    logger.info("Started keyboard stream")
    print("Press Ctrl-c to stop sending")
    return StreamOutlet(info)


def main():
    outlet = create_keyboard_stream()
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
    print("Keyboard stream Stopped")
    logger.info("Stopped keyboard stream")
    print("Cleaning up...")

    del outlet
    logger.info("Stream vars deleted")


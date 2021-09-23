# -*- coding: utf-8 -*-
"""
mouse_data_lsl.py takes the mouse position and button clicks and pushes them out to a stream on LSL
Created on Tue Jul  6 12:38:00 2021

@author: Greg Bales
"""
import pyautogui
from pylsl import StreamInfo, StreamOutlet, local_clock
import pygame
import logging

logging.basicConfig(format='%(asctime)s %(message)s',
    level=logging.INFO,
    filename='mouse_logs.txt')

logger = logging.getLogger()
srate = 80
rest_time = 1/srate

pygame.init()

# Query Mouse Position from Windows
def query_mouse_position():
    mPos = pyautogui.position()
    mButton = pygame.mouse.get_pressed()
    return [mPos.x, mPos.y, int(mButton[0]), int(mButton[1]), int(mButton[2])]


def get_screen_size():
    screenDim = pyautogui.size()
    return [screenDim.width, screenDim.height]


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
    stream_type = 'Standard_Input'
    n_channels = 5
    channel_names = ["x_mouse", "y_mouse", "left_button_press", "right_button_press", "middle_button_press"]

    help_string = 'SendData.py -s <sampling_rate> -n <stream_name> -t <stream_type>'
    info = StreamInfo(name, stream_type, n_channels, srate, 'float32', 'myuid34234')

    screenDim= get_screen_size()

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
    print("Press Ctrl-c to stop sending")
    return StreamOutlet(info)

def main():
    outlet = create_lsl_mouse_stream(sample_rate)
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
    print("Cleaning up...")

    ####### STOP HERE: START LAB_RECORDER TO OBTAIN DATA FROM THE STREAM #########
    del outlet


if __name__ == '__main__':
    main()

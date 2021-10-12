import numpy as np
import math
import pylsl
import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui
from typing import List
from collections import deque

# Basic parameters for the plotting window
plot_duration = 5  # how many seconds of data to show
update_interval = 15  # ms between screen updates
pull_interval = 500  # ms between each pull operation

def check_nan(num):
    if float('-inf') < float(num) < float('inf'):
        return False
    else:
        return True

class Inlet:
    """Base class to represent a plottable inlet"""
    def __init__(self, info: pylsl.StreamInfo):
        # create an inlet and connect it to the outlet we found earlier.
        # max_buflen is set so data older the plot_duration is discarded
        # automatically and we only pull data new enough to show it

        # Also, perform online clock synchronization so all streams are in the
        # same time domain as the local lsl_clock()
        # (see https://labstreaminglayer.readthedocs.io/projects/liblsl/ref/enums.html#_CPPv414proc_clocksync)
        # and dejitter timestamps
        self.inlet = pylsl.StreamInlet(info, max_chunklen=plot_duration, max_buflen=plot_duration,
                                       processing_flags=pylsl.proc_clocksync | pylsl.proc_dejitter)
        # store the name and channel count
        self.name = info.name()
        self.channel_count = info.channel_count()

    def pull_and_plot(self, plot_time: float, plt: pg.PlotItem):
        """Pull data from the inlet and add it to the plot.
        :param plot_time: lowest timestamp that's still visible in the plot
        :param plt: the plot the data should be shown on
        """
        # We don't know what to do with a generic inlet, so we skip it.
        pass


class DataInlet(Inlet):
    """A DataInlet represents an inlet with continuous, multi-channel data that
    should be plotted as multiple lines."""
    dtypes = [[], np.float32, np.float64, None, np.int32, np.int16, np.int8, np.int64]

    def __init__(self, info: pylsl.StreamInfo, plt: pg.PlotItem):
        super().__init__(info)
        # calculate the size for our buffer, i.e. two times the displayed data
        bufsize = (2 * math.ceil(info.nominal_srate() * plot_duration), info.channel_count())
        self.buffer = np.empty(bufsize, dtype=self.dtypes[info.channel_format()])
        empty = np.array([])
        # create one curve object for each channel/line that will handle displaying the data
        self.curves = [pg.PlotCurveItem(x=empty, y=empty, autoDownsample=True) for _ in range(self.channel_count)]
        for curve in self.curves:
            plt.addItem(curve)

    def pull_and_plot(self, plot_time, plt):
        # pull the data
        _, ts = self.inlet.pull_chunk(timeout=0.0,
                                      max_samples=self.buffer.shape[0],
                                      dest_obj=self.buffer)
        # ts will be empty if no samples were pulled, a list of timestamps otherwise
        if ts:
            ts = np.asarray(ts)
            y = self.buffer[0:ts.size, :]
            this_x = None
            old_offset = 0
            new_offset = 0
            for ch_ix in range(self.channel_count):
                # we don't pull an entire screen's worth of data, so we have to
                # trim the old data and append the new data to it
                old_x, old_y = self.curves[ch_ix].getData()
                # the timestamps are identical for all channels, so we need to do
                # this calculation only once
                if ch_ix == 0:
                    # find the index of the first sample that's still visible,
                    # i.e. newer than the left border of the plot
                    old_offset = old_x.searchsorted(plot_time)
                    # same for the new data, in case we pulled more data than
                    # can be shown at once
                    new_offset = ts.searchsorted(plot_time)
                    # append new timestamps to the trimmed old timestamps
                    this_x = np.hstack((old_x[old_offset:], ts[new_offset:]))
                # append new data to the trimmed old data
                this_y = np.hstack((old_y[old_offset:], y[new_offset:, ch_ix] - ch_ix))
                # replace the old data
                self.curves[ch_ix].setData(this_x, this_y)


class MarkerInlet(Inlet):
    """A MarkerInlet shows events that happen sporadically as vertical lines"""
    def __init__(self, info: pylsl.StreamInfo):
        super().__init__(info)

    def pull_and_plot(self, plot_time, plt):
        # TODO: purge old markers
        strings, timestamps = self.inlet.pull_chunk(0)
        if timestamps:
            for string, ts in zip(strings, timestamps):
                plt.addItem(pg.InfiniteLine(ts, angle=90, movable=False, label=string[0]))


class Graph:
    def __init__(self, ):
        self.dat = deque()
        self.maxLen = 50  # max number of data points to show on graph
        self.app = QtGui.QApplication([])
        self.win = pg.GraphicsWindow()

        self.p1 = self.win.addPlot(colspan=2, title="EEG")
        self.win.nextRow()
        self.p2 = self.win.addPlot(colspan=2, title="Biophys")
        self.win.nextRow()
        self.p3 = self.win.addPlot(colspan=2, title="Mouse")
        self.win.nextRow()
        self.p4 = self.win.addPlot(colspan=2, title="Eyetracker")

        self.curve1 = self.p1.plot(title="EEG")
        self.curve2 = self.p2.plot(title="Biophys")
        self.curve3 = self.p3.plot(title="Mouse")
        self.curve4 = self.p4.plot(title="Eyetracker")

        timer = QtCore.QTimer()  # to create a thread that calls a function at intervals
        timer.timeout.connect(self.update)  # the update function keeps getting called at intervals
        timer.start(update_interval)
        QtGui.QApplication.instance().exec_()

    def update(self):
        if len(self.dat) > self.maxLen:
            self.dat.popleft()  # remove oldest
        self.dat.append(random.randint(0, 100))

        self.curve1.setData(self.dat)
        self.curve2.setData(self.dat)
        self.curve3.setData(self.dat)
        self.curve4.setData(self.dat)
        self.app.processEvents()


def main():
    # first resolve all streams that could be shown
    print("looking for streams")
    streams = pylsl.resolve_streams()
    stream_types = ["EEG", "Biophys", "Mouse_Input", "Eyetracker"]
    inlets: List[Inlet] = []

    if len(streams)>=1:
        for idx in range(len(streams)):
            print("Found stream type "+ streams[idx].type() + " ")
    else:
        print("Could not find a stream")

    print("EEG............press 1")
    print("Biophys........press 2")
    print("Mouse..........press 3")
    print("Eyetracker.....press 4")
    select_stream_type = int(input("Please select a stream type: "))
    #select_stream_type = 3

    stream_to_plot = pylsl.resolve_byprop("type", stream_types[select_stream_type - 1], timeout=2)

    # Create the pyqtgraph window
    pw = pg.plot(title=stream_types[select_stream_type-1])
    plt = pw.getPlotItem()
    plt.enableAutoRange(x=False, y=True)

    # iterate over found streams, creating specialized inlet objects that will
    # handle plotting the data
    for info in stream_to_plot:
        if info.type() == 'Markers':
            if info.nominal_srate() != pylsl.IRREGULAR_RATE \
                    or info.channel_format() != pylsl.cf_string:
                print('Invalid marker stream ' + info.name())
            print('Adding marker inlet: ' + info.name())
            inlets.append(MarkerInlet(info))
        elif info.nominal_srate() != pylsl.IRREGULAR_RATE \
                and info.channel_format() != pylsl.cf_string:
            print('Adding data inlet: ' + info.name())
            inlets.append(DataInlet(info, plt))
        else:
            print('Don\'t know what to do with stream ' + info.name())

    def scroll():
        """Move the view so the data appears to scroll"""
        # We show data only up to a timepoint shortly before the current time
        # so new data doesn't suddenly appear in the middle of the plot
        fudge_factor = pull_interval * .002
        plot_time = pylsl.local_clock()
        pw.setXRange(plot_time - plot_duration + fudge_factor, plot_time - fudge_factor)

    def update():
        # Read data from the inlet. Use a timeout of 0.0 so we don't block GUI interaction.
        mintime = pylsl.local_clock() - plot_duration
        # call pull_and_plot for each inlet.
        # Special handling of inlet types (markers, continuous data) is done in
        # the different inlet classes.
        for inlet in inlets:
            inlet.pull_and_plot(mintime, plt)

    # create a timer that will move the view every update_interval ms
    update_timer = QtCore.QTimer()
    update_timer.timeout.connect(scroll)
    update_timer.start(update_interval)

    # create a timer that will pull and add new data occasionally
    pull_timer = QtCore.QTimer()
    pull_timer.timeout.connect(update)
    pull_timer.start(pull_interval)


    import sys

    # Start Qt event loop unless running in interactive mode or using pyside.
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()


if __name__ == '__main__':
    main()
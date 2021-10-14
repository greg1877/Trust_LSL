import numpy as np
import math
import pylsl
import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui
from typing import List

win = pg.GraphicsLayoutWidget(show=True)
win.setWindowTitle('LSL Streams')
pw = []
for idx in range(4):
    pw.append(win.addPlot(row=idx, col=0, colspan=2, title="balls"))

pg.exec()
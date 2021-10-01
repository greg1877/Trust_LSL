import receive_and_plot_LSL_stream as rcp
from typing import List
import pylsl

stream_types = ["EEG","Biophys","Screen_Input"]
streams = []
inlets: List[rcp.Inlet] = []

for idx in range(len(stream_types)):
    streams.append(pylsl.resolve_byprop("type", stream_types[idx], timeout=2))

for idx in range(len(streams)):
    l: int=len(streams[idx])
    if l==1:
        rcp.plot_stream_type(streams[idx][0], inlets)
    elif not l==0:
        rcp.plot_stream_type(streams[idx][:], inlets)


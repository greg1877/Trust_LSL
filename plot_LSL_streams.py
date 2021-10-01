import receive_and_plot_LSL_stream as rcp
from typing import List
import pylsl
import threading

stream_types = ["EEG","Biophys","Screen_Input"]
streams = []
inlets: List[rcp.Inlet] = []


def main():
    for idx in range(len(stream_types)):
        streams.append(pylsl.resolve_byprop("type", stream_types[idx], timeout=2))

    for idx in range(len(streams)):
        l: int=len(streams[idx])
        if not l==0:
            print("Starting a Thread")
            threading.Thread(target = rcp.plot_stream_type(streams[idx][:], inlets)).start()
            #threading.start_new_thread(rcp.plot_stream_type(streams[idx][:], inlets))


if __name__ == '__main__':
    main()



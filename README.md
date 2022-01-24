# Trust_LSL
These python scripts provide the connection of various data to the LSL stream.

To run any script in Windows, open a terminal and type "python" followed by the name of the script.  For example: ``python .\LSL_sender.py``  Each script must run in a separate terminal.  Type ``^C`` (preferred) or close the terminal to kill the process.

  * ``LSL_Stream_Viewer.py`` Finds all regularly sampled LSL streams (those of a fixed sample rate) and plots them on the screen. 
  * ``LSL_sender.py`` creates several LSL streams to check functionality of the viewer.
  * ``mouse_data_win_lsl.py`` creates an LSL stream of the mouse output--pixel position and button clicks.
  * ``Biopac_Multichannel_LSL.py`` pulls the output data from the Biopac module and places them onto a LSL stream.

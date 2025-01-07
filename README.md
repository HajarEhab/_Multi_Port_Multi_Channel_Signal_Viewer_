# _Multi_Port_Multi_Channel_Signal_Viewer_
# Introduction
This project is a Python Qt-based desktop application designed to handle multi-channel signal viewing for visualizing and analyzing Biomedical signals.

# Features
Signal File Browsing: Users can browse their PC to open signal files.
Independent Graphs: Two identical graphs allow the user to display different signals, each with independent controls.
Graph Linking: Users can link the two graphs, ensuring synchronized playback, zooming, panning, and viewport adjustments.
Cine Mode: Signals are displayed dynamically. A rewind option is available to restart the signal from the beginning or stop it.
Signal Manipulations:
Change signal color.
Add titles/labels to signals.
Show/hide signals.
Adjust cine speed.
Pause, play, or rewind signals.
Zoom in/out and pan signals.
Scroll through signals using sliders.
Move signals between the two graphs.
![image](https://github.com/user-attachments/assets/a78631b6-e4b4-4b0a-9948-0d7647370825)

Non-Rectangular Visualization: Provides non-rectangular views of the signal data for advanced insights and visualization beyond standard Cartesian graphs.
![image](https://github.com/user-attachments/assets/80875f7f-1384-4245-b0c0-926d1c5b308b)

API Integration: An API feature allows integration with external systems for importing signals or interacting with remote signal sources.

Signal Gluing: Users can select and cut segments from the two signals displayed in each of the two viewers. These segments can then be glued together to create a continuous signal. This feature enables users to merge different parts of signals, which is useful for combining multiple segments or signals from different sources. 

# Export and Reporting:
![image](https://github.com/user-attachments/assets/046364c9-4213-4822-add8-4c97865dfd12)

Generate PDF reports with snapshots of graphs and signal statistics.
Include data statistics (mean, median, standard deviation, min, and max values) in a well-structured table.
Support single or multi-page PDF reports with an organized layout.

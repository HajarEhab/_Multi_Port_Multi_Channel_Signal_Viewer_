import sys
import numpy as np
import pandas as pd
from PyQt5.QtWidgets import (QApplication, QWidget, QPushButton, QLabel, QRadioButton, 
                             QVBoxLayout, QHBoxLayout, QSlider, QLineEdit, QDialog,QDialogButtonBox,QGroupBox,QButtonGroup,
                             QScrollBar, QGridLayout, QComboBox, QFileDialog, QColorDialog, QSpacerItem, QSizePolicy,QFormLayout,QMessageBox
)


from PyQt5.QtCore import Qt, QTimer,QRect
import pyqtgraph as pg
from PyQt5.QtGui import QColor
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
import os
import numpy as np
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from PyQt5.QtWidgets import QFileDialog
from pyqtgraph import exporters

class SignalColorDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.selected_color = None
        self.selected_title = None
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Signal Properties")
        layout = QFormLayout()

        # Color Picker
        self.color_button = QPushButton("Select Color")
        self.color_button.clicked.connect(self.choose_color)
        layout.addRow("Color:", self.color_button)

        # Title Input
        self.title_input = QLineEdit()
        layout.addRow("Signal Title:", self.title_input)

        # Buttons
        button_box = QHBoxLayout()
        ok_button = QPushButton("OK")
        ok_button.clicked.connect(self.accept)
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        button_box.addWidget(ok_button)
        button_box.addWidget(cancel_button)
        layout.addRow(button_box)

        self.setLayout(layout)

    def choose_color(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.selected_color = color
            self.color_button.setStyleSheet(f"background-color: {color.name()};")
    def get_color(self):

        return self.selected_color

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        
        self.graph_data = []
        self.timers = []      # Timers for playing signals
        self.current_indices = [] 
        self.timer_states = []
        self.selected_color=SignalColorDialog().get_color()
        self.plotted_signals = [] 
        self.selected_colors = {} 
        self.signal_visibility = {} 
        self.is_linked = False
         # Track previous scroll values for each graph
        self.prev_horizontal_scroll = {'graph1': 50, 'graph2': 50, 'gluedGraph': 50}
        self.prev_vertical_scroll = {'graph1': 50, 'graph2': 50, 'gluedGraph': 50}
        #data bounds for graph1
        self.graph1_x_min = -100
        self.graph1_x_max = 100
        self.graph1_y_min = -10
        self.graph1_y_max = 10

        #data bounds for graph2
        self.graph2_x_min = -100
        self.graph2_x_max = 100
        self.graph2_y_min = -10
        self.graph2_y_max = 10

        #data bounds for gluedGraph
        self.gluedGraph_x_min = -100
        self.gluedGraph_x_max = 100
        self.gluedGraph_y_min = -10
        self.gluedGraph_y_max = 10

        self.initUI()
        #self.load_default_file()
    def initUI(self):
        
        self.setStyleSheet("""
         QWidget {
                background-color: #BBDEFB; /* Light sky blue */
            }                  

        QPushButton {
            background-color: #007BFF; /* Blue color */
            color: white;
            border: none;
            border-radius: 4px;
            padding: 5px 10px;
        }
        QPushButton:hover {
            background-color: #0056b3;
        }
        QPushButton:pressed {
            background-color: #004085;
        }
        QLineEdit {
            border: 1px solid #ced4da;
            border-radius: 3px;
            padding: 2px;
        }
        QLabel {
            color: #212529;
            font-size: 14px;
        }
        QScrollBar:vertical {
            background: #f8f9fa;
            border: none;
            width: 10px;
            margin: 0px;
        }
        QScrollBar:horizontal {
            background: #f8f9fa;
            border: none;
            height: 10px;
            margin: 0px;
        }
    """)
        
        
        #Layout for the entire window
        mainLayout = QVBoxLayout()

        # Top Row: Non-Rectangle Viewer, Address Field
        topLayout = QHBoxLayout()
        nonRectangleBtn = QPushButton('Non-Rectangle Viewer')
        signalInput = QLineEdit('Enter address of a realtime signal source')
        topLayout.addWidget(nonRectangleBtn)
        topLayout.addWidget(signalInput)

        mainLayout.addLayout(topLayout)

        # Editable labels for renaming graphs
        graph1Label = QLineEdit('Graph 1')
        graph1Label.setFixedWidth(150)  # Decrease width
        graph2Label = QLineEdit('Graph 2')
        graph2Label.setFixedWidth(150)  # Decrease width
        gluedLabel = QLineEdit('Glued Signals')
        gluedLabel.setFixedWidth(150)  # Decrease width

        # Initialize graphs
        self.graph1 = pg.PlotWidget()
        self.graph1.showGrid(x=True, y=True)
        self.graph1.setLimits(xMin=0)
       # Set background and grid
        #self.graph1.setBackground('#131E3A')


        self.graph2 = pg.PlotWidget()
        self.graph2.showGrid(x=True, y=True)
        self.graph2.setLimits(xMin=0)

        self.gluedGraph = pg.PlotWidget()
        self.gluedGraph.showGrid(x=True, y=True)
        self.gluedGraph.setLimits(xMin=0)
         
        # Set sizes for the graphs
        self.graph1.setFixedSize(1700, 250)
        self.graph2.setFixedSize(1700, 250)
        self.gluedGraph.setFixedSize(1700, 250)

        # Define components to be added beside each graph
        for graph, label, graphIndex in [
            (self.graph1, graph1Label, 1), 
            (self.graph2, graph2Label, 2), 
            (self.gluedGraph, gluedLabel, 3)
        ]:
            graphContainer = QVBoxLayout()
            graphContainer.addWidget(label)

            # Horizontal layout for the graph, scrollbars, and control buttons
            graphRow = QHBoxLayout()

            verticalScrollBar = QScrollBar(Qt.Vertical)
            verticalScrollBar.setRange(0, 100)  # Set the range for the scrollbar
            verticalScrollBar.setValue(50)     # Set the initial position to the middle
            verticalScrollBar.valueChanged.connect(lambda value, g=graph: self.vertical_scroll(value, g))
            graphRow.addWidget(verticalScrollBar)

            # Add the graph widget
            graphRow.addWidget(graph)

            # Control buttons with reduced width aligned on the right side
            controlLayout = QVBoxLayout()

            buttonWidth = 100  # Set button width for a compact layout
            

              
            # Open and Connect buttons for Graph 1 and Graph 2
            if graphIndex in [1, 2]:
                openBtn = QPushButton('Open')
                openBtn.setFixedWidth(buttonWidth)
                connectBtn = QPushButton('Connect')
                connectBtn.setFixedWidth(buttonWidth)
                controlLayout.addWidget(openBtn)
                controlLayout.addWidget(connectBtn)
                openBtn.clicked.connect(lambda checked, g=graph: self.open_file(g))

           
           

            # Add specific buttons for Graph 1, Graph 2, and Glued Graph
            if graphIndex == 1:
                moveBtn = QPushButton('Move')
                play_button_Graph1 = QPushButton('Play / Pause')
                rewind_button_Graph1 = QPushButton('Rewind')
                color_button_Graph1 = QPushButton('Color')
                zoom_in_butt1=QPushButton('Zoom In')
                zoom_out_butt1=QPushButton('Zoom Out')
                showHideBtn1 = QPushButton('Show/Hide')



                moveBtn.setFixedWidth(buttonWidth)
                play_button_Graph1.setFixedWidth(buttonWidth)
                rewind_button_Graph1.setFixedWidth(buttonWidth)
                color_button_Graph1.setFixedWidth(buttonWidth)
                zoom_in_butt1.setFixedWidth(buttonWidth)
                zoom_out_butt1.setFixedWidth(buttonWidth)
                showHideBtn1.setFixedWidth(buttonWidth)



                controlLayout.addWidget(play_button_Graph1)
                controlLayout.addWidget(rewind_button_Graph1)
                controlLayout.addWidget(color_button_Graph1)
                controlLayout.addWidget(moveBtn)
                controlLayout.addWidget(zoom_in_butt1)
                controlLayout.addWidget(zoom_out_butt1)
                controlLayout.addWidget(showHideBtn1)



                play_button_Graph1.clicked.connect(lambda: self.toggle_play_pause(0, play_button_Graph1))
                rewind_button_Graph1.clicked.connect(lambda : self.rewind_signal(0))
                zoom_in_butt1.clicked.connect(lambda: self.zoom(self.graph1, 0.75))
                zoom_out_butt1.clicked.connect(lambda: self.zoom(self.graph1, 1.25)) 
                showHideBtn1.clicked.connect(lambda: self.toggle_visibility(self.graph1))
                color_button_Graph1.clicked.connect(lambda: self.change_color(1))
                moveBtn.clicked.connect(self.move_signal)



            if graphIndex == 2:
                linkBtn = QPushButton('Link')
                play_button_Graph2 = QPushButton('Play / Pause')
                rewind_button_Graph2 = QPushButton('Rewind')
                color_button_Graph2 = QPushButton('Color')
                zoom_in_butt2=QPushButton('Zoom In')
                zoom_out_butt2=QPushButton('Zoom Out')
                showHideBtn2 = QPushButton('Show/Hide')

                linkBtn.setFixedWidth(buttonWidth)
                play_button_Graph2.setFixedWidth(buttonWidth)
                rewind_button_Graph2.setFixedWidth(buttonWidth)
                color_button_Graph2.setFixedWidth(buttonWidth)
                zoom_in_butt2.setFixedWidth(buttonWidth)
                zoom_out_butt2.setFixedWidth(buttonWidth)
                showHideBtn2.setFixedWidth(buttonWidth)

                controlLayout.addWidget(play_button_Graph2)
                controlLayout.addWidget(rewind_button_Graph2)
                controlLayout.addWidget(color_button_Graph2)
                controlLayout.addWidget(linkBtn)
                controlLayout.addWidget(zoom_in_butt2)
                controlLayout.addWidget(zoom_out_butt2)
                controlLayout.addWidget(showHideBtn2)
                play_button_Graph2.clicked.connect(lambda: self.toggle_play_pause(1, play_button_Graph2))
                rewind_button_Graph2.clicked.connect(lambda :  self.rewind_signal(1))
                zoom_in_butt2.clicked.connect(lambda: self.zoom(self.graph2, 0.75))
                zoom_out_butt2.clicked.connect(lambda: self.zoom(self.graph2, 1.25)) 
                showHideBtn2.clicked.connect(lambda: self.toggle_visibility(self.graph2))
                color_button_Graph2.clicked.connect(lambda: self.change_color(2))
                linkBtn.clicked.connect(self.toggle_link)


            if graphIndex == 3:
                for btn_text in [ 'Export Report' ,' Snapshot','Select']:
                    button = QPushButton(btn_text)
                    button.setFixedWidth(buttonWidth)
                    controlLayout.addWidget(button)
             
               
                # Text inputs and Glue button
                gapInput = QLineEdit('Enter gap value')
                gapInput.setFixedWidth(150)  # Decrease width
                interpInput = QLineEdit('Enter interpolation value')
                interpInput.setFixedWidth(150)  # Decrease width
                glueBtn = QPushButton('Glue')
                glueBtn.setFixedWidth(buttonWidth)
                zoom_in_butt3=QPushButton('Zoom In')
                zoom_out_butt3=QPushButton('Zoom Out')
                showHideBtn3 = QPushButton('Show/Hide')
                zoom_in_butt3.setFixedWidth(buttonWidth)
                zoom_out_butt3.setFixedWidth(buttonWidth)
                showHideBtn3.setFixedWidth(buttonWidth)
                controlLayout.addWidget(zoom_in_butt3)
                controlLayout.addWidget(zoom_out_butt3)
                controlLayout.addWidget(showHideBtn3)

                controlLayout.addWidget(gapInput)
                controlLayout.addWidget(interpInput)
                controlLayout.addWidget(glueBtn)
                zoom_in_butt3.clicked.connect(lambda: self.zoom(self.gluedGraph, 0.75))
                zoom_out_butt3.clicked.connect(lambda: self.zoom(self.gluedGraph, 1.25)) 
                showHideBtn3.clicked.connect(lambda: self.toggle_visibility(self.gluedGraph))
                if btn_text == 'Export Report':
                    button.clicked.connect(self.export_report)  # Connect to export_report method
                elif btn_text == 'Snapshot':
                    button.clicked.connect(self.take_snapshot) 

            spacer = QSpacerItem(20, 10, QSizePolicy.Minimum, QSizePolicy.Expanding)
            controlLayout.addItem(spacer)
              
            cineSpeedLabel = QLabel(f'Cine Speed ')
            cineSpeedSlider = QSlider(Qt.Horizontal)
            cineSpeedSlider.setRange(1, 10)  # Speed factor range: 1x (slowest) to 10x (fastest)
            cineSpeedSlider.setValue(5)
            cineSpeedSlider.setFixedWidth(150)
            # Add cine speed slider to the control layout
            controlLayout.addWidget(cineSpeedLabel)
            controlLayout.addWidget(cineSpeedSlider)

             # Connect the slider to adjust speed for the corresponding graph
            cineSpeedSlider.valueChanged.connect(lambda value, idx=graphIndex-1: self.adjust_speed(idx, value))
           
    

            # Add control layout to the graph row and move it further to the right
            graphRow.addLayout(controlLayout, 1)  # Adding stretch factor for right alignment

            # Add the graph row to the container layout
            graphContainer.addLayout(graphRow)

            # Move the horizontal scrollbar below each graph to the left
            horizontalScrollBar = QScrollBar(Qt.Horizontal)
            horizontalScrollBar.setRange(0, 100)  # Set the range for the scrollbar
            horizontalScrollBar.setValue(50)     # Set the initial position to the middle
            horizontalScrollBar.valueChanged.connect(lambda value, g=graph: self.horizontal_scroll(value, g))
            graphContainer.addWidget(horizontalScrollBar)

            # Add the complete container to the main layout
            mainLayout.addLayout(graphContainer)
          
        # Align control buttons to the right
        for i in range(mainLayout.count()):
            item = mainLayout.itemAt(i)
            itemLayout = item.layout()
            itemLayout.setAlignment(Qt.AlignRight)
        showHideBtn1.setObjectName("showHideBtn1")
        showHideBtn2.setObjectName("showHideBtn2")
        showHideBtn3.setObjectName("showHideBtn3")

        # Set main layout
        self.setLayout(mainLayout)
        self.setWindowTitle('Signal Viewer')
        self.show()

    def horizontal_scroll(self, current_value, graph):
        """Handle horizontal scrolling for the given graph."""
        graph_name = self.get_graph_name(graph)  # Map graph object to its name
        prev_value = self.prev_horizontal_scroll[graph_name]
        difference = current_value - prev_value

        if difference != 0:
            self.update_graph_view(graph, 'x', difference)

        self.prev_horizontal_scroll[graph_name] = current_value

    def vertical_scroll(self, current_value, graph):
        """Handle vertical scrolling for the given graph."""
        graph_name = self.get_graph_name(graph)
        prev_value = self.prev_vertical_scroll[graph_name]
        difference = current_value - prev_value

        if difference != 0:
            self.update_graph_view(graph, 'y', difference)

        self.prev_vertical_scroll[graph_name] = current_value

    def get_graph_name(self, graph):
        """Return the name of the graph based on its object."""
        if graph == self.graph1:
            return 'graph1'
        elif graph == self.graph2:
            return 'graph2'
        elif graph == self.gluedGraph:
            return 'gluedGraph'
        return None


    def update_graph_view(self, graph, axis, difference):
        """Update the graph's view range based on scroll movement."""
        current_range = graph.viewRange()  # Get the current view range

        # Get data bounds for the graph
        data_bounds = self.get_data_bounds(graph)
        if data_bounds is None:
            return

        scaling_factor = 0.01  # Scaling factor to control scroll sensitivity

        if axis == 'x':
            # Adjust X-axis range based on scroll difference
            new_x_min = max(data_bounds['x_min'], current_range[0][0] + difference * scaling_factor)
            new_x_max = min(data_bounds['x_max'], current_range[0][1] + difference * scaling_factor)

            # Ensure we don't scroll past the data bounds
            if new_x_min < new_x_max:
                graph.setXRange(new_x_min, new_x_max, padding=0)

        elif axis == 'y':
            # Adjust Y-axis range based on scroll difference
            new_y_min = max(data_bounds['y_min'], current_range[1][0] + difference * scaling_factor)
            new_y_max = min(data_bounds['y_max'], current_range[1][1] + difference * scaling_factor)

            # Ensure we don't scroll past the data bounds
            if new_y_min < new_y_max:
                graph.setYRange(new_y_min, new_y_max, padding=0)

    def get_data_bounds(self, graph):
        """Retrieve the data bounds for the given graph."""
        if graph == self.graph1:
            return {'x_min': self.graph1_x_min, 'x_max': self.graph1_x_max, 'y_min': self.graph1_y_min, 'y_max': self.graph1_y_max}
        elif graph == self.graph2:
            return {'x_min': self.graph2_x_min, 'x_max': self.graph2_x_max, 'y_min': self.graph2_y_min, 'y_max': self.graph2_y_max}
        elif graph == self.gluedGraph:
            return {'x_min': self.gluedGraph_x_min, 'x_max': self.gluedGraph_x_max, 'y_min': self.gluedGraph_y_min, 'y_max': self.gluedGraph_y_max}
        return None


    def load_default_file(self):
        default_file_path = "C:/final_task-1/normal_ecg.csv"  
        
        try:
            data = pd.read_csv(default_file_path, header=None)
            time = data[0].to_numpy()
            signal = data[1].to_numpy()
            time = time - time[0]  

            
            graph_index = 0
            while len(self.graph_data) <= graph_index:
                self.graph_data.append([])
            while len(self.current_indices) <= graph_index:
                self.current_indices.append(0)
                self.timers.append(QTimer(self))
            
            self.graph_data[graph_index].append((time, signal))

            if not self.timers[graph_index].isActive():
                self.timers[graph_index].timeout.connect(lambda g=self.graph1, gi=graph_index: self.plot_all_signals(g, gi))
                self.timers[graph_index].start(50)

            self.current_indices[graph_index] = 0
            self.plot_all_signals(self.graph1, graph_index)  

        except Exception as e:
            print(f"Error loading default file: {e}")

    def open_file(self, graph):
     """Handles file opening and updates the selected graph."""
     file_name, _ = QFileDialog.getOpenFileName(self, "Open File", "", "CSV Files (*.csv);;All Files (*)")
     if file_name:
       
        data = pd.read_csv(file_name, header=None)
        time = data[0].to_numpy()
        signal = data[1].to_numpy()
        time = time - time[0]
        if graph == self.graph1:
            graph_index = 0
        elif graph == self.graph2:
            graph_index = 1
        else:
            return  
        while len(self.graph_data) <= graph_index:
            self.graph_data.append([])
        while len(self.current_indices) <= graph_index:
            self.current_indices.append(0)
            self.timers.append(QTimer(self))

        
        dialog = SignalColorDialog()
        if dialog.exec_() == QDialog.Accepted:
            color = dialog.selected_color.name() if dialog.selected_color else 'b'
            title = dialog.title_input.text() or f"Signal {len(graph.listDataItems()) + 1}"
            signal_index = len(self.graph_data[graph_index])
            self.selected_colors[(graph_index, signal_index)] = color
            self.graph_data[graph_index].append((time, signal))

            if not self.timers[graph_index].isActive():
                self.timers[graph_index].timeout.connect(lambda g=graph, gi=graph_index: self.plot_all_signals(g, gi))
                self.timers[graph_index].start(50)
        
        
        self.current_indices[graph_index] = 0
        self.plot_all_signals(graph, graph_index)
        print(f"Number of timers: {len(self.timers)}")

    def move_signal(self):
     """Moves plotted signals from Graph 1 to Graph 2, clears Graph 1, and starts plotting on Graph 2."""
   
     if len(self.graph_data) > 0 and len(self.graph_data[0]) > 0:
       
        if len(self.graph_data) < 2:
            self.graph_data.append([])  
            self.timers.append(QTimer(self)) 
        self.graph_data[1].extend(self.graph_data[0])  

       
        self.graph_data[0] = [] 
        self.current_indices[0] = 0  
        self.graph1.clear()  

       
        self.current_indices[1] = 0  
        self.plot_all_signals(self.graph2, 1)  

    def plot_all_signals(self, graph, graph_index):
     """Plots all signals on the specified graph."""
     graph.clear()
     for i, (time, signal) in enumerate(self.graph_data[graph_index]):
        if self.current_indices[graph_index] < len(time):
            current_time = time[:self.current_indices[graph_index]]
            current_signal = signal[:self.current_indices[graph_index]]
            pen_color = self.selected_colors.get((graph_index, i), 'b')
            if self.signal_visibility.get(graph_index, True):
                graph.plot(current_time, current_signal, pen=pen_color, clear=False)
     self.current_indices[graph_index] += 1

    def toggle_link(self):
     """Toggles the linking state between Graph 1 and Graph 2."""
     self.is_linked = not self.is_linked
     if self.is_linked:
        print("Graphs are now linked.")
        self.rewind_signal(0)  
        self.rewind_signal(1) 
     else:
        print("Graphs are now unlinked.")
    def adjust_speed(self, graph_index, value):
     if graph_index < len(self.timers):
        speed_factor = value  # Speed factor from slider (1 to 10)
        if speed_factor <= 0:
            speed_factor = 1  # 

        if self.is_linked:
             new_interval= int(100 / speed_factor)
             self.timers[0].setInterval(new_interval)
             self.timers[1].setInterval(new_interval)
       
        else:
        # Calculate new timer interval (inverse of speed factor)
         new_interval = int(100 / speed_factor)  # Base interval: 100ms for 1x speed
         self.timers[graph_index].setInterval(new_interval)

        
        
    def toggle_play_pause(self,graph_index , button):
        """Toggles play/pause for a specific signal."""
        if self.is_linked:
       
         other_graph_index = 1 if graph_index == 0 else 0
         self.sync_play_pause(graph_index, other_graph_index, button)
        else:
       
         if self.timers[graph_index].isActive():
            self.timers[graph_index].stop()
            button.setText("Play")
         else:
            self.timers[graph_index].start(50)
            button.setText("Pause")
    def sync_play_pause(self, graph_index1, graph_index2, button):
     """Sync play/pause for both linked graphs."""
     if self.timers[graph_index1].isActive() and self.timers[graph_index2].isActive():
        self.timers[graph_index1].stop()
        self.timers[graph_index2].stop()
        button.setText("Play")
     else:
        self.timers[graph_index1].start(50)
        self.timers[graph_index2].start(50)
        button.setText("Pause")        
    def rewind_signal(self, graph_index):
        if self.is_linked:
         other_graph_index = 1 if graph_index == 0 else 0
         self.sync_rewind(graph_index, other_graph_index)
        else:
         self.rewind_single_graph(graph_index)

    def sync_rewind(self, graph_index1, graph_index2):
     """Rewinds both linked graphs."""
     self.rewind_single_graph(graph_index1)
     self.rewind_single_graph(graph_index2)
    def rewind_single_graph(self, graph_index):
     """Rewinds a single graph."""
     self.timers[graph_index].stop()
     self.current_indices[graph_index] = 0
     if graph_index == 0:
        graph = self.graph1
     elif graph_index == 1:
        graph = self.graph2
     else:
        graph = self.gluedGraph
     graph.clear()
     self.plot_all_signals(graph, graph_index)
     self.timers[graph_index].start(50)

    def change_color(self, graph_index):
   
     if graph_index == 1:
        graph = self.graph1
     elif graph_index == 2:
        graph = self.graph2
     elif graph_index == 3:
        graph = self.gluedGraph
     else:
        return

   
     if graph_index - 1 < len(self.graph_data):
        dialog = QColorDialog(self)
        new_color = dialog.getColor()
        
        if new_color.isValid():
           
            color_hex = new_color.name()
            
           
            signal_index = 0  
            if (graph_index - 1, signal_index) in self.selected_colors:
                self.selected_colors[(graph_index - 1, signal_index)] = color_hex
            if self.is_linked:
                other_graph = self.graph2 if graph == self.graph1 else self.graph1
                self.apply_linked_color(graph, other_graph, color_hex)

            
            self.plot_all_signals(graph , graph_index - 1)
    def apply_linked_color(self, graph1, graph2, color_hex):
     """Apply the color change to both linked graphs."""
    
     graph1_index = self.get_graph_index(graph1)
     graph2_index = self.get_graph_index(graph2)

     for i in range(len(self.graph_data[graph1_index])):
        self.selected_colors[(graph1_index, i)] = color_hex
        self.selected_colors[(graph2_index, i)] = color_hex


   
     self.plot_all_signals(graph1, graph1_index)
     self.plot_all_signals(graph2, graph2_index)

    def zoom(self, graph, factor):
     view_box = graph.getViewBox()
     view_box.scaleBy((factor, factor))
     view_box.setAutoPan(True)
     if self.is_linked:
        other_graph = self.graph2 if graph == self.graph1 else self.graph1
        self.apply_linked_zoom(graph, other_graph, factor)
    def apply_linked_zoom(self,view_box1, view_box2 , factor):
     """Applies the zoom to both graphs if they are linked."""
     range1 = view_box1.viewRange()
    
    
     new_xrange = [range1[0][0] * factor, range1[0][1] * factor]
     new_yrange = [range1[1][0] * factor, range1[1][1] * factor]
    
    
     view_box2.setXRange(new_xrange[0], new_xrange[1], padding=0)
     view_box2.setYRange(new_yrange[0], new_yrange[1], padding=0)

    def toggle_visibility(self, graph):
     graph_index = self.get_graph_index(graph)
     if graph_index == -1:
        return

     if self.is_linked:
        other_graph_index = 1 if graph_index == 0 else 0
        self.sync_visibility(graph_index, other_graph_index)
     else:
        self.signal_visibility[graph_index] = not self.signal_visibility.get(graph_index, True)
        graph.clear()
        self.plot_all_signals(graph, graph_index)

     self.update_show_hide_button(graph)
    def sync_visibility(self, graph_index1, graph_index2):
     """Sync visibility for both linked graphs."""
     self.signal_visibility[graph_index1] = not self.signal_visibility.get(graph_index1, True)
     self.signal_visibility[graph_index2] = self.signal_visibility[graph_index1]
     self.graph1.clear()
     self.graph2.clear()
     self.plot_all_signals(self.graph1, graph_index1)
     self.plot_all_signals(self.graph2, graph_index2)  
     self.update_show_hide_button(self.graph1)
     self.update_show_hide_button(self.graph2)  


    def update_show_hide_button(self, graph):
     """Update the Show/Hide button text based on the visibility state."""
     graph_index = self.get_graph_index(graph)
     if graph_index == -1:
        return

     if graph_index == 0:
        button = self.findChild(QPushButton, "showHideBtn1")
     elif graph_index == 1:
        button = self.findChild(QPushButton, "showHideBtn2")
     elif graph_index == 2:
        button = self.findChild(QPushButton, "showHideBtn3")
     else:
        return

     if self.signal_visibility.get(graph_index, True):
        button.setText("Hide")
     else:
        button.setText("Show")
    def get_graph_index(self, graph):
     """Returns the index of the graph."""
     if graph == self.graph1:
        return 0
     elif graph == self.graph2:
        return 1
     elif graph == self.gluedGraph:
        return 2
     return -1
    def take_snapshot(self):
        # Specify the directory where the snapshots will be saved
        snapshot_dir = "snapshots"
        os.makedirs(snapshot_dir, exist_ok=True)  # Create the directory if it doesn't exist

        # Define the filename with date and time
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        snapshot_filename = os.path.join(snapshot_dir, f"snapshot_{timestamp}.png")

        # Access the "Glued Signals" graph
        glued_signals_plot = self.gluedGraph.plotItem  # Adjust this if necessary to get the correct graph

        # Take the snapshot
        exporter = pg.exporters.ImageExporter(glued_signals_plot)
        exporter.export(snapshot_filename)

        # Show success message
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setText("Snapshot saved successfully!")
        msg.setInformativeText(f"Saved to: {snapshot_filename}")
        msg.setWindowTitle("Snapshot Success")
        msg.exec_()

    def export_report(self):
        # Create the PDF file name based on the current date and time
        now = datetime.now()
        report_filename = f"reports/report_{now.strftime('%Y-%m-%d_%H-%M-%S')}.pdf"

        # Create a canvas object
        c = canvas.Canvas(report_filename, pagesize=letter)
        width, height = letter

        # Add images and text
        logo_height = 70  # height of the logo in the header
        c.drawImage("images/uni-logo.png", width - 150, height - logo_height - 40, width=100, height=logo_height)  # right side
        c.drawImage("images/sbme-logo.jpg", 50, height - logo_height - 40, width=100, height=logo_height)  # left side
        
        # Title in the middle
        c.setFont("Helvetica-Bold", 22)
        c.drawCentredString(width / 2, height - 90, "Biological Signal Report")

        # Take snapshot of "Glued Signals" graph
        snapshot_path = f"snapshots/snapshot_{now.strftime('%Y%m%d_%H%M%S')}.png"
        exporter = pg.exporters.ImageExporter(self.gluedGraph.plotItem)  # Adjust this to your actual reference
        exporter.export(snapshot_path)

        # Add the snapshot to the PDF
        snapshot_y_position = height - logo_height - 100  # Adjust this to place it below the title
        c.drawImage(snapshot_path, 50, snapshot_y_position - 200, width=500, height=200)  # Adjust positioning and size

        # Gather data from the gluedGraph (assuming it’s a PyQtGraph plot with data)
        # Extract the data from the graph for statistics calculation
        plot_data = self.gluedGraph.plotItem.listDataItems()[0].getData()  # Assuming the first data item
        y_data = plot_data[1]  # Get the y-values for statistics

        # Calculate statistics
        mean = np.mean(y_data)
        median = np.median(y_data)
        std_dev = np.std(y_data)
        min_val = np.min(y_data)
        max_val = np.max(y_data)

        # Create the table data
        table_data = [
            ['Statistic', 'Value'],
            ['Mean', f'{mean:.5f}'],
            ['Median', f'{median:.5f}'],
            ['Std_dev', f'{std_dev:.5f}'],
            ['Min', f'{min_val:.5f}'],
            ['Max', f'{max_val:.5f}'],
        ]

        # Create the table
        table = Table(table_data, colWidths=[200, 200])

        # Add style to the table
        style = TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.black),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ])
        table.setStyle(style)

        # Convert table into a canvas element
        table.wrapOn(c, width, height)
        table.drawOn(c, 103, snapshot_y_position - 370)  # Adjust positioning based on where you want the table


        # Finalize the PDF
        c.showPage()
        c.save()

        # Show success message
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setText("Report generated successfully!")
        msg.setInformativeText(f"Saved to: {report_filename}")
        msg.setWindowTitle("Report Success")
        msg.exec_()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    sys.exit(app.exec_()) 
import numpy as np
from PyQt5.QtWidgets import (QApplication, QWidget, QPushButton, QLabel,  
                             QVBoxLayout, QHBoxLayout, QSlider, QFileDialog, QColorDialog
)
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QPainter, QPen, QBrush

class CircularGraph(QWidget):
    def __init__(self,parent=None, zoom_level=1.0):
        super().__init__(parent)
        self.parent_instance = parent
        self.setMinimumSize(400, 400)
        self.data = None
        self.angle = 0
        self.circular_zoom_level = zoom_level
        self.pen_color = Qt.red  # Default pen color
        self.brush_color = Qt.red  # Default brush color

    def paintEvent(self, event):
        painter = QPainter(self)
        center_x, center_y = self.width() // 2, self.height() // 2
        radius = min(self.width(), self.height()) // 2 - 20

        painter.setBrush(QBrush(Qt.white, Qt.SolidPattern))
        painter.drawEllipse(center_x - radius, center_y - radius, 2 * radius, 2 * radius)

        pen = QPen(Qt.black, 4, Qt.SolidLine)
        painter.setPen(pen)
        painter.drawEllipse(center_x - radius, center_y - radius, 2 * radius, 2 * radius)

        painter.setPen(QPen(Qt.gray, 1, Qt.DotLine))
        decrement_radius = radius // 7
        for i in range(7):
            grid_radius = radius - decrement_radius * i
            painter.drawEllipse(center_x - grid_radius, center_y - grid_radius, 2 * grid_radius, 2 * grid_radius)

        num_radial_lines = 12
        for angle in np.linspace(0, 360, num_radial_lines, endpoint=False):
            x = center_x + radius * np.cos(np.radians(angle))
            y = center_y + radius * np.sin(np.radians(angle))
            painter.drawLine(center_x, center_y, int(x), int(y))

        if self.data is not None:
            angles = np.linspace(0, 2 * np.pi, len(self.data))
            previous_point = None
            current_index = np.argmax(angles >= self.angle) - 1
            current_index = max(current_index, 0)

            for idx, value in enumerate(self.data):
                if angles[idx] <= self.angle:
                    point_radius = value * self.circular_zoom_level
                       
                    x = point_radius * np.cos(angles[idx])
                    y = point_radius * np.sin(angles[idx])
                    painter.setBrush(QBrush(self.brush_color))
                    painter.drawEllipse(int(center_x + x) - 2, int(center_y + y) - 2, 4, 4)

                    if previous_point is not None:
                        painter.setPen(QPen(self.pen_color, 0.9))
                        painter.drawLine(previous_point[0], previous_point[1], int(center_x + x), int(center_y + y))

                    previous_point = (int(center_x + x), int(center_y + y))
                    if idx == current_index:
                        painter.setPen(QPen(Qt.black, 0.9))
                        painter.drawText(int(center_x + x) + 5, int(center_y + y) - 5, f"{value:.1f}")

    def update_graph(self):
        self.angle += np.pi / 90
        if self.angle >= 2 * np.pi:
            self.angle = 0
            if self.data is not None and  self.parent_instance:
                self.parent_instance.rewind()  # Call rewind method from parent (NonRectangleViewer)
        self.update()


class NonRectangleViewer(QWidget):
    def __init__(self):
        super().__init__()
                # Apply the global stylesheet to the entire application
        app = QApplication.instance()
        app.setStyleSheet("""
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
        self.setWindowTitle("Non-Rectangle Viewer")
        self.resize(1000, 600) 
        self.circular_zoom_level = 1.0 
        self.show_points = True  
        # Initialize flag for play/pause state
        self.flag = 0  
        
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)

        # Wrapper layout to center the circular graph
        graph_layout = QHBoxLayout()
        graph_layout.setAlignment(Qt.AlignCenter) 

        # Circular Graph
        self.circular_graph = CircularGraph()
        self.circular_graph.setFixedSize(600, 600) 
        graph_layout.addWidget(self.circular_graph)

        main_layout.addStretch()
        main_layout.addLayout(graph_layout)
        main_layout.addStretch()

        # Buttons and Controls Layout
        controls_layout = QHBoxLayout()
        controls_layout.setSpacing(10) 
        controls_layout.setAlignment(Qt.AlignCenter)  
        self.setup_controls(controls_layout)
        main_layout.addLayout(controls_layout)
        main_layout.addStretch()

        # Add margins for better appearance
        main_layout.setContentsMargins(20, 20, 20, 20)

        # Timer for cine mode
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.circular_graph.update_graph)

    def setup_controls(self, layout):
        self.add_button(layout, "Open", self.load_signal)
        self.play_pause_button = self.add_button(layout, "Play", self.toggle_play_pause) 
        self.add_button(layout, "Rewind", self.rewind)
        self.add_button(layout, "Color", self.change_color)
        self.add_button(layout, "Zoom In", self.zoom_in)
        self.add_button(layout, "Zoom Out", self.zoom_out)
        speed_layout = QVBoxLayout()
        speed_layout.setAlignment(Qt.AlignCenter)
    
        speed_label = QLabel("Cine Speed")
        speed_layout.addWidget(speed_label)
        speed_label.setFixedSize(100, 30) 
        self.speed_slider = QSlider(Qt.Horizontal)
        self.speed_slider.setFixedSize(300,30)
        self.speed_slider.setRange(1, 100)
        self.speed_slider.setValue(50)  
        self.speed_slider.valueChanged.connect(self.update_cine_speed)
        speed_layout.addWidget(self.speed_slider)
        layout.addLayout(speed_layout)

    def update_cine_speed(self):
        """Update the timer interval based on the slider value."""
        speed_value = self.speed_slider.value()
        
        # Set the timer interval based on the slider value
        new_interval = max(10, 200 - speed_value * 2)  
        self.timer.setInterval(new_interval)
    
    def add_button(self, layout, text, callback):
        """Helper method to create and add a button to the layout."""
        button = QPushButton(text)
        button.setFixedSize(80, 30)
        button.clicked.connect(callback)
        layout.addWidget(button)
        return button
    def load_signal(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Open File", "", "Text Files (*.txt);;All Files (*)")
        if file_name:
            self.circular_graph.data = np.loadtxt(file_name)
            self.circular_graph.angle = 0
        self.start_cine_mode()
        self.play_pause_button.setText("Pause")

    def toggle_play_pause(self):
        """Toggle between play and pause states."""
        if self.flag == 1:
            self.stop_cine_mode()
            self.play_pause_button.setText("Play")
        else:
            self.start_cine_mode()
            self.play_pause_button.setText("Pause")

    def zoom_in(self):
        self.circular_zoom_level *= 1.1  # Increase zoom level
        self.circular_graph.circular_zoom_level = self.circular_zoom_level 
        self.circular_graph.update() 

    def zoom_out(self):
        self.circular_zoom_level= max(1.0, self.circular_zoom_level / 1.1)  
        self.circular_graph.circular_zoom_level = self.circular_zoom_level 
        self.circular_graph.update()  
            

    def start_cine_mode(self):
        self.flag = 1
        if self.circular_graph.data is not None:
            self.timer.start(100)

    def stop_cine_mode(self):
        self.flag = 0
        self.timer.stop()

    def rewind(self):
        """Rewinds a single graph."""
        self.stop_cine_mode()
        self.circular_graph.angle = 0  
        self.circular_graph.update()  
        self.start_cine_mode()
    
    def change_color(self):
      color = QColorDialog.getColor()
      if color.isValid():
        self.circular_graph.pen_color = color
        self.circular_graph.brush_color = color
        self.circular_graph.update()
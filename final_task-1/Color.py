from PyQt5.QtWidgets import ( QPushButton, QHBoxLayout, QLineEdit, QDialog,
                             QColorDialog, QFormLayout
)

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
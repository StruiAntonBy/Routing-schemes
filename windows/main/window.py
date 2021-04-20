from PyQt5.QtWidgets import QWidget, QPushButton, QVBoxLayout, QApplication
from PyQt5.QtCore import pyqtSignal, Qt
from config import APP_NAME
from windows.main.config import *


class MainWindow(QWidget):
    switch_window = pyqtSignal(str)

    def __init__(self, parent=None):
        QWidget.__init__(self, parent, Qt.MSWindowsFixedSizeDialogHint)
        self.setWindowTitle(APP_NAME)
        self.resize(*GEOMETRY)
        desktop = QApplication.desktop()
        self.move((desktop.width() - self.width()) // 2, (desktop.height() - self.height()) // 2)

        btn_generate_diagram = QPushButton(NAME_BTN)
        btn_generate_diagram.clicked.connect(self.generate_diagram)

        vbox = QVBoxLayout()
        vbox.addWidget(btn_generate_diagram)
        self.setLayout(vbox)

    def generate_diagram(self):
        self.switch_window.emit("main>generate_diagram")

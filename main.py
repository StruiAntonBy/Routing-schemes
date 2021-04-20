import sys
import resources

from controller import Controller
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QIcon
from config import *


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon(ICON))
    controller = Controller()
    controller.select_forms("main")
    sys.exit(app.exec_())

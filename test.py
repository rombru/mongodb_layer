import sys

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QApplication, QMainWindow)

from core import async_utils
from core.mongodb_layer_dockwidget import MongoDBLayerDockWidget


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.loop = async_utils.create_loop()
        self.resize(400, 600)
        self.addDockWidget(Qt.RightDockWidgetArea, MongoDBLayerDockWidget(self.loop))


if __name__ == '__main__':
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    sys.exit(app.exec_())

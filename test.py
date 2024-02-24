import sys

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QApplication, QMainWindow)

from core.mongodb_layer_dockwidget import MongoDBLayerDockWidget


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.resize(400, 600)
        self.addDockWidget(Qt.RightDockWidgetArea, MongoDBLayerDockWidget())


if __name__ == '__main__':
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    sys.exit(app.exec_())

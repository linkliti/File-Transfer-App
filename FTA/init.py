from PyQt5 import uic, QtGui
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt

import sys
from pkg_resources import resource_filename
from threading import Thread

from FTA import server, client
import time


def file(path):
    """Get file from package"""
    return (resource_filename('FTA', path))


def text_mode(args) -> None:
    """Text mode"""
    try:
        if args['--server']:
            print("Press CTRL+C to exit")
            server_thread = Thread(target=server.main)
            server_thread.daemon = True
            server_thread.start()
            while True:
                time.sleep(100)
        else:
            client.main(2121)
    except (KeyboardInterrupt, SystemExit):
        print("Detected CTRL+C")
        sys.exit()


def window_mode() -> None:
    """Show Graphical user interface"""
    class MainWindow(QMainWindow):
        """Main window class"""

        def __init__(self):
            super().__init__()
            #uic.loadUi(pkg_file('FTA', 'style/mainwindow.ui'), self)
            uic.loadUi(file('style/mainwindow.ui'), self)
            #self.setWindowIcon(QtGui.QIcon(pkg_file('FTA', 'style/icon.svg')))

            # self.pushButton.clicked.connect(print("hello"))

    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec()

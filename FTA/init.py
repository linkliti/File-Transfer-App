from PyQt5 import uic, QtGui
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt
import sys
from pkg_resources import resource_filename as pkg_file


def button_hello():
    """
    Действие при нажатии на кнопку
    """
    print("Hello World!")


def window_mode():
    """
    Графическое отображение программы
    """
    class MainWindow(QMainWindow):
        """
        Класс главного окна программы
        """

        def __init__(self):
            super().__init__()
            #uic.loadUi(pkg_file('FTA', 'style/mainwindow.ui'), self)
            uic.loadUi(pkg_file('FTA', 'style/mainwindow.ui'), self)
            #self.setWindowIcon(QtGui.QIcon(pkg_file('FTA', 'style/icon.svg')))

            self.pushButton.clicked.connect(button_hello)

    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec()


def text_mode():
    """
    Текстовое отображение программы
    """
    print("Hello World!")

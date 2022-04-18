"""File Transfer App
Usage:
    FTA [-t=TYPE]
    FTA -h | --help

Options:
    -h --help           Show this screen
    -t=<gui|text>       Change type [default: gui]
"""

from PySide6.QtWidgets import *  # temp import all
from PySide6.QtCore import Qt
import sys
import docopt


def window():
    class MainWindow(QMainWindow):
        def __init__(self):
            super().__init__()
            self.setWindowTitle("My App")
            self.setFixedWidth(500)
            self.setFixedHeight(500)

            self.text = QLabel("Hello World!", self)
            self.text.setAlignment(Qt.AlignCenter)
            self.text.setStyleSheet("""
                QLabel {
                    color: black;
                    font-size: 50px;
                    }
                """)
            self.setCentralWidget(self.text)

    app = QApplication()
    window = MainWindow()
    window.show()
    app.exec()


def hello_world():
    print("Hello World!")


def main():
    args = docopt.docopt(__doc__)
    mode = args['-t']
    if mode == 'text':
        hello_world()
    elif mode == 'gui':
        window()


if __name__ == '__main__':
    main()

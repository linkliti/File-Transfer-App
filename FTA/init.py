from PyQt5 import uic, QtGui
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt

import sys

from threading import Thread
import socket

from FTA.server import server, send
from FTA.client import listen, scan
from FTA.util import get_ip, make_pass, pkgfile
from time import sleep


class UserData():
    def __init__(self, args):
        """
        Метод инициализации

            ip          - IP адрес хоста
            port        - Используемый порт
            hostname    - Имя хоста

            Сервер:
            is_random   - Флаг незаданных данных пользователя
            user        - Пользователь
            pwd         - Пароль FTP сервера
            path        - Путь (для сервера)
            write       - Разрешение на запись

            Клиент:
            target_ip   - Целевые IP адреса
            path_save   - Путь сохранения файлов
        """
        self.ip = get_ip()
        self.port = args['--port']
        self.hostname = socket.gethostname()
        # Сервер
        self.is_random = False if (
            args['--user'] and args['--pwd']) else True
        self.user = args['--user'] or 'fta_server'
        self.pwd = args['--pwd'] or make_pass()
        self.path = args['<path>'] or '.'
        self.write = args['--write']
        # Клиент
        self.target_ip = args['<target>']
        self.save = args['<path_save>']


def text_mode(args) -> None:
    """Консольный режим работы"""
    try:
        session = UserData(args)
        # Режим работы
        if args['listen']:
            func = listen
        elif args['scan']:
            func = scan
        elif args['send']:
            func = send
        elif args['server']:
            func = server
        # Запуск основного процесса
        thread = Thread(target=func, args=(session,))
        thread.daemon = True
        thread.start()
        # Не завершать работу программы
        while thread.is_alive():
            sleep(1)
    except (KeyboardInterrupt, SystemExit):
        print("Выход из программы")
        sys.exit()


def window_mode() -> None:
    """Графический режим работы"""
    class MainWindow(QMainWindow):
        """Класс графического интерфейса"""
        def hello():
            print("hello")

        def __init__(self):
            super().__init__()
            uic.loadUi(pkgfile('style/mainwindow.ui'), self)
            self.setWindowIcon(QtGui.QIcon(pkgfile('style/icon.svg')))
            self.pushButton.clicked.connect(MainWindow.hello)

    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec()


if __name__ == '__main__':
    print('Используйте "python -m FTA"')

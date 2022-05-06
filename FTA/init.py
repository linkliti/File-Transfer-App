import os
import socket
import sys
from threading import Thread
from time import sleep

from PyQt5 import QtGui, uic
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import *

from FTA.client import listen, scan
from FTA.server import send, server
from FTA.util import get_ip, homedir, pkgfile


class UserData():
    def __init__(self, args):
        """
        Метод инициализации

        ip              - IP адрес текущего ПК
        port            - Используемый порт
        hostname        - Имя текущего ПК

        Сервер:
        is_random       - Флаг незаданного пароля
        user            - Пользователь ('fta_server')
        pwd             - Пароль FTP сервера
        file_targets    - Целевые папки, файлы
        write           - Разрешение на изменение файлов

        Клиент:
        target_ip       - Целевые IP адреса
        save_path       - Путь сохранения файлов
        """
        self.ip = get_ip()
        self.port = int(args['--port'])
        self.hostname = socket.gethostname()

        # Сервер
        self.is_random = False
        self.user = 'fta_server'
        self.pwd = args['--pwd'] or None
        self.file_targets = args['<files>'] if args['<files>'] else ['.']
        self.write = bool(args['--write'])

        # Клиент
        self.auto_accept = bool(args['--auto-accept'])
        self.target_ip = args['<target_ip>']
        self.save_path = args['<save_path>'] if args['<save_path>'] \
            else './fta_received'


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

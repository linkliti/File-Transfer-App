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
from FTA.util import clear_folder, get_ip, homedir, pkgfile, is_ip


class UserData():
    """ Класс данных пользователя \n
        \n |ip              - IP адрес текущего ПК
        \n |port            - Используемый порт
        \n |hostname        - Имя текущего ПК

        \n Сервер:
        \n |use_cert        - Использование сертификата для TLS
        \n |is_random       - Флаг незаданного пароля
        \n |user            - Пользователь ('fta_server')
        \n |pwd             - Пароль FTP сервера
        \n |file_targets    - Целевые папки, файлы
        \n |write           - Разрешение на изменение файлов

        \n Клиент:
        \n |target_ip       - Целевые IP адреса
        \n |save_path       - Путь сохранения файлов
    """

    def __init__(self, args):
        self.ip = args['--ip'] if is_ip(args['--ip']) == 4 else get_ip()
        self.port = int(args['--port'] or 2121)
        self.hostname = socket.gethostname()

        # Сервер
        self.use_cert = not args['--no_cert'] and True
        self.is_random = False
        self.user = 'fta_server'
        self.pwd = args['--pwd'] or None
        self.is_legacy = bool(args['legacy'])
        if self.is_legacy:
            self.file_targets = args['<folder>'] if args['<folder>'] \
                else '.'
        else:
            self.file_targets = args['<files>'] if args['<files>'] else ['.']
        self.write = bool(args['--write'])
        self.server_dir = ''

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
        raise SystemExit
    except (KeyboardInterrupt, SystemExit):
        print("Выход из программы")
        if session.server_dir:
            clear_folder(session.server_dir, safe_flag=True)
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

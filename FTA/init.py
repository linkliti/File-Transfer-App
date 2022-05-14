import socket
import sys

from FTA.client import listen, scan
from FTA.gui import MainWindow
from FTA.server import send, server
from FTA.util import Thread_Process, clear_folder, get_ip, is_ip, sleep


class UserData():
    """ Класс данных пользователя \n
        \n |is_gui          - Флаг графического интерфейса
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
        self.is_gui = False
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
            self.file_targets = args['<files>'] if args['<files>'] else []
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
        # Общий UserData между независ. процессами
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
        thread = Thread_Process(session, func)
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


def window_mode(DEFAULT_ARG) -> None:
    """Графический режим работы"""
    try:
        from PyQt5.QtWidgets import QApplication
        app = QApplication(sys.argv)
        # Общий UserData между независ. процессами
        session = UserData(DEFAULT_ARG)
        window = MainWindow(session)
        window.show()
        app.exec()
        raise SystemExit
    except (KeyboardInterrupt, SystemExit):
        if session.server_dir:
            clear_folder(session.server_dir, safe_flag=True)
        sys.exit()


if __name__ == '__main__':
    print('Используйте "python -m FTA"')

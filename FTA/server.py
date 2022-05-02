import json
import logging
import os
import socket
import sys
from inspect import ismethod

from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import FTPHandler
from pyftpdlib.log import config_logging
from pyftpdlib.servers import FTPServer

from FTA.__init__ import __version__
from FTA.util import (abs_path, clear_folder, copy_handler, drive, hlink,
                      is_ip, parse_folder)


def server(s) -> None:
    """Функция запуска сервера"""
    serv = ServerData(s)
    hardlink_gen(serv.server_dir, serv.files_data)
    if len(serv.files_data) == 0:
        print('Нет файлов для отправки')
        return
    # Сервер
    run_server(s.ip, s.port, s.pwd, serv.server_dir, False,
               s.write, s.user, s.is_random)


class MyFTPHandler(FTPHandler):
    # Выход по завершению соединения
    def on_disconnect(self):
        self.server.close_all()


def run_server(ip, port, pwd, server_dir, is_send=False,
        write_perm=False, user='fta_server', is_random=True):
    """FTP Сервер"""
    # Отключить лог
    config_logging(level=logging.ERROR)
    # Авторизация
    authorizer = DummyAuthorizer()
    # Пользователь
    rule = 'elrawMT' if write_perm else 'elr'  # Разрешение на изменение файлов
    authorizer.add_user(user, pwd, server_dir, rule)
    # Обработчик
    handler = MyFTPHandler if is_send else FTPHandler
    handler.authorizer = authorizer
    # Баннер при подключении
    handler.banner = "FTA Server"
    # FTP Сервер
    server = FTPServer((ip, port), handler)
    # Лимит подключений
    conn_lim = 2 if is_send else 5
    server.max_cons = conn_lim
    server.max_cons_per_ip = conn_lim
    server.max_login_attempts = conn_lim
    # Лог логина и пароля если случайные
    if is_random:
        print(f"Данные для входа: {user} {pwd}")
    # Старт
    print("Сервер запущен")
    server.serve_forever()
    print("Сервер выключен")


class ServerData():
    """ Класс информации о сервере"""

    def __init__(self, s):
        """
        Метод инициализации
        server_dir      - Папка FTP сервера
        files_data      - Пути файлов [имя на сервере, абс путь]
        """
        self.server_dir = ''
        self.files_data = []
        self.FTA_version = str(__version__)
        # Парсировка file_targets
        self.files_parse(s.file_targets)

    def files_parse(self, file_targets):
        """ Обработка файлов и файлов в папках"""
        try:
            # Обработка файлов и файлов в папках
            for entry in file_targets:

                # Если папка
                if os.path.isdir(entry):
                    # Обработка всех файлов полученных от parse_folder
                    for entry_file in parse_folder(entry):
                        self.inspect_file(entry_file, entry)

                # Иначе если файл
                elif os.path.isfile(entry):
                    self.inspect_file(abs_path(entry))

        except OSError as e:
            print(f"Ошибка", type(e).__name__, '-', e)

    def inspect_file(self, file_path, folder=None) -> None:
        """ Обработка отправляемого файла """
        # Файл уже добавлен или его не существует
        if file_path in (self.files_data[i][1]
                         for i in range(len(self.files_data))
                         ) or not os.path.exists(file_path):
            return

        # Используемый диск
        file_disk = drive(file_path)

        # Диск не выбран
        if self.server_dir == '':
            self.server_dir = file_disk + '/.fta_shared'
        # Разные диски
        elif file_disk != drive(self.server_dir):
            print(f'Невозможно добавить {file_path}', end=' - ')
            print(f'Файл находится на другом диске')
            return

        # Имя и местоположение файла на сервере
        ftp_path = ''
        if folder:
            ftp_path = os.path.basename(
                abs_path(folder)) + file_path[len(abs_path(folder)):]
        else:
            ftp_path = os.path.basename(file_path)

        # Проверка совпадений названий
        while ftp_path in (self.files_data[i][0] for i in range(len(self.files_data))):
            ftp_path = copy_handler(ftp_path)

        # Сохранить полный, короткие пути и диск
        self.files_data.append((ftp_path, file_path))


class RequestData(ServerData):
    """ Класс отправляемой информации"""

    def __init__(self, s):
        """
        FTA_version         - Версия программы
        hostname            - Имя текущего ПК
        ip                  - IP текущего ПК
        port                - Используемый порт для FTP

        files_list_size     - Размер списка отправляемых файлов
        files_size          - Размер отправляемых файлов
        files_count         - Кол-во отправляемых файлов

        Отправляемый отдельно список файлов:
        sendable_filelist   - Отправляемые файлы [имя, размер файла]
        """
        ServerData.__init__(self, s)
        self.hostname = s.hostname
        self.ip = s.ip
        self.port = s.port
        self.user = s.user

        self.files_list_size = 0
        self.files_size = 0
        self.files_count = 0

        self.sendable_filelist = {}

    def gen_msgs(self):
        ''' Создание отправляемой информации '''
        # Создание списка файлов
        self.make_sendable_filelist()
        self.files_list_size = sys.getsizeof(self.sendable_filelist.encode())
        # Преобразовывание всех полей в JSON
        return json.dumps(dict((name, getattr(self, name))
                               for name in dir(self)
                               if not name.startswith('__')
                               and not name in ('server_dir',
                                                'files_data',
                                                'sendable_filelist')
                               and not ismethod(getattr(self, name))))

    def make_sendable_filelist(self):
        ''' Создание списка файлов (вызывается в gen_msgs) '''
        for entry in self.files_data:
            # Размер файла
            size = os.path.getsize(entry[1])
            self.files_size += size
            self.files_count += 1
            temp = {entry[0]: size}
            self.sendable_filelist = {**self.sendable_filelist, **temp}
        self.sendable_filelist = json.dumps(self.sendable_filelist)


def send(s) -> None:
    """ Отправка запроса на передачу файлов """
    # Отправляемая информация
    req = RequestData(s)
    req_json = req.gen_msgs().encode()
    if len(req.files_data) == 0:
        print('Нет файлов для отправки')
        return
    hardlink_gen(req.server_dir, req.files_data)

    # Подключение
    ClientSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ClientSock.connect((s.target_ip[0], s.port))

    # Отправка запроса
    ClientSock.send(req_json)
    if not ClientSock.recv(40).decode() == 'conf':
        print('Нет подтверждения')
        return 1

    # Отправка списка файлов
    ClientSock.send((req.sendable_filelist).encode())

    # Получение ответа
    data = ClientSock.recv(128)
    resp = json.loads(data.decode())

    # Согласие
    if is_ip(resp['confirm']) == 4:
        print("Получено согласие")
        ClientSock.close()
        # Старт сервер
        run_server(resp['confirm'], s.port, s.pwd, req.server_dir,
                   True, is_random=True)
        return 0

    # Отказ
    elif resp['confirm'] == False:
        print("Получен отказ")
        return 1
    else:
        print('Соединение потеряно')
        return 1


def hardlink_gen(server_dir, files_data):
    """ Создание ссылок для папки FTP сервера """
    # Очистка папки сервера
    if os.path.exists(server_dir):
        clear_folder(server_dir, safe_flag=True)
    # Создание ссылок
    for entry in files_data:
        try:
            link_path = os.path.split(server_dir + '/' + entry[0])[0]
            if not os.path.exists(link_path):
                os.makedirs(link_path)
            # Связь
            hlink(entry[1], server_dir + '/' + entry[0])
        except PermissionError as e:
            print('Невозможно передать', entry[1], end = ' - ')
            print(e)
            files_data.remove(entry)


if __name__ == '__main__':
    print('Используйте "python -m FTA"')

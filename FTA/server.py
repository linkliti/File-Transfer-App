import json
import logging
import os
import socket
import sys
from inspect import ismethod

from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import TLS_FTPHandler
from pyftpdlib.log import config_logging
from pyftpdlib.servers import FTPServer

from FTA.__init__ import __version__
from FTA.client import scanner
from FTA.util import (abs_path, clear_folder, copy_handler, drive, hlink,
                      is_fat32_or_ronly, is_ip, make_pass, parse_folder,
                      pkgfile)


def server(s) -> None:
    """Функция запуска сервера"""
    serv = ServerData(s)
    if len(serv.files_data) == 0:
        print('Нет файлов для отправки')
        return
    # Очистка папки
    if s.server_dir and not s.is_legacy:
        clear_folder(s.server_dir, safe_flag=True)
    # Создание ссылок и выход при неудаче
    if serv.hardlink() == -1:
        return
    # Пароль
    if not s.pwd:
        s.pwd = make_pass()
        s.is_random = True
    # Сервер
    print(f'IP адрес: {s.ip}:{s.port}')
    server_process(ip=s.ip, port=s.port, pwd=s.pwd,
                   server_dir=serv.server_dir,
                   is_send=False, write_perm=s.write,
                   user=s.user,
                   is_random=s.is_random, hostname=s.hostname,
                   use_cert=s.use_cert)


def server_process(ip, port, pwd, server_dir, is_send=False,
                   write_perm=False, user='fta_server',
                   is_random=True, hostname='', use_cert=True):
    """ Процесс сервера """
    # Отключить лог для передачи файлов
    if is_send:
        config_logging(level=logging.ERROR)
    # Авторизация
    authorizer = DummyAuthorizer()
    # Пользователь
    rule = 'elrawMT' if write_perm else 'elr'  # Разрешение на  изменение файлов
    authorizer.add_user(user, pwd, server_dir, rule)
    # Обработчик
    handler = MyTLS_FTPHandler if is_send else TLS_FTPHandler
    handler.certfile = pkgfile('cert/demo_keycert.pem')
    if use_cert:
        handler.tls_control_required = True
        handler.tls_data_required = True
    else:
        print("[!] Возможно незашифрованное подключение")
    handler.authorizer = authorizer
    # Баннер при подключении
    handler.banner = "FTA_Send_Server" if is_send else f'FTA_Server {hostname}'
    # FTP Сервер
    try:
        server = FTPServer((ip, port), handler)
    except OSError as e:
        print("Недопустимый IP:", type(e).__name__, '-', e)
        return
    # Лимит подключений
    conn_lim = 2 if is_send else 5
    server.max_cons = conn_lim
    server.max_cons_per_ip = conn_lim
    server.max_login_attempts = 3
    # Старт
    server.serve_forever()


class MyTLS_FTPHandler(TLS_FTPHandler):
    """ Обработчик: Выход по завершению соединения """

    def on_disconnect(self):
        """ Функция вызываемая при отключении клиента """
        self.server.close_all()


class ServerData():
    """ Класс информации о сервере \n
    \n |is_legacy       - Флаг режима совместимости
    \n |server_dir      - Папка FTP сервера
    \n |files_data      - Пути файлов [имя на сервере, абсолютный путь]
    \n |FTA_version     - Версия программы
    """

    def __init__(self, s):
        self.is_legacy = s.is_legacy
        self.server_dir = ''
        self.files_data = []
        self.FTA_version = str(__version__)
        # Если не папка и режим совместимости
        if self.is_legacy and not os.path.isdir(s.file_targets):
            print("В режиме совместимости возможно передавать только папку")
            return
        # Режим совместимости
        if self.is_legacy:
            self.server_dir = s.file_targets
            self.files_parse([s.file_targets])
        # Обычный режим
        else:
            # Парсировка file_targets
            self.files_parse(s.file_targets)
            # Временная папка
            self.server_dir = self.server_dir + '/.fta_shared'
            s.server_dir = self.server_dir

    def __del__(self):
        if self.server_dir.endswith('/.fta_shared'):
            clear_folder(self.server_dir, safe_flag=True)

    def files_parse(self, file_targets):
        """ Обработка файлов и файлов в папках"""
        try:
            # Обработка файлов и файлов в папках
            for entry in file_targets:

                # Если папка
                if os.path.isdir(entry):
                    # Обработка всех файлов полученных от parse_folder
                    for entry_file in parse_folder(entry)[1]:
                        self.inspect_file(entry_file, entry)

                # Иначе если файл
                elif os.path.isfile(entry):
                    self.inspect_file(abs_path(entry))

        except OSError as e:
            print(f"Ошибка:", type(e).__name__, '-', e)

    def inspect_file(self, file_path, folder=None) -> None:
        """ Обработка отправляемого файла """
        # Файл уже добавлен или его не существует
        if file_path in (self.files_data[i][1]
                         for i in range(len(self.files_data))
                         ) or not os.path.exists(file_path):
            return

        # Используемый диск
        if not self.is_legacy:
            temp = drive(file_path, self.server_dir)
            if temp == False:
                print(f'Невозможно добавить {file_path}', end=' - ')
                print(f'Файл находится на другом диске')
                return
            else:
                self.server_dir = temp

        # Имя и местоположение файла на сервере
        ftp_path = ''
        if folder:
            ftp_path = os.path.basename(
                abs_path(folder)) + file_path[len(abs_path(folder)):]
        else:
            ftp_path = os.path.basename(file_path)

        # Проверка совпадений названий
        while ftp_path in (self.files_data[i][0]
                           for i in range(len(self.files_data))):
            ftp_path = copy_handler(ftp_path)

        # Сохранить полный, короткие пути и диск
        self.files_data.append((ftp_path, file_path))

    def hardlink(self) -> int:
        """
        Проверка диска на FAT32 и режим чтения
        Пропуск если включен режим совместимости
        """
        if not self.is_legacy:
            if is_fat32_or_ronly(self.server_dir.rstrip('/.fta_shared')):
                print("Неподдерживаемый диск. Используйте режим совместимости")
                return -1
            hardlink_gen(self.server_dir, self.files_data)
        return 0


class RequestData(ServerData):
    """ Класс отправляемой информации \n
    \n |hostname            - Имя текущего ПК
    \n |ip                  - IP текущего ПК
    \n |port                - Используемый порт для FTP
    \n |user                - Имя пользователя
    \n |files_list_size     - Размер списка отправляемых файлов
    \n |files_size          - Размер отправляемых файлов
    \n |files_count         - Кол-во отправляемых файлов

    \n Отправляемый отдельно список файлов:
    \n |sendable_filelist   - Отправляемые файлы [имя, размер файла]"""

    def __init__(self, s):
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
    # Автоматический режим
    if s.target_ip == ['']:
        s.target_ip = ['auto']
    # Выбор IP
    if len(s.target_ip) == 1 and is_ip(s.target_ip[0]) == 4:
        target = s.target_ip[0]
    else:
        l = scanner(s.target_ip, s.port)
        if len(l):
            while True:
                try:
                    if s.is_gui:
                        print("[!] Требуется подтверждение в консоли")
                    print('Введите индекс: ', end='')
                    index = int(input())
                    if index == 0:
                        print('Отмена')
                        return
                    elif index > 0 and index <= len(l) \
                            and l[index-1][3] == 'FTA прослушиватель':
                        target = (l[index-1][1]).split(':')[0]
                        break
                except TypeError:
                    pass
                print('Неверный индекс')
        else:
            return
    # Отправляемая информация
    req = RequestData(s)
    req_json = req.gen_msgs().encode()
    if len(req.files_data) == 0:
        print('Нет файлов для отправки')
        return 1
    # Очистка папки
    if s.server_dir and not s.is_legacy:
        clear_folder(s.server_dir, safe_flag=True)
    if req.hardlink() == -1:
        return -1

    # Подключение
    ClientSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print("Подключение...")
    try:
        ClientSock.connect((target, s.port))
    except TimeoutError as e:
        print('Ошибка подключения:', type(e).__name__, '-', e)
        return -1
    except ConnectionRefusedError:
        print(f'Ошибка подключения к {target}:{s.port}')
        return -1
    ClientSock.settimeout(3600)
    try:
        # Получение статуса клиента
        msg = ClientSock.recv(50).decode()
        if not 'FTA_Listen' in msg:
            print('Клиент не в режиме прослушивания')
            return 1

        # Отправка запроса
        ClientSock.send(req_json)
        if not ClientSock.recv(50).decode() == 'FTA_conf':
            print('Нет подтверждения получения информации')
            return -1

        # Отправка списка файлов
        ClientSock.send((req.sendable_filelist).encode())
        print("Ожидание клиента")

        # Получение ответа
        data = ClientSock.recv(128)
        resp = json.loads(data.decode())

        # Согласие
        if is_ip(resp['confirm']) == 4:
            print("Получено согласие")
            ClientSock.close()
            # Старт сервера
            # Пароль
            if not s.pwd:
                s.pwd = make_pass()
                s.is_random = True
            server_process(ip=resp['confirm'], port=s.port, pwd=s.pwd,
                           server_dir=req.server_dir,
                           is_send=True, write_perm=False, is_random=s.is_random,
                           use_cert=True)
            return 0

        # Отказ
        elif resp['confirm'] == False:
            print("Отключение: Получен отказ")
            ClientSock.close()
            return 1
        else:
            print('Соединение потеряно')
            return -1
    except json.decoder.JSONDecodeError:
        print('Соединение потеряно')
        return -1
    except ConnectionResetError as e:
        print('Соединение потеряно:', type(e).__name__, '-', e)
        return -1


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
            print('Невозможно передать', entry[1], end=' - ')
            print(e)
            files_data.remove(entry)


if __name__ == '__main__':
    print('Используйте "python -m FTA"')

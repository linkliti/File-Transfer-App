from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import FTPHandler
from pyftpdlib.servers import FTPServer
import socket
import json
import os
import sys
from inspect import ismethod
from FTA.__init__ import __version__
from FTA.util import parse_folder, abs_path, copy_handler


def server(s) -> None:
    """FTP Сервер"""
    # Авторизация
    authorizer = DummyAuthorizer()

    # Пользователь
    rule = 'elradfmwMT' if s.write else 'elr'
    authorizer.add_user(s.user, s.pwd, s.files[0], rule)

    # Обработчик
    handler = FTPHandler
    handler.authorizer = authorizer

    # Баннер при подключении
    handler.banner = "FTA Server"

    # FTP Сервер
    server = FTPServer((s.ip, s.port), handler)

    # Лимит подключений
    server.max_cons = 5
    server.max_cons_per_ip = 5

    # Лог логина и пароля если случайные
    if s.is_random:
        print(f"Данные для входа: {s.user} {s.pwd}")

    # Старт
    server.serve_forever()


class RequestData():
    """ Класс отправляемой информации"""

    def __init__(self, s):
        """
        Метод инициализации
        __files_data    - Абсолютные пути файлов [абс путь, имя на сервере]
        FTA_version     - Версия программы
        hostname        - Имя текущего ПК
        ip              - IP текущего ПК
        port            - Используемый порт для FTP

        files_list_size  - Размер списка отправляемых файлов
        files_size      - Размер отправляемых файлов
        files_count     - Кол-во отправляемых файлов
        files           - Отправляемые файлы [имя на сервере, размер в байтах]
        user            - Имя пользователя FTP сервера
        """
        self.__files_data = []
        self.FTA_version = str(__version__)
        self.hostname = s.hostname
        self.ip = s.ip
        self.port = s.port
        self.user = s.user

        self.files_list_size = 0
        self.files_size = 0
        self.files_count = 0
        self.files = []
        self.files_parse(s.files)

    def gen_form(self):
        # Преобразовывание всех полей в JSON
        return json.dumps(dict((name, getattr(self, name))
                               for name in dir(self)
                               if not name.startswith('__')
                               and not name.startswith('_RequestData__')
                               and not name == 'files'
                               and not ismethod(getattr(self, name))))

    def inspect_file(self, file_path, folder=None) -> list or None:
        # Обработка отправляемого файла
        # Файл уже добавлен или не существует
        if (file_path in self.__files_data) or not os.path.exists(file_path):
            return None

        # Сохранить полный путь
        self.__files_data.append(file_path)

        # Имя и местоположение файла на сервере
        if folder:
            ftp_path = os.path.basename(
                folder) + file_path[len(abs_path(folder)):]
        else:
            ftp_path = os.path.basename(file_path)

        # Проверка совпадений названий
        while ftp_path in (self.files[i][0] for i in range(len(self.files))):
            ftp_path = copy_handler(ftp_path)

        # Размер файла
        size = os.path.getsize(file_path)
        self.files_size += size
        self.files_count += 1

        # Сохранение информации
        self.files.append([ftp_path, size])

    def files_parse(self, files):
        # Генерация списка отправляемых файлов
        for entry in files:
            try:
                # Папка
                if os.path.isdir(entry):
                    for entry_file in parse_folder(entry):
                        self.inspect_file(entry_file, entry)
                # Файл
                elif os.path.isfile(entry):
                    self.inspect_file(abs_path(entry))
            except OSError as e:
                print(f"Ошибка обработки {entry}: {e}")


def send(s) -> None:
    """ Отправка запроса на передачу файлов
    и запуск временного FTP сервера """
    # Отправляемая информация
    req = RequestData(s)

    # Отправляемый словарь файлов
    files_dict = {}
    for file in req.files:
        # Имя и размер файла
        entry = {file[0]: file[1]}
        files_dict = {**files_dict, **entry}

    # Флаг конца передачи
    entry = {'end': ''}
    files_dict = {**files_dict, **entry}

    # Размер словаря отправляемых файлов
    files_json = json.dumps(files_dict).encode()
    req.files_list_size = sys.getsizeof(files_json)

    # Подключение
    ClientSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ClientSock.connect((s.target_ip[0], s.port))

    # Отправка запроса
    ClientSock.send(req.gen_form().encode())
    if not ClientSock.recv(37).decode() == 'conf':
        print('Нет подтверждения')
        return 1

    # Отправка списка файлов
    ClientSock.send(json.dumps(files_dict).encode())

    # Получение ответа
    data = ClientSock.recv(55)
    resp = json.loads(data.decode())
    if resp['confirm'] == True:
        print("Согласие")
        return 0
    elif resp['confirm'] == False:
        print("Отказ")
        return 1
    else:
        print('Нет подтверждения')
        return 1


if __name__ == '__main__':
    print('Используйте "python -m FTA"')

from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import FTPHandler
from pyftpdlib.servers import FTPServer
import socket
import json
from inspect import ismethod
from FTA.__init__ import __version__


def server(s) -> None:
    """FTP Сервер"""
    # Авторизация
    authorizer = DummyAuthorizer()
    # Пользователь
    rule = 'elradfmwMT' if s.write else 'elr'
    authorizer.add_user(s.user, s.pwd, s.path, rule)
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
        FTA_version     - Версия программы
        hostname        - Имя текущего ПК
        """
        self.FTA_version = str(__version__)
        self.hostname = s.hostname

    def send_form(self):
        # Преобразовывание всех полей в JSON
        return json.dumps(dict((name, getattr(self, name))
                               for name in dir(self)
                               if not name.startswith('__')
                               and not ismethod(getattr(self, name))))


def send(s) -> None:
    """ Отправка запроса на передачу файлов
    и запуск временного FTP сервера """
    # Отправляемая информация
    req = RequestData(s).send_form()
    # Подключение
    ClientSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ClientSock.connect((s.target_ip, s.port))
    # Отправка
    ClientSock.send(req.encode())
    # Получение ответа
    data = ClientSock.recv(1024)
    resp = json.loads(data.decode())
    print(resp)
    if resp['confirm'] == True:
        print("Согласие")
        return 0
    else:
        print("Отказ")
        return 1


if __name__ == '__main__':
    print('Используйте "python -m FTA"')

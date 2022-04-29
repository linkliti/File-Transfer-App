import os
import sys
from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import FTPHandler
from pyftpdlib.servers import FTPServer
import socket


def server(s):
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


def send(s):
    pass


if __name__ == '__main__':
    print('Используйте "python -m FTA"')

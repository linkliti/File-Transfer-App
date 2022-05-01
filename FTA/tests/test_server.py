import pytest
import os
import sys
from FTA import client, server, init, util
from threading import Thread
from FTA.__main__ import DEFAULT_ARG
from FTA.tests.test_FTA import udata, files


def test_server_run(udata):
    # Тестовый запуск сервера
    from time import sleep
    thread = Thread(target=server.server, args=(udata,))
    thread.daemon = True
    thread.start()
    print("Starting server for 3 seconds")
    sleep(3)
    print("Done")


def test_req_data(udata, files):
    # Проверка отправляемых данных (дебаг)
    udata.files = [
        './test_files/b.txt',
        './test_files/3.txt',
        './test_files/subfolder',
        './test_files/subfolder2/3.txt',
    ]
    req = server.RequestData(udata)
    print()
    print('Files:')
    for entry in req.files:
        print(entry)
    print('Data:')
    data = req.gen_form()
    print(f'Unencoded Size {sys.getsizeof(data)} bytes')
    print(f'Encoded Size {sys.getsizeof(data.encode())} bytes')
    print(data)

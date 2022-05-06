import json
import os
import sys
from threading import Thread

import pytest
from FTA import client, init, server, util
from FTA.__main__ import DEFAULT_ARG
from FTA.tests.test_FTA import files, udata


def test_server_run(udata, files):
    # Тестовый запуск сервера
    from time import sleep
    udata.file_targets = [
        './test_files/1.txt'
    ]
    udata.pwd = '90'
    udata.write = True
    udata.port = 2021
    udata.is_random = False
    thread = Thread(target=server.server, args=(udata,))
    thread.daemon = True
    thread.start()
    print("Starting server for 3 seconds")
    sleep(3)
    print("Done")


def test_req_data(udata, files):
    # Проверка отправляемых данных (дебаг)
    udata.file_targets = [
        './test_files/b.txt',
        './test_files/3.txt',
        './test_files/subfolder',
        './test_files/subfolder2/3.txt',
        '../project/test_files/.',
        'test_files',
        'kek',
        '../project/test_files/subfolder2/..',
    ]
    req = server.RequestData(udata)
    print()
    print(req.gen_msgs())
    print('\n')
    d = json.loads(req.sendable_filelist)
    for entry in d:
        print(f'{entry} : {d[entry]}')

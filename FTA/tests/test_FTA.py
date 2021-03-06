import os
import sys
from threading import Thread

import pytest
from FTA import client, init, server, util
from FTA.__main__ import DEFAULT_ARG


@pytest.fixture
def files():
    # Очистка
    util.clear_folder('./test_files')
    util.clear_folder('./fta_received')
    # Существующий файл
    os.makedirs('./fta_received', exist_ok=True)
    with open(f"./fta_received/1.txt", "w") as f:
        f.write('existing file')
    # Отправляемые файлы
    os.makedirs('./test_files/subfolder/moredata', exist_ok=True)
    os.makedirs('./test_files/subfolder2', exist_ok=True)
    for symb in ('1', '2', '3'):
        with open(f"./test_files/{symb}.txt", "w") as f:
            # 20 байт
            f.write('fezdrfgsitjdrdozbsti')
        with open(f"./test_files/subfolder/{symb}.txt", "w") as f:
            # 30 байт
            f.write('lyrerrmcpsxlbsydefzdkroeomegyo')
        with open(f"./test_files/subfolder2/{symb}.txt", "w") as f:
            # 45 байт
            f.write('tnwolqtsdjvsrlfqmmksstqkyioaqzatczksyffrpeqkl')
        with open(f"./test_files/subfolder/moredata/{symb}.txt", "w") as f:
            # 17 байт
            f.write('wjiasxopvfkggqbxs')


@pytest.fixture
def udata():
    args = DEFAULT_ARG
    args['gui'] = False
    args['<files>'] = ['.']
    session = init.UserData(args)
    return session


def test_self_deny_legacy_response(monkeypatch, udata, files):
    # Самоотправка запроса (отказ) [режим совместимости]
    import concurrent.futures
    action = ['n', 'f']

    def alt_input():
        act = action.pop()
        #print(x, act, sep='')
        return act

    # Переопределение input()
    monkeypatch.setattr('builtins.input', alt_input)

    def cl(udata):
        return client.listen(udata)

    def serv(udata):
        return server.send(udata)

    udata.is_legacy = True
    udata.target_ip = [udata.ip]
    udata.file_targets = 'F:/1'
    th1 = Thread(target=cl, args=(udata,), daemon=True)
    th1.start()
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future = executor.submit(serv, udata)
        val = future.result()
    assert val == 1


def test_self_deny_response(monkeypatch, udata, files):
    # Самоотправка запроса (отказ)
    import concurrent.futures
    action = ['n', 'f']

    def alt_input():
        act = action.pop()
        #print(x, act, sep='')
        return act

    # Переопределение input()
    monkeypatch.setattr('builtins.input', alt_input)

    def cl(udata):
        return client.listen(udata)

    def serv(udata):
        return server.send(udata)

    udata.target_ip = [udata.ip]
    udata.file_targets = ['./test_files/b.txt',
                          './test_files/3.txt',
                          './test_files/subfolder',
                          './test_files/subfolder2/3.txt', ]
    th1 = Thread(target=cl, args=(udata,), daemon=True)
    th1.start()
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future = executor.submit(serv, udata)
        val = future.result()
    assert val == 1


def test_self_accept_response(monkeypatch, udata, files):
    # Самоотправка запроса (согласие)
    import concurrent.futures
    action = ['y', '150', '70', '90']
    action.reverse()

    def alt_input():
        act = action.pop()
        #print(x, act, sep='')
        return act

    # Переопределение input()
    monkeypatch.setattr('builtins.input', alt_input)

    def cl(udata):
        return client.listen(udata)

    def serv(udata):
        return server.send(udata)

    udata.write = True
    udata.pwd = '90'
    udata.target_ip = [udata.ip]
    udata.file_targets = ['./test_files/1.txt',
                          './test_files/subfolder',
                          './test_files/3.txt']
    th1 = Thread(target=cl, args=(udata,), daemon=True)
    th1.start()
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future = executor.submit(serv, udata)
        val = future.result()
    assert val == 0

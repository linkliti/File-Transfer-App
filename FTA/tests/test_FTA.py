import pytest
import os
import sys
from FTA import client, server, init, util
from threading import Thread
from FTA.__main__ import DEFAULT_ARG


@pytest.fixture
def files():
    util.clear_folder('./test_files')
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


def test_no_user_pass_fields():
    # Тест автогенерации пароля
    args = DEFAULT_ARG
    assert init.UserData(args).is_random == True
    args['--pwd'] = 'pass'
    assert init.UserData(args).is_random == False


def test_self_response(monkeypatch, udata, files):
    # Самоотправка запроса (отказ)
    import concurrent.futures
    action = ['n', 'f']

    def alt_input(x):
        act = action.pop()
        print(x, act, sep='')
        return act

    # Переопределение input()
    monkeypatch.setattr('builtins.input', alt_input)

    def cl(udata):
        return client.listen(udata)

    def serv(udata):
        return server.send(udata)

    udata.target_ip = [udata.ip]
    udata.files = ['./test_files/b.txt',
                   './test_files/3.txt',
                   './test_files/subfolder',
                   './test_files/subfolder2/3.txt', ]
    th1 = Thread(target=cl, args=(udata,), daemon=True)
    th1.start()
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future = executor.submit(serv, udata)
        val = future.result()
    assert val == 1

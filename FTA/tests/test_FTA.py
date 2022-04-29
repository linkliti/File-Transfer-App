import pytest
from FTA import client, server, init, util
from threading import Thread
from FTA.__main__ import DEFAULT_ARG


@pytest.fixture
def udata():
    args = DEFAULT_ARG
    args['gui'] = False
    args['<path>'] = '.'
    session = init.UserData(args)
    return session


def test_ip_check():
    # Тест текущего IP
    import socket
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.settimeout(0)
    s.connect(('8.8.8.8', 20))
    IP = s.getsockname()[0]
    print()
    assert init.get_ip() == IP


def test_no_user_pass_fields():
    # Тест автогенерации пароля
    args = DEFAULT_ARG
    assert init.UserData(args).is_random == True
    args['--user'] = 'user'
    assert init.UserData(args).is_random == True
    args['--pwd'] = 'pass'
    assert init.UserData(args).is_random == False


def test_server_run(udata):
    # Тестовый запуск сервера
    from time import sleep
    thread = Thread(target=server.server, args=(udata,))
    thread.daemon = True
    thread.start()
    print("Starting server for 3 seconds")
    sleep(3)
    print("Done")


@pytest.mark.parametrize('ip,res', [
    ('127.0.0.1',       4),
    ('192.168.1.1',     4),
    ('192.168.1.255',   4),
    ('255.255.255.255', 4),
    ('0.0.0.0',         4),
    ('127.0.0',         3),
    ('192.168.1',       3),
    ('255.255.255',     3),
    ('0.0.0',           3),
    ('1.1.1.01',        0),
    (' 127.0.0.1',      0),
    ('127',             0),
    ('127.',            0),
    ('30.168.1.255.1',  0),
    ('192.168.1.256',   0),
    ('-1.2.3.4',        0),
    ('3...3',           0),
])
def test_ip_regex(ip, res):
    # Проверка IP адреса
    assert util.is_ip(ip) == res


@pytest.mark.parametrize('ip', [
    ('192.168.1.1'),
    ('192.168.1'),
    ('192.168.1.'),
    ('192.168.1.1, 192.168.1.2'),
    ('192.168.1.1, 192.168.1'),
    ('192.168.1, 192.168.2'),
    ('192.168.1, 192.168.6.'),
    ('192.168.256'),
    ('192.168.256.'),
    (' 192.168.255.'),
    ('text'),
])
def test_scan(ip, udata):
    # Проверка сканера
    udata.target_ip = ip
    assert client.scan(udata) == 0


def test_req_data(udata):
    # Проверка отправляемых данных (дебаг)
    req = server.RequestData(udata).send_form()
    print()
    print(type(req))
    print('Data:')
    print(req)


def test_self_response(monkeypatch, udata):
    # Самоотправка запроса (отказ)
    import concurrent.futures

    def alt_input(x):
        return 0

    # Переопределение input()
    monkeypatch.setattr('builtins.input', alt_input)

    def cl(udata):
        return client.listen(udata)

    def serv(udata):
        return server.send(udata)

    udata.target_ip = udata.ip
    th1 = Thread(target=cl, args=(udata,), daemon=True)
    th1.start()
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future = executor.submit(serv, udata)
        val = future.result()
    assert val == 1

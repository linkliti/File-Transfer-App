import pytest
import os
import sys
import time
from FTA import client, server, init, util
from threading import Thread
from FTA.__main__ import DEFAULT_ARG
from FTA.tests.test_FTA import udata, files


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
@pytest.mark.usefixtures("udata")
def test_scan(ip, udata):
    """ Проверка сканера """
    udata.target_ip = ip
    assert client.scan(udata) == 0


def test_scan(udata):
    """ Проверка сканера """
    udata.target_ip = ['172.24.98']
    client.scan(udata)
    #assert client.scan(udata) is not None


def test_default_scan(udata):
    """ Проверка сканера """
    assert client.scan(udata) is None


def test_progress_bar():
    """ Проверка прогресс бара """
    n = 5
    client.printProgressBar(0, n)
    for i in range(n+1):
        time.sleep(0.1)
        client.printProgressBar(i, n)

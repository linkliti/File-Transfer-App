import pytest
import os
import sys
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
    # Проверка сканера
    udata.target_ip = ip
    assert client.scan(udata) == 0

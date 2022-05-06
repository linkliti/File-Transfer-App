import os
import sys
from threading import Thread

import pytest
from FTA import client, init, server, util
from FTA.__main__ import DEFAULT_ARG
from FTA.tests.test_FTA import files, udata


@pytest.mark.parametrize('file,drive', [
    ('/mnt/d/tutorial', '/mnt/d'),
    ('d:/tutorial/tut', 'd:'),
    ('/home/mnt/tutorial', os.path.expanduser("~")),
    ('c:/files/c', 'c:'),
    ('C:/files/c', 'c:'),
    ('d:/d/d', 'd:'),
    ('/media/alex/disk/file', '/media/alex/disk'),
])
def test_drive(file, drive):
    assert util.drive(file, '') == drive


def test_variable_size():
    # Размер переменной (дебаг)
    var = 'FTA_Send_Server'
    print(sys.getsizeof(var))
    print(sys.getsizeof(var.encode()))


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


def test_homedir():
    # Проверка домашней папки (дебаг)
    print(util.homedir())
    print(util.homedir() + '/.FTA')
    return


def test_parse_folder(files):
    # Проверка получения списка файлов (дебаг)
    for elem in util.parse_folder('../project/test_files'):
        print(elem)


def test_clear_folder(files):
    # Проверка удаления папки
    util.clear_folder('./test_files/subfolder')


@pytest.mark.parametrize('name,res', [
    ('subfolder/1.txt',         'subfolder/1 (2).txt'),
    ('subfolder/2.txt',         'subfolder/2 (2).txt'),
    ('subfolder/1 (2).txt',     'subfolder/1 (3).txt'),
    ('fold/.FTA/1.txt',         'fold/.FTA/1 (2).txt'),
    ('fold/.FTA/2 (1).txt',     'fold/.FTA/2 (2).txt'),
    ('fold/.FTA/1 (4).txt',     'fold/.FTA/1 (5).txt'),
    ('1.txt',                   '1 (2).txt'),
    ('2.txt',                   '2 (2).txt'),
    ('1 (2).txt',               '1 (3).txt'),
    ('1 (2).tar.gz',            '1 (3).tar.gz'),
    ('1 (10).tar.gz',           '1 (11).tar.gz'),
])
def test_copy_handler(name, res):
    # Проверка переименований копий
    assert util.copy_handler(name) == res


def test_ip_check():
    # Тест текущего IP
    import socket
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.settimeout(0)
    s.connect(('8.8.8.8', 20))
    IP = s.getsockname()[0]
    print()
    assert init.get_ip() == IP

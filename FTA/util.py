from __future__ import absolute_import
import socket
from pkg_resources import resource_filename
from glob import glob
import re
import os
import sys
import shutil
import secrets
import string
import netifaces
from platform import uname

SIZE_VAL = ('байт', 'КБайт', 'МБайт', 'ГБайт', 'ТБайт', 'ПБайт')

def drive(file_path) -> str:
    """ Получить диск файла """
    return ((os.path.splitdrive(abs_path(file_path))[0])) or ''


def readable_size(size) -> tuple:
    """ Получить читабельный размер """
    size_t = 0
    while size // 1024 > 0 and size_t < 6:
        size /= 1024
        size_t += 1
    return (size, SIZE_VAL[size_t])


def copy_handler(filename) -> str:
    """ Обновление индекса одинаковых имен """
    name, ext = os.path.splitext(filename)
    # Исправления tar.gz
    part = os.path.splitext(name)[1]
    while part != '':
        name = name[:len(name)-len(part)]
        ext = part + ext
        part = os.path.splitext(name)[1]
    # Проверка существующего индекса
    index = re.findall('\s\(\d+\)$', name)
    if index:
        num = int(re.findall('\d+', index[0])[0])
        name = name[:len(name)-len(index[0])] + f' ({str(num+1)})'
    # Не существует
    else:
        name = name + ' (2)'
    return name + ext


def abs_path(path) -> str:
    """ Получить абсолютный путь """
    return os.path.abspath(path).replace('\\', '/')


def clear_folder(folder_path, safe_flag=False) -> None:
    """Очистить содержимое папки"""
    # Флаг безопасной очистки
    if safe_flag and ('/.fta_shared' not in abs_path(folder_path)):
        return
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print(f'Не удалось удалить {file_path} : {e}')


def parse_folder(folder_path) -> list:
    """Получить рекурсивно все файлы из папки"""
    return [abs_path(y) for x in os.walk(folder_path)
            for y in glob(os.path.join(x[0], '*.*'))]


def homedir() -> str:
    """ Получить домашнюю папку """
    try:
        directory = os.path.expanduser("~").replace(
            '\\', '/') + '/.FTA'
        if not os.path.exists(directory):
            os.makedirs(directory)
    except OSError as e:
        print(f"Ошибка доступа к домашней папке: {e}")
        print(f"Будет использоваться {abs_path('.')}")
        directory = '.'
    return directory


def hlink(src, dist):
    """Создание hardlink связки"""
    os.link(src, dist)



def pkgfile(path) -> str:
    """Получить файл пакета"""
    return (resource_filename('FTA', path))


def make_pass() -> str:
    """Создать 10 значный пароль"""
    alphabet = string.ascii_letters + string.digits
    pwd = ''.join(secrets.choice(alphabet) for i in range(10))
    return pwd


def is_ip(ip) -> int:
    """ Проверка полных и неполных IP адресов (2-4 колонки)"""
    if type(ip) is str:
        col_count = ip.count('.') + 1
        if col_count > 1 and col_count < 5:
            pattern = '^((25[0-5]|(2[0-4]|1\d|[1-9]|)\d)(\.(?!$)|$)){' + \
                str(col_count) + '}$'
            return (col_count if bool(re.search(pattern, ip)) else 0)
    return 0


def get_ip() -> str:
    """ Получить локальный IP """
    sc = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sc.settimeout(0)
    try:
        sc.connect(('10.255.255.255', 1))
        IP = sc.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        sc.close()
    return IP


def get_all_ip() -> list:
    """ Получить все локальные IP """
    ips = [netifaces.ifaddresses(iface)
           [netifaces.AF_INET][0]['addr'] for iface in
           netifaces.interfaces() if netifaces.AF_INET in
           netifaces.ifaddresses(iface)]
    # Исправление для WSL
    if 'microsoft-standard' in uname().release:
        ips.append(
            os.popen('''cat /etc/resolv.conf | grep nameserver \
                     | cut -d ' ' -f 2''').read())
    return ips


if __name__ == '__main__':
    print('Используйте "python -m FTA"')

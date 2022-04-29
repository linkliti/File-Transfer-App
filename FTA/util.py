import socket
from pkg_resources import resource_filename
import re
import os


def pkgfile(path) -> str:
    """Получить файл пакета"""
    return (resource_filename('FTA', path))


def make_pass() -> str:
    """Создать 13 значный пароль"""
    import secrets
    import string
    alphabet = string.ascii_letters + string.digits
    pwd = ''.join(secrets.choice(alphabet) for i in range(13))
    return pwd


def is_ip(ip) -> int:
    """ Проверка полных и неполных IP адресов (2-4 колонки)"""
    col_count = ip.count('.') + 1
    if col_count > 1 and col_count < 5:
        pattern = '^((25[0-5]|(2[0-4]|1\d|[1-9]|)\d)(\.(?!$)|$)){' + \
            str(col_count) + '}$'
        return (col_count if bool(re.search(pattern, ip)) else 0)
    else:
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
    import netifaces
    from platform import uname
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

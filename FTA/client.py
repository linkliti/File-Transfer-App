import ftplib
import json
import os
import socket
from threading import Lock, Thread

from tabulate import tabulate

from FTA.__init__ import __version__
from FTA.util import (abs_path, copy_handler, get_all_ip, get_console_width,
                      is_ip, readable_size)


class Scan_Threader:
    """Класс сканирования сети"""

    def __init__(self):
        self.thread_lock = Lock()
        self.functions_lock = Lock()
        self.functions = []
        self.threads = []
        self.nthreads = 255
        self.running = True
        self.print_lock = Lock()
        socket.setdefaulttimeout(0.1)

    def stop(self) -> None:
        """Сигнал остановки"""
        self.running = False

    def append(self, function, *args) -> None:
        """Добавить функцию в список"""
        self.functions.append((function, args))

    def start(self) -> None:
        """Создание ограниченного числа потоков"""
        for i in range(self.nthreads):
            thread = Thread(target=self.worker, daemon=True)
            thread._args = (thread, )
            self.threads.append(thread)
            thread.start()

    def join(self) -> None:
        """Присоединение к основному процессу"""
        for thread in self.threads:
            thread.join()

    def worker(self, thread: Thread) -> None:
        """Обработчик списка функций"""
        while self.running and (len(self.functions) > 0):
            try:
                with self.functions_lock:
                    # Получить функцию
                    function, args = self.functions.pop(0)
                # Вызвать функцию
                function(*args)
            except IndexError:
                # Замедление работы
                self.nthreads -= 5

        # Убрать процесс из списка процессов
        with self.thread_lock:
            self.threads.remove(thread)


def connect(hostname, port) -> None:
    """Подключение к hostname:port"""
    msg = ''
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        result = sock.connect_ex((hostname, port))
        try:
            msg = sock.recv(50).decode()
        except:
            if not msg:
                return
    try:
        if 'FTA_Server' in msg:
            user = (msg.split(' ')[2]).rstrip()
            resp = 'FTA сервер'
        elif 'FTA_Send_Server' in msg:
            user = 'Неизвестно'
            resp = 'FTA отправитель'
        elif 'FTA_Listen' in msg:
            user = msg.split(' ')[1]
            resp = 'FTA прослушиватель'
        else:
            user = 'Неизвестно'
            resp = 'Неизвестно'
    except IndexError:
        user = 'Неизвестно'
        resp = 'Неизвестно'
    if msg:
        print(f"Найден {hostname}:{port}, {user} [{resp}]")
        found_list.append([f'{hostname}:{port}', user, resp])


def gen_ips(ip, port) -> None:
    """Генератор IP адресов"""
    global threader
    threader = Scan_Threader()
    col_num = is_ip(ip)
    # 4 колонки
    if col_num == 4:
        connect(ip, port)
    # 3 колонки
    elif col_num == 3:
        for i in range(255+1):
            threader.append(connect, f'{ip}.{i}', port)
        threader.start()
        threader.join()
        threader = Scan_Threader()
    # 2 колонки
    elif col_num == 2:
        for i in range(255+1):
            print(f"Сканирование '{ip}.{i}'...")
            gen_ips(f'{ip}.{i}', port)
    # Иное
    else:
        print(f'Неверный IP: {ip}')


def scan(s) -> None:
    """ Стартер scanner """
    scanner(s.target_ip, s.port)


def scanner(target_ip, port) -> list or None:
    """Сканирование сети

    Примеры ip адресов: \n
    None/auto   -> Локальные без 4 колонки \n
    192.168.1.9 -> 192.168.1.9 \n
    192.168.1   -> 192.168.1.X \n
    192.168     -> 192.168.X.X \n
    """
    # пустой s.target_ip:
    if not target_ip or target_ip == ['auto']:
        # Получение IP адресов
        target_ip = get_all_ip()
        for i in range(len(target_ip)):
            # Убрать 4 колонку
            target_ip[i] = '.'.join((target_ip[i]).split('.')[:-1])

    # Обработка списка ip адресов
    global found_list
    found_list = []
    for ip in target_ip:
        # Убрать лишние символы
        t_ip = ip.strip().strip('.')
        print(f"Сканирование '{t_ip}'...")
        # Сканирование
        gen_ips(t_ip, port)
    print('Сканирование завершено')
    # Нумерация
    i = 1
    for entry in found_list:
        entry.insert(0, i)
        i += 1
    if found_list:
        print("Найденные адреса:")
        print(tabulate(found_list, headers=[
              '#', 'Адрес', 'Имя', 'Тип сервера'], tablefmt="presto"))
        print()
    else:
        print("Ничего не найдено")
    return found_list


def listen(s) -> None:
    """ Ожидание отправителя"""
    try:
        if not s.is_gui:
            ip = s.target_ip[0]
        else:
            ip = s.ip
    except IndexError:
        ip = s.ip
    print(f'Прослушивание "{ip}:{s.port}"...')
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as ServerSock:
            ServerSock.bind((ip, s.port))
            ServerSock.listen(1)
            connection = Metadata(ServerSock, s)
            connection.get_metadata()
        if connection.status == 'confirm':
            connection.download_manager()
        elif connection.status == 'ok':
            listen(s)
            return
        else:
            return
    except Exception as e:
        print('Ошибка прослушивания:', type(e).__name__, '-', e)


class Metadata():
    """
    Класс обработки запроса на передачу файлов \n
    \n | status         - Состояние обработки запроса
    \n | sock           - Сокет прослушки
    \n | hostname       - Имя пользователя
    \n | ip             - Используемый IP
    \n | user           - Пользователь FTP сервера
    \n | pwd            - Пароль FTP сервера
    \n | auto_accept    - Автоматическая отправка согласия
    \n | save_path      - Путь сохранения файлов
    \n | port           - Используемый порт
    \n | files_list     - Полученный список файлов
    """

    def __init__(self, ServerSock, s):
        self.s = s
        self.status = 'ok'
        self.sock = ServerSock
        self.hostname = s.hostname
        self.ip = ''
        self.user = ''
        self.pwd = s.pwd
        self.auto_accept = s.auto_accept
        self.save_path = s.save_path
        self.port = 0
        self.files_list = {}

    def get_metadata(self) -> int:
        """
        Получение информации по отправляемым файлам и
        отправка ответа
        """
        try:
            # Продолжать работу после сканеров
            while True:
                # Подключение
                clientConnected, cl_adr = self.sock.accept()
                clientConnected.settimeout(3600)
                # Отправка статуса
                clientConnected.send(f'FTA_Listen {self.hostname}'.encode())
                # Сообщение
                print(f'Входящее подключение {cl_adr[0]}:{cl_adr[1]}', end='')
                # Получение основной информации
                data = clientConnected.recv(512)
                try:
                    req = json.loads(data.decode())
                    print()
                    break
                except json.JSONDecodeError:
                    print(f' - Сканер')
            # Отправка подтверждения приема информации
            clientConnected.send('FTA_conf'.encode())
            try:
                # Сохранение IP и пользователя
                self.ip = cl_adr[0]
                self.user = req['user']
                self.port = req['port']
                # Получение списка файлов
                temp_list = {}
                size = readable_size(req['files_list_size'])
                print(f'Загрузка списка файлов размером {size[0]} {size[1]}')
                data = clientConnected.recv(req['files_list_size'])
                temp_list = json.loads(data.decode())
                self.files_list = {**self.files_list, **temp_list}

                # Подсчет кол-ва файлов и их размер
                if not (sum(self.files_list.values()) == req['files_size'] and
                        len(self.files_list) == req['files_count']):
                    print(f'Отключение от {cl_adr[0]}:{cl_adr[1]}', end=' - ')
                    print('Список файлов не совпадает с ожидаемой передачей')
                    print('Информация:', type(e).__name__, '-', e)
                    clientConnected.close()
                    return -1

                # Обработка запроса
                # Разные версии
                if not req['FTA_version'] == __version__:
                    print(f"Разная версия программ (текущая: ", end=' ')
                    print(f"{__version__} полученная: {req['FTA_version']}")

            # Неудачная обработка JSON
            except json.JSONDecodeError as e:
                print(f'Отключение от {cl_adr[0]}:{cl_adr[1]}', end=' - ')
                print('Был передан поврежденный JSON')
                print('Информация:', type(e).__name__, '-', e)
                clientConnected.close()
                return -1
            # Информирование
            confirm = self.request_msg(req, self.s.is_gui)

            # Отправка ответа
            resp = json.dumps(
                {'confirm': (cl_adr[0] if confirm else False)})
            clientConnected.send(resp.encode())
            return 0
        except Exception as e:
            self.status = 'error'
            print('Ошибка сокета:', type(e).__name__, '-', e)
            return -1

    def download_manager(self):
        """ Работа с FTP сервером """
        try:
            # Папка скачиваемых файлов
            if not os.path.exists(self.save_path):
                os.makedirs(abs_path(self.save_path))
            # Подключение
            ftp = ftplib.FTP_TLS()
            print(f'Подключение к: {self.ip}:{self.port}')
            ftp.connect(self.ip, self.port)
            # Пароль

            if not login(self.user, self.pwd, ftp.login, is_gui=self.s.is_gui):
                print("Ошибка FTP: Не удалось подключиться")
                ftp.close()
                return

            # Прогресс бар
            printProgressBar(0, len(self.files_list), is_gui=self.s.is_gui)
            i = 0
            # Скачивание
            ftp.prot_p()
            for file in self.files_list:
                # Создание подпапки
                subfolder, filename = os.path.split(
                    self.save_path + '/' + file)
                if not os.path.exists(subfolder):
                    os.makedirs(subfolder)
                # Существующий дубликат -> переименовать скачиваемый файл
                while os.path.exists(subfolder + '/' + filename):
                    filename = copy_handler(filename)
                # Скачивание
                with open(subfolder + '/' + filename, 'wb') as my_file:
                    ftp.retrbinary('RETR ' + file, my_file.write, 1024)
                # Обновление прогресс бара
                i += 1
                printProgressBar(i, len(self.files_list), is_gui=self.s.is_gui)
            print('Скачивание завершено')
            ftp.close()
        except ftplib.all_errors as e:
            print('Ошибка FTP:', type(e).__name__, '-', e)

    def request_msg(self, req, is_gui=False):
        """ Функция текстового информирования """
        print(f"Запрос на передачу от {req['hostname']}")
        print(f"Всего файлов: {req['files_count']}", end='; ')
        print(f"Размер:", ' '.join(str(x) for x in
                                   readable_size(req['files_size'])))
        printable_list = tabulate([
            (k, ' '.join(str(x) for x in readable_size(v))) for k, v
            in self.files_list.items()],
            headers=['Файл', 'Размер'])
        if not self.auto_accept and is_gui:
            print("[!] Требуется подтверждение в консоли")
        while True:
            if self.auto_accept:
                self.status = 'confirm'
                return True
            try:
                print("Согласиться? (Да|Нет|Файлы): ", end='')
                q = input()
            except:
                return False
            # Согласие
            if q[0] in ('y', 'Y', '1', 'Д', 'д', 'да', 'Да', 'yes'):
                self.status = 'confirm'
                return True
            # Список файлов
            elif q[0] in ('L', 'l', 'Л', 'л', 'Ф',
                          'ф', 'F', 'f', 'С', 'с', 'файлы', 'Файлы', 'files'):
                print()
                print(printable_list)
                print()
            # Отказ
            else:
                return False


def printProgressBar(iteration, total, prefix='Прогресс:', suffix='завершено ',
                     decimals=1, fill='█',
                     printEnd="\r\n", is_gui=False):
    """
    Прогресс бар для списка скачиваемых файлов
    """
    if is_gui:
        length, printEnd = (10, '\r\n')
    else:
        length, printEnd = get_console_width()  # Длина терминала
    percent = ("{0:." + str(decimals) + "f}").format(100 *
                                                     (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '-' * (length - filledLength)
    if length >= 20:
        print(f'\r{prefix} |{bar}| {percent}% {suffix}', end=printEnd)
    else:
        print(f'\r{percent}% {suffix}', end=printEnd)
    # Print New Line on Complete
    if iteration == total:
        print()


def login(user, pwd, login_func, attempt=0, is_gui=False):
    """ Функция логина на сервера """
    if attempt == 3:
        return 0
    if not pwd:
        if is_gui:
            print('[!] Требуется ввод пароля в консоль')
        print('Введите пароль: ', end='')
        new_pass = str(input())
    else:
        new_pass = pwd
    try:
        login_func(user, new_pass)
        return 1
    except ftplib.error_perm as e:
        print('Неверный пароль')
        res = login(user, None, login_func, attempt+1)
        return res


if __name__ == '__main__':
    print('Используйте "python -m FTA"')

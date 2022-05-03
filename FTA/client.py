import json
import socket
import ftplib
import os
from threading import Lock, Thread

from FTA.__init__ import __version__
from FTA.util import get_all_ip, is_ip, readable_size, abs_path


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
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        result = sock.connect_ex((hostname, port))
        with threader.print_lock:
            if result == 0:
                print(f"Найден {hostname}:{port}\n")
                found_list.append(f'{hostname}:{port}')


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


def listen(s) -> None:
    """ Ожидание отправителя"""
    # Прослушивание
    ServerSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        ip = s.target_ip[0]
    except IndexError:
        ip = s.ip
    print(f'Прослушивание "{ip}:{s.port}"...')
    ServerSock.bind((ip, s.port))
    ServerSock.listen(1)
    confirm = False
    try:
        while True:
            # Подключение
            clientConnected, cl_adr = ServerSock.accept()
            print(f'Входящее подключение {cl_adr[0]}:{cl_adr[1]}')
            files_list = {}  # Список файлов {путь: размер}
            try:
                # Получение осноной информации
                data = clientConnected.recv(512)
                req = json.loads(data.decode())
                # Подтверждение
                clientConnected.send('conf'.encode())

                # Получение списка файлов
                temp_list = {}
                data = clientConnected.recv(req['files_list_size'])
                temp_list = json.loads(data.decode())
                files_list = {**files_list, **temp_list}

            # Неудачная обработка JSON
            except json.JSONDecodeError as e:
                print(f'Отключение от {cl_adr[0]}:{cl_adr[1]}', end=' - ')
                print('Был передан поврежденный JSON')
                print('Информация:', type(e).__name__, '-', e)
                clientConnected.close()
                break

            # Подсчет кол-ва файлов и их размер
            if not (sum(files_list.values()) == req['files_size'] and
                    len(files_list) == req['files_count']):
                print(f'Отключение от {cl_adr[0]}:{cl_adr[1]}', end=' - ')
                print('Список файлов не совпадает с ожидаемой передачей')
                print('Информация:', type(e).__name__, '-', e)
                clientConnected.close()
                break

            # Обработка запроса
            # Разные версии
            if not req['FTA_version'] == __version__:
                print(f"Разная версия программ (текущая: ", end=' ')
                print(f"{__version__} полученная: {req['FTA_version']}")

            # Информирование
            print(f"Запрос на передачу от {req['hostname']}")
            print(f"Всего файлов: {req['files_count']}", end=' ')
            print(f"Размер: {readable_size(req['files_size'])}")
            while True:
                q = input(f"Согласиться? (Да|Нет|Файлы): ")
                # Согласие
                if q[0] in ('y', 'Y', '1', 'Д', 'д'):
                    confirm = True
                    break
                # Список файлов
                elif q[0] in ('L', 'l', 'Л', 'л', 'Ф',
                              'ф', 'F', 'f', 'С', 'с'):
                    for dict_entry in files_list:
                        print(dict_entry)
                        # print(f'Файл: {file[0]}, \
                        # Размер: {readable_size(file[1])}')
                # Отказ
                else:
                    confirm = False
                    break
            # Отправка ответа
            resp = json.dumps({'confirm': (cl_adr[0] if confirm else False)})
            clientConnected.send(resp.encode())
            ServerSock.close()
            # Выход из listen цикла
            break
    except Exception as e:
        ServerSock.close()
        print('Ошибка сокета:', e)
    # Работа с FTP сервером
    if confirm:
        try:
            # Папка скачиваемых файлов
            if not os.path.exists(s.save_path):
                os.makedirs(abs_path(s.save_path))
            # Подключение
            ftp = ftplib.FTP()
            ftp.connect(cl_adr[0], req["port"])
            # Пароль
            if not login(req["user"], s.pwd, ftp.login):
                print("Ошибка FTP: Не удалось подключиться")
                ftp.close()
                return
            # Скачивание
            print('FTP Files:')
            print(ftp.nlst())
            for file in files_list:
                # Создание подпапки
                subfolder, filename = os.path.split(s.save_path + '/' + file)
                if not os.path.exists(subfolder):
                    os.makedirs(subfolder)
                # Скачивание
                with open(subfolder + '/' + filename, 'wb') as my_file:
                    ftp.retrbinary('RETR ' + file, my_file.write, 1024)
            print('Скачивание завершено')
            ftp.close()
        except ftplib.all_errors as e:
            print('Ошибка FTP:', type(e).__name__, e)

def login(user, pwd, login_func, attempt=0):
    """ Функция логина на сервера """
    if attempt == 3:
        return 0
    if not pwd:
        new_pass = str(input('Введите пароль: '))
    else: new_pass = pwd
    try:
        login_func(user, new_pass)
        return 1
    except ftplib.error_perm as e:
        print('Неверный пароль')
        return login(user, None, login_func, attempt+1)

def scan(s) -> bool:
    """Сканирование сети
    Примеры ip адресов:
    None        -> Локальный без 4 колонки
    192.168.1.9 -> 192.168.1.9
    192.168.1   -> 192.168.1.X
    192.168     -> 192.168.X.X
    """
    # Обработка IP адресов из s.target_ip

    # пустой s.target_ip:
    if not s.target_ip:
        # Получение IP адресов
        s.target_ip = get_all_ip()
        for i in range(len(s.target_ip)):
            # Убрать 4 колонку
            s.target_ip[i] = '.'.join((s.target_ip[i]).split('.')[:-1])
    else:
        # Разбить строку с адресами в список
        s.target_ip = (s.target_ip).split(',')

    # Обработка списка ip адресов
    global found_list
    found_list = []
    for ip in s.target_ip:
        # Убрать лишние символы
        t_ip = ip.strip().strip('.')
        print(f"Сканирование '{t_ip}'...")
        # Сканирование
        gen_ips(t_ip, s.port)
    print('\nСканирование завершено')
    if found_list:
        print("Найденные адреса:")
        for adr in found_list:
            print(f'> {adr}')
    else:
        print("Ничего не найдено")
    return 0


if __name__ == '__main__':
    print('Используйте "python -m FTA"')

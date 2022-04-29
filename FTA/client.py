from threading import Thread, Lock
from FTA.util import is_ip, get_all_ip
from FTA.__init__ import __version__
import socket
import json


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
    ip = s.target_ip or s.ip
    print(f'Прослушивание "{ip}:{s.port}"...')
    ServerSock.bind((ip, s.port))
    ServerSock.listen(1)
    while True:
        # Подключение
        clientConnected, clientAddress = ServerSock.accept()
        print("Входящее подключение %s:%s" %
              (clientAddress[0], clientAddress[1]))
        # Получение информации
        data = clientConnected.recv(1024)
        req = json.loads(data.decode())
        # Обработка запроса
        try:
            if req['FTA_version'] == __version__:
                print(f"Запрос на передачу от {req['hostname']}")
                q = input(f"Согласиться? (1-Да 0-Нет): ")
                if q in ('y', 'Y', '1', 'Д', 'д'):
                    confirm = True
                else:
                    confirm = False
            else:
                print('Неподдерживаемая версия')
        except KeyError:
            print('Был отправлен некорректный запрос')
        # Отправка ответа
        resp = json.dumps({'confirm': confirm})
        clientConnected.send(resp.encode())


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

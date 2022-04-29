from threading import Thread, Lock
import socket
from FTA.util import is_ip


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
        socket.setdefaulttimeout(0.05)

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
            # Получить функцию
            with self.functions_lock:
                function, args = self.functions.pop(0)
            # Вызвать функцию
            function(*args)

        # Убрать процесс из списка процессов
        with self.thread_lock:
            self.threads.remove(thread)


def connect(hostname, port):
    """Подключение к hostname:port"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        result = sock.connect_ex((hostname, int(port)))
        with threader.print_lock:
            if result == 0:
                print(f"Найден {hostname}:{port}\n")
                found_list.append(f'{hostname}:{port}')


def gen_ips(ip, port):
    global threader
    threader = Scan_Threader()
    """Генератор IP адресов"""
    # 4 колонки
    if is_ip(ip) == 4:
        connect(ip, port)
    # 3 колонки
    elif is_ip(ip) == 3:
        for i in range(255+1):
            threader.append(connect, f'{ip}.{i}', port)
        threader.start()
        threader.join()
        threader = Scan_Threader()
    # 2 колонки
    elif is_ip(ip) == 2:
        for i in range(255+1):
            print(f"Сканирование '{ip}.{i}'...")
            gen_ips(f'{ip}.{i}', port)
    # Иное
    else:
        print(f'Неверный IP: {ip}')


def listen(s):
    pass


def scan(s):
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
        s.target_ip = []
        s.target_ip.append('.'.join((s.ip).split('.')[:-1]))
    else:
        s.target_ip = (s.target_ip).split(',')
    # Обработка списка ip адресов
    global found_list
    found_list = []
    for ip in s.target_ip:
        t_ip = ip.strip().strip('.')
        print(f"Сканирование '{t_ip}'...")
        gen_ips(t_ip, s.port)
        print(f'Завершено сканирование {t_ip}')
        if found_list:
            print("Найденные адреса:")
            for adr in found_list:
                print(f'> {adr}')
        else: print("Ничего не найдено")
    return 0


if __name__ == '__main__':
    print('Используйте "python -m FTA"')

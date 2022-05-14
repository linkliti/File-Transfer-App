"""
File Transfer App

gui     - Графический интерфейс
            (автозапуск если нет аргументов)
scan    - Сканирование IP адресов
            (по умолч. - локальные)
server  - Запуск FTP сервера
send    - Отправка запроса и запуск временного FTP сервера
listen  - Режим ожидания запросов
            (по умолч. - прослушка локального адреса)

legacy  - Режим совместимости с FAT32 и Read-Only дисками
            (передача одной папки)

Usage:
    FTA [gui]
    FTA (-h|--help|--version)
    FTA scan
        [<target_ip>]...
    FTA server legacy
        [<folder>]    [--write] [--pwd=<pwd>] [-i=<ip>] [-p=<port>] [--no_cert]
    FTA server
        [<files>]...  [--write] [--pwd=<pwd>] [-i=<ip>] [-p=<port>] [--no_cert]
    FTA send legacy
        <target_ip>   [<folder>]    [--pwd=<pwd>] [-p=<port>]
    FTA send
        <target_ip>   [<files>]...  [--pwd=<pwd>] [-p=<port>]
    FTA listen
        [<save_path>] [<target_ip>] [--pwd=<pwd>] [-p=<port>] [--auto-accept]

Options:
    <files>                 Пути отправляемых файлов и папок
    <folder>                Путь отправляемой папки (режим совместимости)
    <save_path>             Путь сохранения файлов (по умолч: ./fta_received)
    <target_ip>             Целевой IP адрес (несколько если сканер)
    --version               Показать версию программы
    -h --help               Показать помощь
    --no_cert               Разрешить соединения без TLS (только сервер)
    -i --ip=<ip>            Используемый IP для сервера
    -p --port=<port>        Порт (по умолч: 2121)
    -w --write              Разрешение на изменение файлов (сервер)
    --pwd=<pwd>             Пароль FTP сервера
    -a --auto-accept        Подтверждать прием файлов
"""
from docopt import docopt

from FTA.__init__ import __version__
from FTA.init import text_mode, window_mode

DEFAULT_ARG = {'--auto-accept': False,
               '--help': False,
               '--ip': None,
               '--no_cert': False,
               '--port': None,
               '--pwd': None,
               '--version': False,
               '--write': False,
               '<files>': [],
               '<folder>': None,
               '<save_path>': None,
               '<target_ip>': [],
               'gui': True,
               'legacy': False,
               'listen': False,
               'scan': False,
               'send': False,
               'server': False}

if __name__ == '__main__':
    args = docopt(__doc__, version=__version__)
    # Запуск без параметров
    if not (args['listen'] or args['scan'] or
            args['send'] or args['server']):
        # Запуск по конфигурации
        args = DEFAULT_ARG
    # Запуск граф. интерф. при флаге gui или если нет флагов
    if args['gui']:
        window_mode(DEFAULT_ARG)
    else:
        # print(args)
        text_mode(args)

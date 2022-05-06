"""
File Transfer App

gui     - Графический интерфейс (автозапуск если нет аргументов)
scan    - Сканирование IP адресов (по умолч. - локальные)
server  - Запуск FTP сервера
send    - Запуск FTP сервера и отправка запроса цели
listen  - Режим ожидания запросов (по умолч. - прослушка локального адреса)

Usage:
    FTA [gui]
    FTA (-h|--help|--version)
    FTA scan    [<target_ip>]...
    FTA server  [<files>]...                 [-p=<port>] [--pwd=<pwd>] [-w]
    FTA send    <target_ip>   [<files>]...   [-p=<port>] [--pwd=<pwd>]
    FTA listen  [<save_path>] [<target_ip>]  [-p=<port>] [--pwd=<pwd>] [--auto-accept]

Options:
    --version               Показать версию
    -h --help               Показать помощь
    -p --port=<port>        Порт [default: 2121]
    -w --write              Разрешение на изменение файлов
    --pwd=<pwd>             Пароль (FTP сервер)
    -a --auto-accept        Подтверждать прием файлов
"""
from docopt import docopt

from FTA.__init__ import __version__
from FTA.init import text_mode, window_mode

DEFAULT_ARG = {'--auto-accept': False,
               '--help': False,
               '--port': '2121',
               '--pwd': None,
               '--version': False,
               '--write': False,
               '<files>': [],
               '<save_path>': None,
               '<target_ip>': [],
               'gui': True,
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
        window_mode()
    else:
        #print(args)
        text_mode(args)

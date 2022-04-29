"""
File Transfer App

gui - Графический интерфейс (автозапуск если нет аргументов)
scan - Сканирование ip адресов
server - Запуск FTP сервера
send - Запуск FTP сервера и отправка запроса
listen - Режим ожидания запросов

Usage:
    FTA
    FTA gui
    FTA scan [<target>]
    FTA server [<path>] [-p=<port>] [-u=<user>] [--pwd=<pwd>] [-w]
    FTA send <path> <target> [-p=<port>] [--pwd=<pwd>]
    FTA listen <path_save> [-p=<port>] [-a]
    FTA (-h|--help)

Options:
    -h --help               Показать помощь
    -p --port=<port>        Порт [default: 2121]
    -w --write              Разрешение на запись
    -u --user=<user>        Пользователь (FTP сервер)
    --pwd=<pwd>             Пароль (FTP сервер)
    -i --ip=<ip>            IP адреса
    -a --auto-accept        Подтверждать прием файлов
"""
from FTA.init import text_mode, window_mode
from docopt import docopt

DEFAULT_ARG = {'--auto-accept': False,
               '--help': False,
               '--ip': None,
               '--port': '2121',
               '--pwd': None,
               '--user': None,
               '--write': False,
               '<path>': None,
               '<path_save>': None,
               '<target>': None,
               'gui': True,
               'listen': False,
               'scan': False,
               'send': False,
               'server': False}

if __name__ == '__main__':
    args = docopt(__doc__)
    # Запуск без параметров
    if not (args['gui'] or args['listen'] or args['scan'] or
            args['send'] or args['server']):
        # Запуск по конфигурации
        args = DEFAULT_ARG
    no_arg_flag = True
    for arg in args.values():
        if arg is True:
            no_arg_flag = False
    # Запуск граф. интерф. при флаге gui или если нет флагов
    if args['gui'] or no_arg_flag:
        window_mode()
    else:
        # print(args)
        text_mode(args)

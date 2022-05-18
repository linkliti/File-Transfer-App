# File Transfer App
Программа передачи файлов на [Python](https://www.python.org/downloads/)
с использованием FTP сервера
## Установка
1) Загрузить архив и '.ps1' (для Windows) или '.sh' (для Linux) скрипт
2) Запустить скрипт в одной папке с архивом

## Ручная установка
1) Загрузить архив и открыть консоль в папке с архивом
2) Ввести команды
```
pip install setuptools --upgrade
pip install ./FTA-1.0.1.zip
```

## Использование
```
Графический интерфейс
FTA [gui]

Помощь/Версия
FTA (-h|--help|--version)

Сканер
FTA scan [<target_ip>]...

Запуск сервера в режиме совместимости
FTA server legacy [<folder>]
    [--write] [--pwd=<pwd>] [-i=<ip>] [-p=<port>] [--no_cert]

Запуск сервера
FTA server [<files>]...
    [--write] [--pwd=<pwd>] [-i=<ip>] [-p=<port>] [--no_cert]

Запуск отправки в режиме совместимости
FTA send legacy <target_ip> [<folder>]
    [--pwd=<pwd>] [-p=<port>]

Запуск отправки
FTA send <target_ip> [<files>]...
     [--pwd=<pwd>] [-p=<port>]

Запуск прослушивателя (ожидание запросов)
FTA listen [<save_path>] [<target_ip>]
    [--pwd=<pwd>] [-p=<port>] [--auto-accept]
```
Аргументы
```
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
```
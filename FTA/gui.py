import os
import re
import sys

from PyQt5 import QtCore, QtGui, uic
from PyQt5.QtWidgets import *

from FTA.client import listen, scan
from FTA.server import send, server
from FTA.util import (Thread_Process, abs_path, make_pass, pkgfile,
                      readable_size, sleep)


class MainWindow(QMainWindow):
    """Класс графического интерфейса"""

    thread = None  # Активный процесс

    def closeEvent(self, event):
        """ Выход из программы """
        self.stop_flag = True
        if self.thread:
            self.thread.raise_exception()

    def __init__(self, s):
        super().__init__()
        # Данные пользователя
        self.s = s

        # Окно
        uic.loadUi(pkgfile('style/mainwindow.ui'), self)

        # Иконка
        app_icon = QtGui.QIcon(pkgfile('style/icon.svg'))
        self.setWindowIcon(app_icon)

        # Консоль console
        sys.stdout = self.Console_write(self.console)
        self.console_ButtonClear.clicked.connect(self.clear_console)

        # Таблица файлов
        self.legacy_check.stateChanged.connect(self.legacyButton)
        self.fTableClear.clicked.connect(self.clear_filesTable)
        self.filesTable.clearContents()
        self.filesTable.setRowCount(0)
        self.filesTable.resizeColumnToContents(0)
        self.filesTable.resizeColumnToContents(1)
        self.filesTable.resizeColumnToContents(2)

        # Игнорирование: Cannot queue arguments of type 'QTextCursor'
        def handler(msg_type, msg_log_context, msg_string):
            pass
        QtCore.qInstallMessageHandler(handler)
        print('FTA запущен')

        # IP, Порт, Путь сохранения по умолчанию
        self.target_ip_field.setInputMask("000.000.000.000")
        self.ip_field.setText(s.ip)
        self.ip_field.setInputMask("000.000.000.000")
        self.port_field.setText(str(s.port))
        self.port_field.setValidator(QtGui.QIntValidator())
        self.save_path_field.setText(abs_path(s.save_path))

        # Случайный пароль
        self.make_pass_field()
        self.pwd_field_random.clicked.connect(self.make_pass_field)

        # Кнопки скрытия личной информации
        self.hide_ip_field.stateChanged.connect(lambda: self.btnstate('ip'))
        self.hide_port_field.stateChanged.connect(
            lambda: self.btnstate('port'))
        self.hide_pwd_field.stateChanged.connect(lambda: self.btnstate('pwd'))

        # Кнопки выбора пути/файлов
        self.pathSelectButton.clicked.connect(
            lambda: self.file_select('path'))
        self.fTableSelectFiles.clicked.connect(
            lambda: self.file_select('files'))
        self.fTableSelectFolder.clicked.connect(
            lambda: self.file_select('folder'))

        # Кнопки запуска процессов
        self.serverToggle.clicked.connect(lambda: self.startProcess('server'))
        self.scanToggle.clicked.connect(lambda: self.startProcess('scan'))
        self.listenToggle.clicked.connect(lambda: self.startProcess('listen'))
        self.sendToggle.clicked.connect(lambda: self.startProcess('send'))

        # Отключаемые поля и кнопки
        self.toggleable_stuff = (self.serverToggle,
                                 self.fTableClear,
                                 self.scanToggle,
                                 self.listenToggle,
                                 self.sendToggle,
                                 self.target_ip_field,
                                 self.save_path_field,
                                 self.pathSelectButton,
                                 self.ip_field,
                                 self.port_field,
                                 self.legacy_check,
                                 self.nocert_check,
                                 self.write_check,
                                 self.scan_field,
                                 self.fTableSelectFiles,
                                 self.fTableSelectFolder,
                                 self.pwd_field_random,
                                 self.autoaccept_check)

    def make_pass_field(self):
        """ Случайный пароль """
        self.pwd_field.setText(make_pass())

    def legacyButton(self):
        """ Переключатель режима совместимости"""
        if self.legacy_check.isChecked():
            self.fTableSelectFiles.setEnabled(False)
        else:
            self.fTableSelectFiles.setEnabled(True)
        self.clear_filesTable()

    def toggleVisibility(self, line):
        """ Переключение отображения личной информации """
        if line.echoMode() == QLineEdit.Normal:
            line.setEchoMode(QLineEdit.Password)
        else:
            line.setEchoMode(QLineEdit.Normal)

    def btnstate(self, btn):
        """ Функционал кнопок скрытия личной информации """
        self.toggleVisibility(getattr(self, btn + '_field'))

    def clear_filesTable(self):
        """ Очистка списка файлов """
        self.filesTable.clearContents()
        self.filesTable.setRowCount(0)
        self.s.file_targets = []

    def file_select(self, t):
        """ Вызов окна выбора файлов """
        if t == 'path':
            inp = QFileDialog.getExistingDirectory(self, "Выберите папку")
            if not inp:
                return
            self.save_path_field.setText(str(inp))
            return
        elif t == 'files':
            inp = QFileDialog.getOpenFileNames(self, "Выберите файлы")[0]
            if not inp:
                return
            self.s.file_targets += inp
        else:
            #self.s.file_targets += parse_folder(folder)[1]
            #folder = QFileDialog.getExistingDirectory(self, "Выберите папку")
            try:
                inp = QFileDialog.getExistingDirectory(self, "Выберите папку")
            except FileNotFoundError:
                return
            if not inp:
                return
            if self.legacy_check.isChecked():
                self.s.file_targets = [inp]
            else:
                self.s.file_targets += [inp]
        # Обновление таблицы
        self.filesTable.clearContents()
        row = 0
        self.filesTable.setRowCount(len(self.s.file_targets))
        for file in self.s.file_targets:
            if os.path.isdir(file):
                size = 'Папка'
            else:
                size = readable_size(os.path.getsize(file))
                size = str(size[0]) + ' ' + size[1]
            self.filesTable.setItem(
                row, 0, QTableWidgetItem(os.path.split(file)[1]))
            self.filesTable.setItem(
                row, 1, QTableWidgetItem(size))
            self.filesTable.setItem(
                row, 2, QTableWidgetItem(file))
            # Отключить редактирование
            for i in range(3):
                item = self.filesTable.item(row, i)
                item.setFlags(item.flags() ^ QtCore.Qt.ItemIsEditable)
            row = row+1
        self.filesTable.resizeColumnToContents(0)
        self.filesTable.resizeColumnToContents(1)
        self.filesTable.resizeColumnToContents(2)

    def enable_buttons(self, process):
        """ Включение кнопок и полей """
        if process == 'server':
            self.serverToggle.setText('Запуск сервера')
        elif process == 'scan':
            self.scanToggle.setText('Сканирование')
        elif process == 'listen':
            self.listenToggle.setText('Прослушивание')
        elif process == 'send':
            self.sendToggle.setText('Отправка')
        for elem in self.toggleable_stuff:
            elem.setEnabled(True)

    def disable_buttons(self, process):
        """ Отключение кнопок и полей """
        if process == 'server':
            self.serverToggle.setText('Выключить сервер')
        elif process == 'scan':
            self.scanToggle.setText('Остановить сканер')
        elif process == 'listen':
            self.listenToggle.setText('Остановить прослушку')
        elif process == 'send':
            self.sendToggle.setText('Остановить отправку')
        for elem in self.toggleable_stuff:
            elem.setEnabled(False)

    def runProcess(self, process):
        """ Запуск процесса """
        # Обновление UserData
        self.s.is_gui = True
        self.s.ip = self.ip_field.text()
        self.s.port = int(self.port_field.text())
        self.s.pwd = self.pwd_field.text()
        self.s.save_path = self.save_path_field.text()
        self.s.target_ip = [self.target_ip_field.text().rstrip('.')]
        self.s.is_legacy = self.legacy_check.isChecked()
        self.s.write = self.write_check.isChecked()
        self.s.use_cert = not self.nocert_check.isChecked()
        self.s.auto_accept = self.autoaccept_check.isChecked()
        # Режим работы
        if process == 'listen':
            func = listen
        elif process == 'scan':
            self.s.target_ip = re.split(
                ';|,| |\n', self.scan_field.toPlainText())
            if self.s.target_ip == ['']:
                self.s.target_ip = ['auto']
            func = scan
        elif process == 'send':
            func = send
        elif process == 'server':
            func = server
        # Запуск основного процесса
        self.thread = Thread_Process(self.s, func)
        self.thread.daemon = True
        print(f'Запущен процесс {process}')
        self.thread.start()
        # Не завершать работу программы
        while self.thread.is_alive() and not self.stop_flag:
            sleep(1)
        print(f'Процесс {process} завершил работу')
        self.stopProcess(process)

    def stopProcess(self, process):
        """ Попытка остановить процесс без завершения программы """
        # Отключение кнопки
        getattr(self, process + 'Toggle').setEnabled(False)
        # Остановка процесса
        if self.thread.is_alive() and not self.stop_flag:
            print(f'Остановка {process}...')
            if process == 'listen' or process == 'server':
                print("[!] При ручном выходе требуется перезапуск")
            self.thread.raise_exception()
        self.stop_flag = True
        # Выключение кнопки-выключателя
        getattr(self, process + 'Toggle').setEnabled(False)
        # Назначение кнопки на включение
        getattr(self, process + 'Toggle').clicked.disconnect()
        getattr(self, process +
                'Toggle').clicked.connect(lambda: self.startProcess(process))
        # Включение всех кнопок
        self.enable_buttons(process)

    def startProcess(self, process):
        """ Отключение кнопок перед запуском процесса """
        # Отключение кнопок
        self.disable_buttons(process)
        # Назначение кнопки на выключение
        getattr(self, process + 'Toggle').clicked.disconnect()
        getattr(self, process +
                'Toggle').clicked.connect(lambda: self.stopProcess(process))
        # Включение кнопки-выключателя
        getattr(self, process + 'Toggle').setEnabled(True)
        # Процесс
        self.stop_flag = False
        self.runProcess(process)

    def clear_console(self):
        """ Очистка консоли (кнопка)"""
        self.console.setText('')

    class Console_write(object):
        """ Добавление текста в встроенную консоль """

        def __init__(self, console):
            self.console = console

        def write(self, text):
            self.console.insertPlainText(text)
            self.console.moveCursor(QtGui.QTextCursor.End)

        def flush(self):
            pass

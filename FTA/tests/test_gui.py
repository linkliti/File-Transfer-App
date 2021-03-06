import pytest
from FTA import client, init, server, util
from FTA.__main__ import DEFAULT_ARG
from FTA.tests.test_FTA import files, udata


def test_launch_gui():
    """ Запуск графического интерфейса (запускать отдельно)"""
    with pytest.raises(SystemExit):
        init.window_mode(DEFAULT_ARG)

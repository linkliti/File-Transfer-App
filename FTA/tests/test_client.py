import pytest
from FTA.client import *


def test_client():
    ips = ['192.168.0', '172.24.102']
    port = 2121
    print("\nScript Output:")
    assert main(ips, port) == 0

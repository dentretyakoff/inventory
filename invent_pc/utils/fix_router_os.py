"""Исправление сторонней библиотеки RouterOS,
для корректного чтения комментариев на кириллице.
"""

from collections import defaultdict

import routeros_api
from routeros_api.api_structure import StringField


class CustomStringField(StringField):
    def get_mikrotik_value(self, string):
        return string.encode()

    def get_python_value(self, bytes):
        return bytes.decode('cp1251')


class ConnectionWrapper:
    """Позволяет выполнять соедениение к Mikrotik через
    контекстный менеджер with."""
    def __init__(self, connection):
        self.connection = connection

    def __enter__(self):
        return self.connection

    def __exit__(self, exc_type, exc_value, traceback):
        self.connection.disconnect()


routeros_api_fix = routeros_api
routeros_api_fix.api_structure.default_structure = defaultdict(
    CustomStringField)

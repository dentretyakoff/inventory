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


routeros_api_fix = routeros_api
routeros_api_fix.api_structure.default_structure = defaultdict(
    CustomStringField)

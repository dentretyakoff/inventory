"""Модуль исключений для систем: Active Directory, Radius, VPN."""

from exceptions.base import InventoryError


class MissingVariableError(InventoryError):
    """Некорректно заполнена переменная окружения для подключения к сервису."""

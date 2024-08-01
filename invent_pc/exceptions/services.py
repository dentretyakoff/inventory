"""Модуль исключений для систем: Active Directory, Radius, VPN."""

from exceptions.base import InventoryError


class MissingVariableError(InventoryError):
    """Некорректно заполнена переменная окружения для подключения к сервису."""


class RadiusUsersNotFoundError(InventoryError):
    """Не найдены пользователи в группе на сервере Radius."""


class EncryptionKeyMissingError(InventoryError):
    """Ключ шифрования ENCRYPTION_KEY не заполнен в settings."""

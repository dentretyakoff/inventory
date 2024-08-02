import ssl

import mysql.connector
from django.conf import settings

from utils.fix_router_os import routeros_api_fix


class MySQLConnectionManager:
    """Позволяет выполнять соедениение с MySQL через
    контекстный менеджер with."""
    def __init__(self, host, port, user, password, database):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.database = database
        self.connection = None

    def __enter__(self):
        self.connection = mysql.connector.connect(
            host=self.host,
            port=self.port,
            user=self.user,
            password=self.password,
            database=self.database
        )
        return self.connection

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.connection is not None:
            self.connection.close()


class MikrotikConnectionManager:
    """Позволяет выполнять соедениение к Mikrotik через
    контекстный менеджер with."""
    def __init__(
            self, host, port, user, password, use_ssl,
            ssl_verify, ssl_verify_hostname):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.use_ssl = use_ssl
        self.ssl_verify = ssl_verify
        self.ssl_verify_hostname = ssl_verify_hostname
        self.connection = None
        self.plaintext_login = True
        root_cert = settings.ROOT_CA_CERT
        if root_cert.exists():
            ssl_context = ssl.create_default_context(cafile=str(root_cert))
            self.ssl_context = ssl_context
        else:
            self.ssl_context = None

    def __enter__(self):
        self.connection = routeros_api_fix.RouterOsApiPool(
            host=self.host,
            port=self.port,
            username=self.user,
            password=self.password,
            use_ssl=self.use_ssl,
            ssl_verify=self.ssl_verify,
            ssl_verify_hostname=self.ssl_verify_hostname,
            plaintext_login=self.plaintext_login,
            ssl_context=self.ssl_context
        )
        return self.connection

    def __exit__(self, exc_type, exc_value, traceback):
        self.connection.disconnect()

from abc import ABC, abstractmethod

from .mysqlmanager import MySQLConnectionManager


class ExternalService(ABC):
    @abstractmethod
    def session(self):
        """Создать сессию."""
        pass

    @abstractmethod
    def get_users(self):
        """Получить список пользователей."""
        pass

    @abstractmethod
    def block_users(self, users):
        """Заблокировать пользователей."""
        pass


class GigrotermonService(ExternalService):
    def session(self, host, port, user, password, database):
        """Создать сессию."""
        return MySQLConnectionManager(host, port, user, password, database)

    def get_users(self, session):
        """Получить список пользователей."""
        cursor = session.cursor()
        query = """
            WITH option_ids AS (
            SELECT
                MAX(CASE WHEN shortName = 'user.name' THEN id END) AS name_option_id,
                MAX(CASE WHEN shortName = 'user.userLock' THEN id END) AS status_option_id
            FROM optionsname
            )
            SELECT
                o.id AS user_id,
                name_option.newValue AS username,
                status_option.newValue AS status
            FROM
                objects o
            LEFT JOIN actualoptions name_actual 
                ON o.id = name_actual.objectID 
                AND name_actual.optionID = (SELECT name_option_id FROM option_ids)
            LEFT JOIN options name_option 
                ON name_actual.curID = name_option.id
            LEFT JOIN actualoptions status_actual 
                ON o.id = status_actual.objectID 
                AND status_actual.optionID = (SELECT status_option_id FROM option_ids)
            LEFT JOIN options status_option 
                ON status_actual.curID = status_option.id
            WHERE
                o.objectType = 'user';
        """  # noqa
        cursor.execute(query)
        users = cursor.fetchall()
        cursor.close()
        return users

    def block_users(self, users, session):
        """Заблокировать пользователей."""
        pass

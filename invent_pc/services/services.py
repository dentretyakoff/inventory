import logging
from abc import ABC, abstractmethod

from ldap3 import Server, Connection, SUBTREE
from rocketchat_API.rocketchat import RocketChat

from exceptions.services import RadiusUsersNotFoundError
from users.models import VPN, Radius, ADUsers
from utils.fix_pywinrm import CustomSession
from .context_managers import MySQLConnectionManager, MikrotikConnectionManager


logger = logging.getLogger(__name__)


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


class ADService(ExternalService):
    def session(self, host, port, user, password):
        """Создать сессию."""
        server = Server(host, port)
        return Connection(server, user=user, password=password)

    def get_users(self, session, base_dn, seatch_filter):
        """Получить список пользователей."""
        session.bind()
        result = session.extend.standard.paged_search(
            base_dn,
            seatch_filter,
            SUBTREE,
            get_operational_attributes=True,
            attributes=(
                'cn', 'sAMAccountName', 'wWWHomePage', 'userAccountControl'),
            paged_size=1000,
            generator=True
        )
        return result

    def block_users(self, users):
        """Заблокировать пользователей."""
        pass


class MikrotikService(ExternalService):
    def session(
            self, host, port, user, password, use_ssl,
            ssl_verify, ssl_verify_hostname):
        """Создать сессию."""
        return MikrotikConnectionManager(
            host, port, user, password, use_ssl,
            ssl_verify, ssl_verify_hostname)

    def get_users(self, session):
        """Получить список пользователей."""
        api = session.get_api()
        ppp_secrets = api.get_resource('/ppp/secret/')
        secrets = ppp_secrets.call(
            'print',
            {'proplist': 'name,comment,disabled'}
        )
        return secrets

    def block_users(self, session, need_disable):
        """Заблокировать пользователей."""
        users = VPN.get_users_to_block()

        if not users or not need_disable:
            return

        api = session.get_api()
        ppp_secrets = api.get_resource('/ppp/secret/')

        for user in users:
            secret = ppp_secrets.get(name=user.login)
            if secret:
                ppp_secrets.set(id=secret[0].get('id'), disabled='yes')
                logger.info(f'Пользователь VPN {user} отключен.')

        VPN.objects.bulk_update(users, ['status'])


class RadiusService(ExternalService):
    def session(self, host, user, password, cert_validation):
        """Создать сессию."""
        validation = {True: 'validate', False: 'ignore'}
        return CustomSession(
            transport='ntlm',
            target=host,
            server_cert_validation=validation[cert_validation],
            auth=(user, password)
        )

    def get_users(self, session, ps_script):
        """Получить список пользователей."""
        result = session.run_ps(ps_script)
        result = result.std_out.decode()

        if not result:
            raise RadiusUsersNotFoundError('Не найдены пользователи в группе')

        return result

    def block_users(self, session, need_disable):
        """Заблокировать пользователей."""
        users = Radius.get_users_to_block()

        if not users or not need_disable:
            return

        users_list = ','.join(f'"{user.login}"' for user in users)
        ps_script = f"""
        $users = @({users_list})
        foreach ($user in $users) {{
            Disable-LocalUser -Name $user
        }}
        """
        session.run_ps(ps_script)

        Radius.objects.bulk_update(users, ['status'])


class RocketChatService(ExternalService):
    def session(self, host, user, password):
        """Создать сессию."""
        return RocketChat(user, password, server_url=host)

    def get_users(self, session, ps_script):
        """Получить список пользователей."""
        raise NotImplementedError

    def block_users(self, session, need_disable):
        """Заблокировать пользователей."""
        users = ADUsers.get_users_to_block()

        if not users or not need_disable:
            return

        for user in users:
            user_info = session.users_info(username=user.login).json()
            if user_info.get('success'):
                user_id = user_info['user']['_id']
                session.users_update(user_id=user_id, active=False).json()
                logger.info(
                    f'Пользователь {user.login} отключен на '
                    'сервере RocketChat.')
            else:
                logger.info(f'{user} не найден')

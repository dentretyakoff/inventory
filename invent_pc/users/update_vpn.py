import logging
import ssl

from django.conf import settings

from utils.fix_router_os import routeros_api_fix, ConnectionWrapper
from users.models import VPN, ADUsers
from utils.utils import check_envs
from .utils import update_or_create_users


logger = logging.getLogger(__name__)


def update_vpn():
    """Обновляет учетные записи VPN."""
    vpn_params = check_envs(settings.VPN)
    vpn_users = read_vpn_users(vpn_params)
    update_or_create_users(VPN, vpn_users)
    match_vpn_users()
    block_vpn_users(vpn_params)


def get_vpn_connection(
        vpn_params: dict[str, str]) -> ConnectionWrapper:
    """Создает подключение к Mikrotik."""
    params = {
        'host': vpn_params.get('VPN_HOST'),
        'username': vpn_params.get('VPN_USER'),
        'password': vpn_params.get('VPN_PASSWORD'),
        'use_ssl': vpn_params.get('VPN_USE_SSL'),
        'ssl_verify': vpn_params.get('VPN_SSL_VERIFY'),
        'ssl_verify_hostname': vpn_params.get('VPN_SSL_VERIFY_HOSTNAME'),
        'plaintext_login': True,
    }
    root_cert = settings.ROOT_CA_CERT
    if root_cert.exists():
        ssl_context = ssl.create_default_context(cafile=str(root_cert))
        params['ssl_context'] = ssl_context
    connection = routeros_api_fix.RouterOsApiPool(**params)

    return ConnectionWrapper(connection)


def read_vpn_users(vpn_params: dict[str]) -> list[dict[str, str]]:
    """Читает учетные записи vpn из Mikrotik."""
    with get_vpn_connection(vpn_params) as connection:
        api = connection.get_api()
        ppp_secrets = api.get_resource('/ppp/secret/')
        secrets = ppp_secrets.call(
            'print',
            {'proplist': 'name,comment,disabled'}
        )
        vpn_users = []

        for secret in secrets:
            user_status = 'active'
            if secret['disabled'] == 'true':
                user_status = 'inactive'
            vpn_users.append(
                {
                    'login': secret.get('name'),
                    'comment': secret.get('comment'),
                    'status': user_status
                }
            )

    return vpn_users


def block_vpn_users(vpn_params: dict[str]) -> None:
    """Блокирует учетные записи VPN в mikrotik."""
    users = VPN.get_users_to_block()
    need_disable = vpn_params.get('VPN_NEED_DISABLE_USERS')

    if not users or not need_disable:
        return

    with get_vpn_connection(vpn_params) as connection:
        api = connection.get_api()
        ppp_secrets = api.get_resource('/ppp/secret/')

        for user in users:
            secret = ppp_secrets.get(name=user.login)
            if secret:
                ppp_secrets.set(id=secret[0].get('id'), disabled='yes')
                logger.info(f'Пользователь VPN {user} отключен.')

    VPN.objects.bulk_update(users, ['status'])


def match_vpn_users() -> None:
    """Сопоставляет VPN с учетными записями AD."""
    no_vpn_users = ADUsers.objects.filter(vpn=None)
    vpn_users = {
        user.comment.lower(): user
        for user in VPN.objects.filter(
            ad_user__isnull=True,
            comment__isnull=False
        )
    }

    updated_users = []

    for no_vpn_user in no_vpn_users:
        for comment, vpn_user in vpn_users.items():
            if no_vpn_user.fio and no_vpn_user.fio.lower() in comment:
                no_vpn_user.vpn = vpn_user
                updated_users.append(no_vpn_user)

    ADUsers.objects.bulk_update(updated_users, ('vpn',))

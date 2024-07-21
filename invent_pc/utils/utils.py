import json
import logging
from collections import Counter

from django.db.models import QuerySet
from django.conf import settings
from django.core.paginator import Paginator
from ldap3 import Server, Connection, SUBTREE

from exceptions.services import MissingVariableError, RadiusUsersNotFoundError
from users.models import Radius, VPN, StatusChoices
from .fix_router_os import routeros_api_fix, ConnectionWrapper
from .fix_pywinrm import CustomSession

COUNT_PAGES = settings.COUNT_PAGES_PAGINATOR
AD_STATUS_DISABLED_USER = settings.AD_STATUS_DISABLED_USER
logger = logging.getLogger(__name__)


# Паджинация
def get_pages(request, queryset, count_pages=COUNT_PAGES):
    paginator = Paginator(queryset, count_pages)
    page_number = request.GET.get('page')

    # Возвращаем набор записей для страницы с запрошенным номером
    return paginator.get_page(page_number)


def check_envs(envs: dict) -> dict:
    """Проверяет переменные окружения."""
    for key, env in envs.items():
        if env in (None, ''):
            raise MissingVariableError(
                f'Некорректно заполнена переменная окружения: {key}')
    return envs


def read_ad_users(ad_params: dict) -> list[dict[str]]:
    """Читает пользователей Active Directory."""
    server = Server(ad_params.get('AD_HOST'))
    username = f'{ad_params.get("AD_DOMAIN")}\\{ad_params.get("AD_USER")}'  # noqa 'COMPANY\\inventory'
    password = ad_params.get('AD_PASSWORD')
    base_dn = ad_params.get('AD_SEARCH_BASE')
    seatch_filter = ad_params.get('AD_SEARCH_FILTER')
    attrs = ('cn', 'sAMAccountName', 'wWWHomePage', 'userAccountControl')
    page_size = 1000
    ad_users = []

    with Connection(server, user=username, password=password) as conn:
        conn.bind()
        users = conn.extend.standard.paged_search(
            base_dn,
            seatch_filter,
            SUBTREE,
            get_operational_attributes=True,
            attributes=attrs,
            paged_size=page_size,
            generator=True
        )
        for user in users:
            user_attrs = user['attributes']
            email = None
            user_status = 'inactive'
            if user_attrs['userAccountControl'] not in AD_STATUS_DISABLED_USER:
                user_status = 'active'
            if user_attrs.get('wWWHomePage'):
                email = user_attrs.get('wWWHomePage')
            ad_users.append(
                {
                    'fio': user_attrs.get('cn'),
                    'login': user_attrs.get('sAMAccountName'),
                    'email': email,
                    'status': user_status
                }
            )

    return ad_users


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
    VPN.clear_users_for_blocking()


def get_radius_session(radius_params: dict[str, str]) -> CustomSession:
    """Создает подключение к серверу через WinRM."""
    params = {
        'transport': 'ntlm',
        'target': radius_params.get('RADIUS_HOST'),
        'server_cert_validation': radius_params.get('RADIUS_SERVER_CERT_VALIDATION'),  # noqa
        'auth': (radius_params.get('RADIUS_USER'),
                 radius_params.get('RADIUS_PASSWORD'))
    }

    return CustomSession(**params)


def read_radius_users(radius_params: dict[str]) -> list[dict[str, str]]:
    """Читает учетные записи с сервера Radius."""
    session = get_radius_session(radius_params)
    result = session.run_ps(radius_params.get('RADIUS_SCRIPT'))
    result = result.std_out.decode()
    radius_users = []

    if not result:
        raise RadiusUsersNotFoundError('Не найдены пользователи в группе')

    for user in json.loads(result):
        user_status = 'active'
        if user['Disabled']:
            user_status = 'inactive'
        radius_users.append(
            {
                'fio': user.get('FullName'),
                'login': user.get('Name'),
                'status': user_status
            }
        )

    return radius_users


def block_radius_users(radius_params: dict[str]) -> None:
    """Блокирует учетные записи на сервере Radius."""
    users = Radius.get_users_to_block()
    need_disable = radius_params.get('RADIUS_NEED_DISABLE_USERS')

    if not users or not need_disable:
        return

    session = get_radius_session(radius_params)
    users_list = ','.join(f'"{user.login}"' for user in users)
    ps_script = f"""
    $users = @({users_list})
    foreach ($user in $users) {{
        Disable-LocalUser -Name $user
    }}
    """
    session.run_ps(ps_script)

    Radius.objects.bulk_update(users, ['status'])
    Radius.clear_users_for_blocking()


def get_counters(queryset: QuerySet, field: str) -> dict[str, str]:
    """Подсчитывает одинаковые элементы и их общее количество
    по определенному полю в queryset.
    """
    result = dict(Counter(item[field] for item in queryset if item[field]))
    result['total'] = sum(result.values())

    return result


def sorted_list(unsorted: dict[str, str]) -> list[str]:
    """Получает словарь возвращает отсортированный по значениям список."""
    return sorted(unsorted.items(), key=lambda item: item[1], reverse=True)

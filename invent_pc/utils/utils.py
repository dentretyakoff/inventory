import json
from collections import Counter

import winrm
from django.db.models import QuerySet
from django.conf import settings
from django.core.paginator import Paginator
from ldap3 import Server, Connection, SUBTREE

from exceptions.services import MissingVariableError, RadiusUsersNotFoundError
from .fix_router_os import routeros_api_fix

COUNT_PAGES = settings.COUNT_PAGES_PAGINATOR
AD_STATUS_DISABLED_USER = settings.AD_STATUS_DISABLED_USER


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
    ad_users = []

    with Connection(server, user=username, password=password) as conn:
        conn.bind()
        conn.search(base_dn, seatch_filter, SUBTREE, attributes=attrs)
        for user in conn.entries:
            if user.userAccountControl.value in AD_STATUS_DISABLED_USER:
                user_status = 'inactive'
            else:
                user_status = 'active'
            ad_users.append(
                {
                    'fio': user.cn.value,
                    'login': user.sAMAccountName.value,
                    'email': user.wWWHomePage.value,
                    'status': user_status
                }
            )

    return ad_users


def read_vpn_users(vpn_params: dict[str]) -> list[dict[str, str]]:
    """Читает учетные записи vpn из Mikrotik."""
    router_ip = vpn_params.get('VPN_HOST')
    username = vpn_params.get('VPN_USER')
    password = vpn_params.get('VPN_PASSWORD')

    connection = routeros_api_fix.RouterOsApiPool(
        host=router_ip,
        username=username,
        password=password,
        plaintext_login=True
    )
    api = connection.get_api()
    ppp_secrets = api.get_resource('/ppp/secret')
    secrets = ppp_secrets.get()
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
    connection.disconnect()

    return vpn_users


def read_radius_users(radius_params: dict[str]) -> list[dict[str, str]]:
    """Читает учетные записи с сервера Radius."""
    radius_host = radius_params.get('RADIUS_HOST')
    radius_user = radius_params.get('RADIUS_USER')
    radius_password = radius_params.get('RADIUS_PASSWORD')
    radius_script = radius_params.get('RADIUS_SCRIPT')

    session = winrm.Session(radius_host, auth=(radius_user, radius_password))
    result = session.run_ps(radius_script)
    result = result.std_out.decode('utf-8')
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

from django.conf import settings
from django.core.paginator import Paginator
from ldap3 import Server, Connection, SUBTREE

from exceptions.services import MissingVariableError

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

from django.conf import settings
from ldap3 import Server, Connection, SUBTREE

from utils.utils import check_envs
from .utils import update_or_create_users
from .models import ADUsers


AD_STATUS_DISABLED_USER = settings.AD_STATUS_DISABLED_USER


def update_ad() -> None:
    """Обновляет учетные записи AD."""
    ad_params = check_envs(settings.AD)
    ad_users = read_ad_users(ad_params)
    update_or_create_users(ADUsers, ad_users)


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

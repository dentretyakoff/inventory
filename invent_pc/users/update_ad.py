from django.conf import settings

from services.models import ActiveDirectory
from services.services import ADService
from .utils import update_or_create_users
from .models import ADUsers, StatusChoices


AD_STATUS_DISABLED_USER = settings.AD_STATUS_DISABLED_USER


def update_ad() -> None:
    """Обновляет учетные записи AD."""
    ad_servers = ActiveDirectory.objects.filter(active=True)
    service = ADService()
    ad_users = []
    for ad_server in ad_servers:
        with service.session(**ad_server.credentials()) as conn:
            result = service.get_users(
                session=conn,
                base_dn=ad_server.base_dn,
                seatch_filter=ad_server.seatch_filter
            )
            for user in result:
                user_attrs = user['attributes']
                email = None
                user_status = StatusChoices.INACTIVE
                status = user_attrs['userAccountControl']
                if status not in AD_STATUS_DISABLED_USER:
                    user_status = StatusChoices.ACTIVE
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
    if ad_users:
        update_or_create_users(ADUsers, ad_users)

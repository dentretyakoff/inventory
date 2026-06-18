import logging

from services.models import PfSense
from services.services import PfSenseService

from users.models import ADUsers, PfSenseUser, StatusChoices

from .utils import update_or_create_users

logger = logging.getLogger(__name__)


def update_pfsense():
    """Обновляет учетные записи pfSense."""
    pfsense_servers = PfSense.objects.filter(active=True)
    service = PfSenseService()
    pfsense_users = []

    for server in pfsense_servers:
        try:
            session = service.session(**server.credentials())
            result = service.get_users(session)
            for user in result:
                disabled = user.get('disabled', False)
                if isinstance(disabled, str):
                    disabled = disabled.lower() in ('true', '1', 'yes')

                user_status = (
                    StatusChoices.INACTIVE if disabled
                    else StatusChoices.ACTIVE
                )

                pfsense_users.append({
                    'login': user.get('name'),
                    'description': user.get('descr') or '',
                    'disabled': disabled,
                    'status': user_status,
                    'pfsense_id': (user.get('id')
                                   if user.get('id') is not None else None),
                })
        except Exception as error:
            logger.exception(
                f'Ошибка при получении пользователей pfSense '
                f'с {server.host}: {error}'
            )

    if pfsense_users:
        update_or_create_users(PfSenseUser, pfsense_users)
        match_pfsense_users()
    block_pfsense_users()


def block_pfsense_users() -> None:
    """Блокирует учетные записи pfSense на сервере."""
    pfsense_servers = PfSense.objects.filter(active=True)
    service = PfSenseService()
    for server in pfsense_servers:
        session = service.session(**server.credentials())
        service.block_users(session, server.need_disable)


def match_pfsense_users() -> None:
    """Сопоставляет pfSense с учетными записями AD по логину."""
    no_pfsense_users = ADUsers.objects.filter(pfsense=None)
    pfsense_users = PfSenseUser.objects.filter(
        ad_user__isnull=True,
        login__isnull=False
    )

    pfsense_by_login = {
        user.login.lower(): user
        for user in pfsense_users
    }

    updated_users = []

    for ad_user in no_pfsense_users:
        pfsense_user = pfsense_by_login.get(ad_user.login.lower())
        if pfsense_user:
            ad_user.pfsense = pfsense_user
            updated_users.append(ad_user)

    if updated_users:
        ADUsers.objects.bulk_update(updated_users, ('pfsense',))

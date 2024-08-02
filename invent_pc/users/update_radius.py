import json

from services.models import RadiusServer
from services.services import RadiusService
from users.models import Radius, ADUsers, StatusChoices
from .utils import update_or_create_users


def update_radius():
    """Обновляет учетные записи Radius."""
    radius_servers = RadiusServer.objects.filter(active=True)
    service = RadiusService()
    radius_users = []
    for radius_server in radius_servers:
        session = service.session(**radius_server.credentials())
        result = service.get_users(
            session, radius_server.read_users_ps_script)
        for user in json.loads(result):
            user_status = StatusChoices.ACTIVE
            if user['Disabled']:
                user_status = StatusChoices.INACTIVE
            radius_users.append(
                {
                    'fio': user.get('FullName'),
                    'login': user.get('Name'),
                    'status': user_status
                }
            )
    if radius_users:
        update_or_create_users(Radius, radius_users)
        match_radius_users()
    block_radius_users()


def block_radius_users() -> None:
    """Блокирует учетные записи на сервере Radius."""
    radius_servers = RadiusServer.objects.filter(active=True)
    service = RadiusService()
    for radius_server in radius_servers:
        session = service.session(**radius_server.credentials())
        service.block_users(session, radius_server.need_disable)


def match_radius_users() -> None:
    """Сопоставляет Radius с учетными записями AD."""
    no_radius_users = ADUsers.objects.filter(rdlogin=None)
    radius_users = Radius.objects.filter(
        ad_user__isnull=True,
        fio__isnull=False
    )

    updated_users = []

    for no_radius_user in no_radius_users:
        for radius_user in radius_users:
            if (no_radius_user.fio == radius_user.fio
                    or no_radius_user.login == radius_user.login):
                no_radius_user.rdlogin = radius_user
                updated_users.append(no_radius_user)

    ADUsers.objects.bulk_update(updated_users, ('rdlogin',))

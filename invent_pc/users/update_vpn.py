from services.models import Mikrotik
from services.services import MikrotikService
from users.models import VPN, ADUsers, StatusChoices
from .utils import update_or_create_users


def update_vpn():
    """Обновляет учетные записи VPN."""
    mikrotiks = Mikrotik.objects.filter(active=True)
    service = MikrotikService()
    vpn_users = []
    for mikrotik in mikrotiks:
        with service.session(**mikrotik.credentials()) as conn:
            result = service.get_users(conn)
            for secret in result:
                user_status = StatusChoices.ACTIVE
                if secret['disabled'] == 'true':
                    user_status = StatusChoices.INACTIVE
                vpn_users.append(
                    {
                        'login': secret.get('name'),
                        'comment': secret.get('comment'),
                        'status': user_status
                    }
                )
    if vpn_users:
        update_or_create_users(VPN, vpn_users)
        match_vpn_users()
    block_vpn_users()


def block_vpn_users() -> None:
    """Блокирует учетные записи VPN в mikrotik."""
    mikrotiks = Mikrotik.objects.filter(active=True)
    service = MikrotikService()
    for mikrotik in mikrotiks:
        with service.session(**mikrotik.credentials()) as conn:
            service.block_users(conn, mikrotik.need_disable)


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

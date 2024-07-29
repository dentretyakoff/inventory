import json

from django.conf import settings

from users.models import Radius, ADUsers
from utils.fix_pywinrm import CustomSession
from exceptions.services import RadiusUsersNotFoundError
from utils.utils import check_envs
from .utils import update_or_create_users


def update_radius():
    """Обновляет учетные записи Radius."""
    radius_params = check_envs(settings.RADIUS)
    radius_users = read_radius_users(radius_params)
    update_or_create_users(Radius, radius_users)
    match_radius_users()
    block_radius_users(radius_params)


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

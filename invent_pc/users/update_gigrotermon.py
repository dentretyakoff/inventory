from django.db.models import Model

from services.services import GigrotermonService
from services.models import MySQLDatabase
from users.models import StatusChoices, Gigrotermon, ADUsers


def update_gigrotermon():
    """Обновляет учетные записи Gigrotermon."""
    databases = MySQLDatabase.objects.filter(active=True)
    service = GigrotermonService()
    gigro_users = []
    for db in databases:
        with service.session(**db.to_dict()) as conn:
            result = service.get_users(conn)
            for gigro_id, login, gigro_status in result:
                status = StatusChoices.ACTIVE
                if gigro_status == '5':
                    status = StatusChoices.INACTIVE
                gigro_users.append(
                    {
                        'login': login,
                        'status': status,
                        'gigro_id': gigro_id,
                        'db': db,
                    }
                )
    update_or_create_gigro_users(Gigrotermon, gigro_users)
    match_gigro_users()


def update_or_create_gigro_users(
        model: Model, users_data: list[dict[str, str]]) -> None:
    """Обновляет пользователей или создает новых,
    используя уникальную пару полей login и db."""
    existing_users = {
        (user.login, user.db): user for user in model.objects.all()
    }
    new_users = []

    for user_data in users_data:
        login = user_data.pop('login')
        db = user_data.pop('db')
        user = existing_users.pop((login, db), None)
        user_data['successfully_updated'] = True

        if not user:
            new_users.append(model(login=login, db=db, **user_data))
        elif user.needs_update(user_data):
            user.save()

    if existing_users:
        for existing_user in existing_users.values():
            existing_user.successfully_updated = False
        model.objects.bulk_update(existing_users.values(),
                                  ['successfully_updated'])

    if new_users:
        model.objects.bulk_create(new_users)


def match_gigro_users() -> None:
    """Сопоставляет Gigrotermon с учетными записями AD."""
    gigro_users = Gigrotermon.objects.filter(ad_user__isnull=True)
    logins = [user.login for user in gigro_users]
    ad_users_dict = {
        ad_user.login: ad_user
        for ad_user in ADUsers.objects.filter(login__in=logins)
    }
    updated_users = []

    for gigro_user in gigro_users:
        ad_user = ad_users_dict.get(gigro_user.login)
        if ad_user:
            gigro_user.ad_user = ad_user
            updated_users.append(gigro_user)

    if updated_users:
        Gigrotermon.objects.bulk_update(updated_users, ('ad_user',))

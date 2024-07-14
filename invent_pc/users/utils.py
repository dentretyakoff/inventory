from django.db.models import Model


def update_or_create_users(
        model: Model, users_data: list[dict[str, str]]) -> None:
    """Обновляет пользователей или создает новых."""
    for user_data in users_data:
        login = user_data.pop('login')
        _, _ = model.objects.update_or_create(login=login, defaults=user_data)

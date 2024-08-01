from django.conf import settings
from django.contrib import admin, messages

from exceptions.services import EncryptionKeyMissingError
from .models import MySQLDatabase


class BaseServiceAdmin(admin.ModelAdmin):
    """Базовый класс админки для сервисов."""
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if not settings.ENCRYPTION_KEY:
            messages.warning(
                request,
                'Ключ шифрования не заполнен. Сервис не может быть сохранен. '
                'Заполните ENCRYPTION_KEY в файле .env')
        return form

    def save_model(self, request, obj, form, change):
        try:
            obj.save()
        except EncryptionKeyMissingError as e:
            messages.error(request, (f'Ошибка шифрования пароля: {str(e)}'))


@admin.register(MySQLDatabase)
class MySQLDatabaseAdmin(BaseServiceAdmin):
    list_display = (
        'id',
        'name',
        'host',
        'port',
        'user',
        'database',
        'active'
    )
    fields = (
        'name',
        'host',
        'port',
        'user',
        'password',
        'database',
        'active'
    )
    list_display_links = ('id', 'name')
    search_fields = ('name',)
    list_filter = ('active',)

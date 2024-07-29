from django.contrib import admin

from .models import MySQLDatabase


@admin.register(MySQLDatabase)
class MySQLDatabaseAdmin(admin.ModelAdmin):
    list_display = [field.name for field in MySQLDatabase._meta.fields]
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

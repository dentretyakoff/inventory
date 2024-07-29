from django.contrib import admin

from comps.admin import NoAddAdmin
from .models import ADUsers, Radius, VPN, Gigrotermon


@admin.register(ADUsers)
class ADuserAdmin(NoAddAdmin):
    fields = (
        'fio',
        'login',
        'email',
        'status',
        'rdlogin',
        'vpn'
    )
    list_display_links = ('id', 'fio')
    search_fields = (
        'fio',
        'login',
        'email',
    )
    list_filter = ('status',)


@admin.register(Radius)
class RadiusAdmin(NoAddAdmin):
    fields = (
        'fio',
        'login',
        'status',
    )
    list_display_links = ('id', 'fio')
    search_fields = (
        'fio',
        'login',
    )
    list_filter = ('status',)


@admin.register(VPN)
class VPNAdmin(NoAddAdmin):
    fields = (
        'login',
        'comment',
        'status',
    )
    list_display_links = ('id', 'login')
    search_fields = (
        'login',
        'comment',
    )
    list_filter = ('status',)


@admin.register(Gigrotermon)
class GigrotermonAdmin(NoAddAdmin):
    fields = (
        'login',
        'status',
        'db',
        'gigro_id',
        'ad_user'
    )
    list_display_links = ('id', 'login')
    search_fields = (
        'login',
        'db__name',
    )
    list_filter = ('status', 'db')

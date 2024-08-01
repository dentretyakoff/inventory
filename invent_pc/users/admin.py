from django.contrib import admin

from .models import ADUsers, Radius, VPN, Gigrotermon


class NoAddAdmin(admin.ModelAdmin):
    def __init__(self, model, admin_site):
        self.list_display = [field.name for field in model._meta.fields]
        self.readonly_fields = [field.name for field in model._meta.fields]
        self.list_filter = ('status', 'successfully_updated')
        self.list_display_links = ('id', 'login')
        super().__init__(model, admin_site)

    def has_add_permission(self, request):
        return False


@admin.register(ADUsers)
class ADuserAdmin(NoAddAdmin):
    fields = (
        'fio',
        'login',
        'email',
        'status',
        'rdlogin',
        'vpn',
        'successfully_updated'
    )
    search_fields = (
        'fio',
        'login',
        'email',
    )


@admin.register(Radius)
class RadiusAdmin(NoAddAdmin):
    fields = (
        'fio',
        'login',
        'status',
        'successfully_updated'
    )
    search_fields = (
        'fio',
        'login',
    )


@admin.register(VPN)
class VPNAdmin(NoAddAdmin):
    fields = (
        'login',
        'comment',
        'status',
        'successfully_updated'
    )
    search_fields = (
        'login',
        'comment',
    )


@admin.register(Gigrotermon)
class GigrotermonAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'login',
        'status',
        'successfully_updated',
        'db',
        'gigro_id',
        'ad_user',
    )
    fields = (
        'login',
        'status',
        'db',
        'gigro_id',
        'ad_user',
        'successfully_updated'
    )
    list_display_links = ('id', 'login')
    readonly_fields = (
        'login',
        'status',
        'db',
        'gigro_id',
        'successfully_updated'
    )
    search_fields = (
        'login',
        'db__name',
    )
    list_filter = ('status', 'db', 'successfully_updated')

    def has_add_permission(self, request):
        return False

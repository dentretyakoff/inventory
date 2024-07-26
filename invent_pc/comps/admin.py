from django.contrib import admin

from .models import (Comp, Department, Disk, Host, HostVirtualMachine, Monitor,
                     Ram, VirtualMachine, VMAdapter, WebCamera)


class HostVMInline(admin.TabularInline):
    model = HostVirtualMachine
    extra = 0
    min_num = 1
    fields = ('vm',)


class VMAdapterInline(admin.TabularInline):
    model = VMAdapter
    extra = 0
    min_num = 1
    fields = ('mac', 'vlan')


class NoAddAdmin(admin.ModelAdmin):
    def __init__(self, model, admin_site):
        self.list_display = [field.name for field in model._meta.fields]
        self.readonly_fields = [field.name for field in model._meta.fields]
        super().__init__(model, admin_site)

    def has_add_permission(self, request):
        return False


@admin.register(Comp)
class CompAdmin(NoAddAdmin):
    list_display_links = ('id', 'pc_name')
    search_fields = ('pc_name', 'web_camera__model')
    list_filter = ('win_ver',)


@admin.register(Disk)
class DiskAdmin(NoAddAdmin):
    list_display_links = ('id', 'model')
    search_fields = ('model', 'comp__pc_name')
    list_filter = ('status', 'capacity')


@admin.register(Ram)
class RamAdmin(NoAddAdmin):
    list_display_links = ('id', 'model')
    search_fields = ('model', 'comp__pc_name')
    list_filter = ('status', 'capacity')


@admin.register(Monitor)
class MonitorAdmin(NoAddAdmin):
    list_display_links = ('id', 'model')
    search_fields = ('model', 'comp__pc_name')
    list_filter = ('status', 'manufacturer')


@admin.register(WebCamera)
class WebCameraAdmin(NoAddAdmin):
    list_display_links = ('id', 'model')
    search_fields = ('model', 'comp__pc_name')


@admin.register(Department)
class DepartmentAdmin(NoAddAdmin):
    list_display_links = ('id', 'name')
    search_fields = ('model', 'comp__pc_name')


@admin.register(Host)
class HostAdmin(NoAddAdmin):
    list_display_links = ('id', 'name')
    inlines = (HostVMInline,)
    search_fields = ('name', 'host_vm__vm__name')


@admin.register(VirtualMachine)
class VirtualMachineAdmin(NoAddAdmin):
    list_display_links = ('id', 'name')
    inlines = (VMAdapterInline,)
    search_fields = ('name', 'host_vm__host__name')

from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.db.models import Count, Q

from .models import (Comp, Disk, ItemsChoices,
                     Monitor, Ram, Department,
                     Host, VirtualMachine)
from .filters import CompFilter, DiskFilter, RamFilter, MonitorFilter
from .forms import DepartmentFilterForm
from utils.utils import get_pages, get_counters, sorted_list


@login_required
def index(request):
    """Список всех компьютеров."""
    filter_form = DepartmentFilterForm(request.GET)
    comps_filter = CompFilter(request.GET, queryset=Comp.objects.all())

    page_obj = get_pages(request, comps_filter.qs)
    current_query_params = request.GET.copy()
    current_query_params.pop('page', None)

    context = {
        'page_obj': page_obj,
        'filter_form': filter_form,
        'current_query_params': current_query_params,
        'comps_count': comps_filter.qs.count(),
    }

    return render(request, 'comps/index.html', context)


@login_required
def comp_detail(request, pc_name):
    """Детальная информация о компьютере."""
    comp = get_object_or_404(Comp, pc_name=pc_name)
    context = {
        'comp': comp,
    }
    return render(request, 'comps/comp_detail.html', context)


@login_required
def comp_delete(request, pc_name):
    """Удалить компьютер."""
    comp = get_object_or_404(Comp, pc_name=pc_name)
    comp.delete()
    return redirect('comps:index')


@login_required
def item_edit(request, pc_name, item, item_status, item_id):
    """Подтверждение установки/снятие диска на компьютере."""
    models = {
        'disk': Disk,
        'ram': Ram,
        'monitor': Monitor,
    }
    model = models[item]
    item = get_object_or_404(model, pk=item_id)

    if item_status == ItemsChoices.INSTALLED:
        item.install_date = timezone.now()
        item.uninstall_date = None
        item.status = ItemsChoices.INSTALLED

    if item_status == ItemsChoices.UNINSTALLED:
        item.uninstall_date = timezone.now()
        item.status = ItemsChoices.UNINSTALLED

    item.save()

    return redirect('comps:comp_detail', pc_name=pc_name)


@login_required
def reports(request):
    """Общая статистика."""
    filter_form = DepartmentFilterForm(request.GET)
    comps_filter = CompFilter(request.GET, queryset=Comp.objects.all())
    disk_filter = DiskFilter(request.GET, queryset=Disk.objects.filter())
    ram_filter = RamFilter(request.GET, queryset=Ram.objects.filter())
    monitor_filter = MonitorFilter(
        request.GET, queryset=Monitor.objects.filter())

    items = [('motherboard', comps_filter.qs),
             ('win_ver', comps_filter.qs),
             ('os_arch', comps_filter.qs),
             ('cpu', comps_filter.qs),
             ('disks', disk_filter.qs),
             ('rams', ram_filter.qs),
             ('monitors', monitor_filter.qs)]

    context = {
        'comps_count': comps_filter.qs.count(),
        'filter_form': filter_form,
    }

    for item, queryset in items:
        if item in ['disks', 'rams', 'monitors']:
            count_by_item = get_counters(queryset.values('model'), 'model')
        else:
            count_by_item = get_counters(queryset.values(item), item)
        context[f'count_by_{item}'] = sorted_list(count_by_item)

    return render(request, 'comps/reports.html', context)


@login_required
def comps_by_item(request, item_type):
    """Список компьютеров с выбранным оборудованием."""
    item = request.GET.get('item')
    department_id = request.GET.get('department')
    filter_form = DepartmentFilterForm(request.GET)
    item_types = {
        'os_arch': Q(os_arch=item),
        'motherboard': Q(motherboard=item),
        'win_ver': Q(win_ver=item),
        'cpu': Q(cpu=item),
        'disk': Q(disks__model=item, disks__status=ItemsChoices.INSTALLED),
    }
    comps = Comp.objects.filter(item_types.get(item_type, Q()))
    if item_type == 'disk':
        comps = comps.distinct()
    if department_id:
        comps = comps.filter(department=department_id)

    page_obj = get_pages(request, comps)
    current_query_params = request.GET.copy()
    current_query_params.pop('page', None)

    context = {'page_obj': page_obj,
               'filter_form': filter_form,
               'item': item,
               'current_query_params': current_query_params}

    return render(request, 'comps/comps_by_items.html', context)


@login_required
def departments(request):
    """Список отделов с количеством компов."""
    departments = Department.objects.all().order_by('name')
    context = {'departments': departments}
    return render(request, 'comps/departments.html', context)


@login_required
def department_delete(request, department_id):
    """Удалить департамент."""
    department = get_object_or_404(Department, id=department_id)
    department.delete()
    return redirect('comps:departments')


@login_required
def vms(request):
    """Список хостов с виртуальными машинами."""
    hosts = Host.objects.all().prefetch_related(
        'vms').annotate(vms_count=Count('vms')).order_by('-vms_count')
    # Удаление виртуальных машине не имеющих связи с хостами
    VirtualMachine.objects.filter(host_vm__isnull=True).delete()
    vms_count = sum([host.vms_count for host in hosts])
    context = {'hosts': hosts,
               'vms_count': vms_count}
    return render(request, 'comps/vms.html', context)

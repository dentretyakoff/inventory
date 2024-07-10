from collections import Counter

from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.db.models import Count, Q

from .models import (Comp, Disk, ItemsChoices,
                     Monitor, Ram, Department,
                     Host, VirtualMachine)
from .filters import CompFilter
from .forms import DepartmentFilterForm
from .utils import get_pages


def index(request):
    """Список всех компьютеров."""
    filter_form = DepartmentFilterForm(request.GET)
    comps_filter = CompFilter(request.GET, queryset=Comp.objects.all())

    # Не использовать пагинацию для фильтров.
    if request.GET and not request.GET.get('page'):
        page_obj = get_pages(request, comps_filter.qs,
                             len(comps_filter.qs)+1)
    else:
        page_obj = get_pages(request, comps_filter.qs)

    context = {
        'page_obj': page_obj,
        'filter_form': filter_form,
    }

    return render(request, 'comps/index.html', context)


def comp_detail(request, pc_name):
    "Детальная информация о компьютере."
    comp = get_object_or_404(Comp, pc_name=pc_name)
    context = {
        'comp': comp,
    }
    return render(request, 'comps/comp_detail.html', context)


def comp_delete(request, pc_name):
    "Удалить компьютер."
    comp = get_object_or_404(Comp, pc_name=pc_name)
    comp.delete()
    return redirect('comps:index')


def item_edit(request, pc_name, item, item_status, item_id):
    "Подтверждение установки/снятие диска на компьютере."
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


def reports(request):
    """Общая статистика."""
    department_id = request.GET.get('department')
    filter_form = DepartmentFilterForm(request.GET)
    if department_id:
        comps = Comp.objects.filter(department=department_id)
        disks = Disk.objects.filter(status=ItemsChoices.INSTALLED,
                                    comp__department=department_id)
    else:
        comps = Comp.objects.all()
        disks = Disk.objects.filter(status=ItemsChoices.INSTALLED)
    count_by_motherboard = dict(Counter(
        item['motherboard'] for item in comps.values('motherboard')))
    count_by_win_ver = dict(Counter(
        item['win_ver'] for item in comps.values('win_ver')))
    count_by_os_arch = dict(Counter(
        item['os_arch'] for item in comps.values('os_arch')))
    count_by_cpu = dict(Counter(
        item['cpu'] for item in comps.values('cpu')))
    count_by_disks = dict(Counter(
        item['model'] for item in disks.values('model')))
    context = {
        'comps_count': comps.count(),
        'count_by_motherboard': count_by_motherboard,
        'count_by_win_ver': count_by_win_ver,
        'count_by_os_arch': count_by_os_arch,
        'count_by_cpu': count_by_cpu,
        'count_by_disks': count_by_disks,
        'filter_form': filter_form,
    }
    return render(request, 'comps/reports.html', context)


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
    page_obj = get_pages(request, comps, len(comps)+1)
    context = {'page_obj': page_obj,
               'filter_form': filter_form,
               'item': item}
    return render(request, 'comps/comps_by_items.html', context)


def departments(request):
    """Список отделов с количеством компов."""
    departments = Department.objects.all().order_by('name')
    context = {'departments': departments}
    return render(request, 'comps/departments.html', context)


def department_delete(request, department_id):
    """Удалить департамент."""
    department = get_object_or_404(Department, id=department_id)
    department.delete()
    return redirect('comps:departments')


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

import json
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from rest_framework import status

from utils.utils import get_pages

from .models import ADUsers, Radius, VPN
from .filters import UsersFilter


def users_main(request):
    """Список всех учетных записей из AD."""
    user_filter = UsersFilter(
        request.GET,
        queryset=ADUsers.objects.all().select_related('rdlogin', 'vpn')
    )

    # Не использовать пагинацию для фильтров.
    if request.GET and not request.GET.get('page'):
        page_obj = get_pages(request, user_filter.qs,
                             len(user_filter.qs)+1)
    else:
        page_obj = get_pages(request, user_filter.qs)

    context = {
        'page_obj': page_obj,
    }

    return render(request, 'users/users.html', context)


@csrf_exempt
def edit_user(request):
    """Редактирование связаных учетных записей пользователя."""
    if request.method == 'POST':
        ad_user_id = request.POST.get('ad_user_id')
        login_id = request.POST.get('rdlogin_id') or request.POST.get('vpn_id')
        field = request.POST.get('field')
        ad_user = ADUsers.objects.get(id=ad_user_id)
        setattr(ad_user, field, login_id)
        ad_user.save()
        return JsonResponse({'success': True}, status=status.HTTP_200_OK)

    if request.method == 'DELETE':
        body = json.loads(request.body.decode('utf-8'))
        ad_user_id = body.get('ad_user_id')
        ad_user = ADUsers.objects.get(id=ad_user_id)
        field = body.get('field')
        setattr(ad_user, field, None)
        ad_user.save()
        return JsonResponse({'success': True}, status=status.HTTP_200_OK)

    return JsonResponse({'success': False},
                        status=status.HTTP_405_METHOD_NOT_ALLOWED)


def get_rdlogins(request):
    """Получить список доступных учетных записей Radius."""
    rdlogins = list(Radius.objects.filter(ad_user=None).values('id', 'login'))
    return JsonResponse(rdlogins, safe=False)


def get_vpns(request):
    """Получить список доступных учетных записей VPN."""
    vpns = list(VPN.objects.filter(ad_user=None).values('id', 'login'))
    return JsonResponse(vpns, safe=False)

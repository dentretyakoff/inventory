import json

from django.conf import settings
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from ldap3.core.exceptions import LDAPSocketOpenError
from rest_framework import status

from exceptions.services import MissingVariableError
from utils.utils import check_envs, get_pages, read_ad_users

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


def update_ad_users_data(request):
    """Обновить данные учетных записей пользователей Active Directory."""
    try:
        ad_params = check_envs(settings.AD)
        ad_users = read_ad_users(ad_params)
        for ad_user in ad_users:
            login = ad_user.pop('login')
            _, _ = ADUsers.objects.update_or_create(
                login=login,
                defaults=ad_user
            )
    except MissingVariableError as error:
        return JsonResponse(
            {'success': False, 'error': error.__str__()},
            status=status.HTTP_400_BAD_REQUEST
        )
    except LDAPSocketOpenError as error:
        return JsonResponse(
            {'success': False, 'error': error.__str__()},
            status=status.HTTP_400_BAD_REQUEST
        )
    except Exception as error:
        return JsonResponse(
            {'success': False, 'error': error.__str__()},
            status=status.HTTP_400_BAD_REQUEST
        )
    return JsonResponse({'success': True}, status=status.HTTP_200_OK)

from django.urls import path

from . import views

app_name = 'users'


urlpatterns = [
    path('edit-user/', views.edit_user, name='edit_user'),
    path('get-rdlogins/', views.get_rdlogins, name='get_rdlogins'),
    path('get-vpns/', views.get_vpns, name='get_vpns'),
    path('update-users-data/',
         views.update_users_data,
         name='update_users_data'),
    path('', views.users_main, name='users_main'),
]

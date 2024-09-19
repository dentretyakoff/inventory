from django.urls import path
from django.contrib.auth import views as auth_views

from . import views

app_name = 'users'


urlpatterns = [
    path('edit-user/', views.edit_user, name='edit_user'),
    path('get-rdlogins/', views.get_rdlogins, name='get_rdlogins'),
    path('get-vpns/', views.get_vpns, name='get_vpns'),
    path('update-users-data/',
         views.update_users_data,
         name='update_users_data'),
    path('generate-users-report/',
         views.generate_users_report,
         name='generate_users_report'),
    path('generate-radius-report/',
         views.generate_radius_report,
         name='generate_radius_report'),
    path('generate-vpn-report/',
         views.generate_vpn_report,
         name='generate_vpn_report'),
    path('login/', auth_views.LoginView.as_view(
        template_name='users/registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(
        template_name='users/registration/logged_out.html'), name='logout'),
    path('ad/', views.users_main, name='users_main'),
    path('radius/', views.users_radius, name='users_radius'),
    path('vpn/', views.users_vpn, name='users_vpn'),
    path('gigro/', views.users_gigro, name='users_gigro'),
    path('update-expiration-date/',
         views.update_expiration_date,
         name='update_expiration_date'),
]

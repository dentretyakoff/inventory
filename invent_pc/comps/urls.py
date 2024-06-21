from django.urls import path

from . import views

app_name = 'comps'


urlpatterns = [
    path('', views.index, name='index'),
    path('reports/',
         views.reports, name='reports'),
    path('comps_by_item/<slug:item_type>/',
         views.comps_by_item, name='comps_by_item'),
    path('departments/',
         views.departments, name='departments'),
    path('vms/', views.vms, name='vms'),
    path('departments/<int:department_id>/delete',
         views.department_delete, name='department_delete'),
    path('<str:pc_name>/', views.comp_detail, name='comp_detail'),
    path('<str:pc_name>/<str:item>/<slug:item_status>/<int:item_id>',
         views.item_edit, name='item_edit'),
    path('<str:pc_name>/delete/',
         views.comp_delete, name='comp_delete'),
]

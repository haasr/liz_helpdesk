from django.urls import path
from . import views

urlpatterns = [
    path('', views.asset_list, name='asset_list'),
    path('create/', views.asset_create, name='asset_create'),
    path('<str:inventory_number>/', views.asset_detail, name='asset_detail'),
    path('<str:inventory_number>/update/', views.asset_update, name='asset_update'),
    path('<str:inventory_number>/delete/', views.asset_delete, name='asset_delete'),
]

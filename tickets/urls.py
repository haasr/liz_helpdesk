from django.urls import path
from . import views
from . import views_technician

urlpatterns = [
    # Public ticket URLs
    path('submit/', views.submit_ticket, name='submit_ticket'),
    path('confirmation/<str:ticket_number>/', views.ticket_confirmation, name='ticket_confirmation'),
    path('access/', views.access_ticket, name='access_ticket'),
    path('view/<str:ticket_number>/', views.view_ticket, name='view_ticket'),

    # Technician URLs
    path('dashboard/', views_technician.dashboard, name='technician_dashboard'),
    path('manage/<str:ticket_number>/', views_technician.manage_ticket, name='manage_ticket'),
    path('assign/<str:ticket_number>/', views_technician.self_assign_ticket, name='self_assign_ticket'),
    path('manage/<str:ticket_number>/add-asset/', views_technician.add_asset_to_ticket, name='add_asset_to_ticket'),
]
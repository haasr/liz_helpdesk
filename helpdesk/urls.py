from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required

def root_redirect(request):
    """Redirect root URL based on authentication status"""
    if request.user.is_authenticated:
        return redirect('technician_dashboard')
    return redirect('submit_ticket')

urlpatterns = [
    # Root URL handler
    path('', root_redirect, name='root'),

    # Admin
    path('admin/', admin.site.urls),

    # Include app URLs
    path('', include('tickets.urls')),
    path('accounts/', include('accounts.urls')),
    path('assets/', include('assets.urls'))
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
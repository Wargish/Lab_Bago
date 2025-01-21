
from django.contrib import admin
from django.urls import path, include

def trigger_error(request):
    division_by_zero = 1 / 0

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('app.urls')),
    path('auth/', include('authentication.urls')),
    path('externos/', include('external_workers.urls')),
    path('internos/', include('internal_workers.urls')),
    path('mant_preventivo/', include('mant_preventivo.urls')),
    path('sentry-debug/', trigger_error),
]



from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('app.urls')),
    path('auth/', include('authentication.urls')),
    path('externos/', include('external_workers.urls')),
    path('internos/', include('internal_workers.urls')),
    path('mant_preventivo/', include('mant_preventivo.urls')),
]


from django.contrib import admin
from django.urls import path, include

from django.conf import settings
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('inventory.urls')),
    path('api/', include('inventory.api_urls')),
]

if settings.DEBUG:
    urlpatterns += staticfiles_urlpatterns()

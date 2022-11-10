from django.contrib import admin
from django.urls import path,include
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('site-admin-access/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),
    path('accounts/', include('users.urls')),
    path("", include("company.urls")),
    path('', include('core.urls')),
    path('accounts/', include('wallet.urls')),
]

if settings.DEBUG :
    urlpatterns += static(settings.MEDIA_URL,document_root = settings.MEDIA_ROOT)


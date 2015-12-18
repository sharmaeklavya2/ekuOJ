from django.conf.urls import include, url, static
from django.contrib import admin

urlpatterns = [
	url(r'^admin/', include(admin.site.urls)),
	url(r'^account/', include('account.urls', namespace='account')),
	url(r'^', include('main.urls', namespace='main')),
]

from . import settings

if settings.DEBUG:
	urlpatterns+= static.static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

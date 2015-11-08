from django.conf.urls import url
from . import views

urlpatterns = [
	url(r'^$', views.index, name='index'),
	url(r'^submit/(?P<ccode>\w+)/(?P<pcode>\w+)/$', views.submit, name='submit'),
	url(r'^status/submission/(?P<sid>\w+)/$', views.submission_status, name='submission_status'),
]

from django.conf.urls import url
from . import views

urlpatterns = [
	url(r'^$', views.index, name='index'),
	url(r'^submit/(?P<ccode>\w+)/(?P<pcode>\w+)/$', views.submit, name='submit'),
	url(r'^view/(?P<ccode>\w+)/(?P<pcode>\w+)/$', views.view_problem, name='view_problem'),
	url(r'^view/(?P<ccode>\w+)/$', views.view_contest, name='view_contest'),
	url(r'^status/submission/(?P<sid>\w+)/$', views.submission_status, name='submission_status'),
	url(r'^status/', views.status, name='status'),
]

from django.conf.urls import url
from . import views

urlpatterns = [
	url(r'^$', views.index, name='index'),
	url(r'^login/$', views.login_view, name='login'),
	url(r'^logout/$', views.logout_view, name='logout'),
	url(r'^register/$', views.register, name='register'),
	url(r'^account_info/$', views.account_info, name='account_info'),
	url(r'^user/(?P<username>\w+)/$', views.public_profile, name='public_profile'),
	url(r'^user-list/$', views.user_list, name='user_list'),
	url(r'^edit-profile/$', views.edit_profile, name='edit_profile'),
	url(r'^change-password/$', views.change_password, name='change_password'),
]

from django.conf.urls import patterns, include, url
from alpha import views

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'veritaslist.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

	url(r'^$', views.index, name='index'),
	url(r'^listcreator/$', views.listcreator, name='listcreator'),
	url(r'^handle_post/$', views.handle_post, name='handle_post'),
	url(r'^success/$', views.success, name='success'),

	url(r'^(?P<list_id>\d+)/$', views.detail, name='detail'),
)

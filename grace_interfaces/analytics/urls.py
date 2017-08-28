from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.homepage, name='homepage'),
    url(r'^homepage', views.homepage, name = 'homepage'),
    url(r'^main/(?P<netid>[A-Za-z0-9_]+)/', views.main, name = 'main'),
    url(r'^image/(?P<netid>[A-Za-z0-9_]+)/', views.image, name = 'image'),
    url(r'^network/(?P<netid>[A-Za-z0-9_]+)/(?P<dataid>[0-9_]+)', views.network, name = 'network'),
    url(r'^writing/(?P<netid>[A-Za-z0-9_]+)/(?P<dataid>[0-9_]+)', views.network, name = 'network'),
    url(r'^logout/$', views.user_logout, name='logout'),
]

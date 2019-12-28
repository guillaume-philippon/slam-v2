from django.urls import path, re_path

from . import views

urlpatterns = [
    path('', views.networks_view, name='networks'),
    re_path(r'(?P<uri_network>[\w\.\-]+)/(?P<uri_host>[\w\.\-]+)$', views.host_view,
            name='network'),
    re_path(r'(?P<uri_network>[\w\.\-]+)$', views.network_view, name='network'),
]

from django.urls import path, re_path

from . import views

urlpatterns = [
    path('', views.networks_view, name='networks'),
    re_path(r'(?P<uri_network>[\w\.\-]+)/(?P<uri_address>[\w\.\-]+)$', views.address_view,
            name='address'),
    re_path(r'(?P<uri_network>[\w\.\-]+)$', views.network_view, name='network'),
]

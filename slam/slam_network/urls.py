"""
This modules is the URL dispatcher for networks. We have 3 different route
 - https://slam.example.com/networks: to act on all networks
 - https://slam.example.com/networks/name: to act on a network
 - https://slam.example.com/networks/name/ip-address: to act on ip address in network

urlpatterns do not respect pylint name style, so we disable C0103 (invalid-name) check on this file
"""
# pylint: disable=C0103
from django.urls import path, re_path

from . import views

urlpatterns = [
    path('', views.networks_view, name='networks'),
    re_path(r'(?P<uri_network>[\w\.\-]+)/(?P<uri_address>[\w\.\-]+)/(?P<uri_entry>[\w\.\-]+)$',
            views.entry_view, name='entry'),
    re_path(r'(?P<uri_network>[\w\.\-]+)/(?P<uri_address>[\w\.\-]+)$', views.address_view,
            name='address'),
    re_path(r'(?P<uri_network>[\w\.\-]+)$', views.network_view, name='network'),
]

"""
This modules is the URL dispatcher for hosts. We have 2 different route
 - https://slam.example.com/hosts: to act on all hosts
 - https://slam.example.com/hosts/fqdn: to act on fqdn

urlpatterns do not respect pylint name style, so we disable C0103 (invalid-name) check on this file
"""
# pylint: disable=C0103
from django.urls import path, re_path
from . import views

urlpatterns = [
    path('', views.hosts_view, name='hosts'),
    # re_path(r'(?P<uri_hardware>[\w\.\-]+)/(?P<uri_interface>[\w:]+)$',
    #        views.host_view,
    #        name='host'),
    re_path(r'(?P<uri_host>[\w\.\-:]+)$', views.host_view, name='host'),
]

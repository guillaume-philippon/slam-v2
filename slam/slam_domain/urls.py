"""
This modules is the URL dispatcher for domain. We have 3 different route
 - https://slam.example.com/domains: to act on all domains
 - https://slam.example.com/domains/example.com: to act on example.com domain
 - https://slam.example.com/domains/example.com/host: to act on host.example.com entry

urlpatterns do not respect pylint name style, so we disable C0103 (invalid-name) check on this file
"""
# pylint: disable=C0103
from django.urls import path, re_path
from . import views

urlpatterns = [
    path('', views.domains_view, name='domains'),
    re_path(r'(?P<uri_domain>[\w\.\-]+)/(?P<uri_entry>[\w\-]+)$', views.entry_view, name='entry'),
    re_path(r'(?P<uri_domain>[\w\.\-]+)$', views.domain_view, name='domain'),
]

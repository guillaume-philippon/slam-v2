from django.urls import path,re_path

from . import views

urlpatterns = [
    path('', views.domains, name='domains'),
    re_path(r'(?P<name>[\w\.\-]+)/(?P<ns_entry>[\w\-]+)$', views.dns_entry, name='dns_entry'),
    re_path(r'(?P<name>[\w\.\-]+)$', views.domain, name='domain'),
]

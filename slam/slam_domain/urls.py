from django.urls import path, re_path
from . import views

urlpatterns = [
    path('', views.domains_view, name='domains'),
    re_path(r'(?P<uri_domain>[\w\.\-]+)/(?P<uri_entry>[\w\-]+)$', views.entry_view, name='entry'),
    re_path(r'(?P<uri_domain>[\w\.\-]+)$', views.domain_view, name='domain'),
]
